import csv
import json
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event, insert, inspect, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, load_only, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import Settings
from .models import (
    Base,
    ElectionRow,
    ModelVersionRow,
    ParticipationRow,
    PredictionRow,
    SourceRow,
    TerritoryRow,
)


class StoreUnavailable(RuntimeError):
    pass


class DataStore:
    """Database-backed access to the versioned G1 artifacts."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.root = settings.project_root
        self.source_version = "unknown"
        self.warnings: list[str] = []
        self.metadata: dict[str, object] | None = None
        self._ready = False
        self._error = "not_initialized"
        self._load_metadata()

        self.engine = None
        self.sessions = None
        self.is_postgres = False
        try:
            engine_options: dict[str, object] = {"future": True}
            database_url = settings.resolved_database_url
            self.is_postgres = database_url.startswith("postgresql")
            if database_url.startswith("sqlite"):
                engine_options["connect_args"] = {"check_same_thread": False}
                if database_url in {"sqlite://", "sqlite:///:memory:"}:
                    engine_options["poolclass"] = StaticPool
            elif self.is_postgres:
                engine_options["connect_args"] = {"connect_timeout": settings.database_connect_timeout}
            self.engine = create_engine(database_url, **engine_options)
            if database_url.startswith("sqlite"):
                event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
            self.sessions = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
            self.initialize()
        except (OSError, ValueError, SQLAlchemyError) as exc:
            self._ready = False
            self._error = type(exc).__name__

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def error_kind(self) -> str:
        return self._error

    def _load_metadata(self) -> None:
        try:
            metadata = self._read_json(self.root / "data/processed/metadata.json")
            if not isinstance(metadata, dict):
                raise ValueError("metadata.json no es un objeto")
            self.metadata = metadata
            self.source_version = str(metadata["source_version"])
            self.warnings = [str(value) for value in metadata.get("warnings", [])]
        except (OSError, KeyError, TypeError, ValueError):
            self._error = "metadata_unavailable"

    @staticmethod
    def _read_json(path: Path) -> object:
        return json.loads(path.read_text(encoding="utf-8"))

    def initialize(self) -> None:
        try:
            if self.engine is None or self.sessions is None:
                raise RuntimeError("La conexion no esta inicializada")
            if self.is_postgres:
                self._require_postgres_schema()
            else:
                Base.metadata.create_all(self.engine)
            self.seed_from_artifacts()
            self._ready = True
            self._error = ""
        except (OSError, ValueError, RuntimeError, SQLAlchemyError, KeyError, TypeError) as exc:
            self._ready = False
            self._error = type(exc).__name__

    def _require_postgres_schema(self) -> None:
        if self.engine is None:
            raise RuntimeError("La conexion no esta inicializada")
        required = {
            "schema_migrations",
            "sources",
            "territories",
            "elections",
            "participation",
            "model_versions",
            "predictions",
        }
        tables = set(inspect(self.engine).get_table_names())
        missing = required - tables
        if missing:
            raise RuntimeError("Faltan migraciones de API")

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def check_connection(self) -> bool:
        if not self.ready or self.sessions is None:
            return False
        try:
            with self.sessions() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as exc:
            self._ready = False
            self._error = type(exc).__name__
            return False

    def seed_from_artifacts(self) -> None:
        if self.metadata is None:
            raise ValueError("Falta metadata de G1")
        sources = self._read_json(self.root / "data/sources.lock.json")
        territories = self._read_json(self.root / "data/processed/territories.json")
        elections = self._read_json(self.root / "data/processed/elections.json")
        report = self._read_json(self.root / "ml/artifacts/evaluation.json")
        predictions = self._read_json(self.root / "ml/artifacts/predictions_2024.json")

        if not isinstance(sources, list) or not isinstance(territories, list) or not isinstance(elections, list):
            raise ValueError("Los catalogos G1 no tienen formato de lista")
        if not isinstance(report, dict) or not isinstance(predictions, list):
            raise ValueError("Los artefactos del modelo G1 no tienen formato valido")
        if str(self.metadata["source_version"]) != str(report["source_version"]):
            raise ValueError("La version de datos y modelo no coincide")
        territory_ids = {str(item["id"]) for item in territories}
        prediction_ids = {str(item["territory_id"]) for item in predictions}
        if len(predictions) != len(territory_ids) or prediction_ids != territory_ids:
            raise ValueError("La cobertura de predicciones no coincide con territorios")
        model_version = str(report["model_version"])
        if any(str(item["model_version"]) != model_version for item in predictions):
            raise ValueError("Las predicciones mezclan versiones de modelo")

        if self.sessions is None:
            raise RuntimeError("La conexion no esta inicializada")
        with self.sessions() as session:
            for source in sources:
                session.merge(
                    SourceRow(
                        id=str(source["id"]),
                        url=str(source["url"]),
                        title=str(source["title"]),
                        retrieved_at=self._parse_datetime(str(source["retrieved_at"])),
                    )
                )

            for territory in territories:
                territory_id = str(territory["id"])
                existing = session.get(
                    TerritoryRow,
                    territory_id,
                    options=[
                        load_only(
                            TerritoryRow.id,
                            TerritoryRow.name,
                            TerritoryRow.level,
                            TerritoryRow.state_id,
                            TerritoryRow.code_system,
                        )
                    ],
                )
                if existing is None:
                    session.execute(
                        insert(TerritoryRow).values(
                            id=territory_id,
                            name=str(territory["name"]),
                            level=str(territory["level"]),
                            state_id=str(territory["state_id"]),
                            code_system=str(territory["code_system"]),
                        )
                    )
                else:
                    existing.name = str(territory["name"])
                    existing.level = str(territory["level"])
                    existing.state_id = str(territory["state_id"])
                    existing.code_system = str(territory["code_system"])

            for election in elections:
                session.merge(
                    ElectionRow(
                        election_id=str(election["election_id"]),
                        year=int(election["year"]),
                        election_date=date.fromisoformat(str(election["election_date"])),
                        election_type=str(election["election_type"]),
                    )
                )
            session.flush()

            with (self.root / "data/processed/participation.csv").open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    session.merge(
                        ParticipationRow(
                            territory_id=str(row["territory_id"]),
                            election_id=str(row["election_id"]),
                            nominal_count=int(row["nominal_count"]),
                            voted_count=int(row["voted_count"]),
                            not_voted_count=int(row["not_voted_count"]),
                            unknown_count=int(row["unknown_count"]),
                            known_count=int(row["known_count"]),
                            participation_pct=float(row["participation_pct"]),
                            abstention_pct=float(row["abstention_pct"]),
                            unknown_pct=float(row["unknown_pct"]),
                            participation_lower_pct=float(row["participation_lower_pct"]),
                            participation_upper_pct=float(row["participation_upper_pct"]),
                            source_id=str(row["source_id"]),
                            data_status=str(row["data_status"]),
                            denominator=str(row["denominator"]),
                        )
                    )
            session.flush()

            served = report["served"]
            model_warnings = [str(value) for value in report.get("warnings", [])]
            session.merge(
                ModelVersionRow(
                    model_version=model_version,
                    source_version=str(report["source_version"]),
                    strategy=str(report["selected_strategy"]),
                    evaluation_mode="retrospective_holdout",
                    mae_pp=float(served["mae_pp"]),
                    baseline_mae_pp=float(report["baseline"]["mae_pp"]),
                    n_test=int(report["n_test"]),
                    interval_json=report.get("interval"),
                    warnings_json=model_warnings,
                )
            )
            session.flush()
            for prediction in predictions:
                session.merge(
                    PredictionRow(
                        territory_id=str(prediction["territory_id"]),
                        election_id=str(prediction["election_id"]),
                        model_version=str(prediction["model_version"]),
                        abstention_pct=float(prediction["abstention_pct"]),
                        participation_pct=float(prediction["participation_pct"]),
                        mae_pp=float(prediction["mae_pp"]),
                        baseline_mae_pp=float(prediction["baseline_mae_pp"]),
                        n_test=int(prediction["n_test"]),
                        interval_json=prediction.get("interval"),
                        warnings_json=[str(value) for value in prediction.get("warnings", [])],
                        strategy=str(prediction["strategy"]),
                        evaluation_mode=str(prediction["evaluation_mode"]),
                    )
                )
            session.commit()

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    @contextmanager
    def session(self) -> Iterator[Session]:
        if not self.ready or self.sessions is None:
            raise StoreUnavailable(self.error_kind)
        session = self.sessions()
        try:
            yield session
        except SQLAlchemyError as exc:
            session.rollback()
            self._ready = False
            self._error = type(exc).__name__
            raise StoreUnavailable("database_unavailable") from exc
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_territory(self, territory_id: str) -> dict[str, str] | None:
        with self.session() as session:
            row = session.get(
                TerritoryRow,
                territory_id,
                options=[
                    load_only(
                        TerritoryRow.id,
                        TerritoryRow.name,
                        TerritoryRow.level,
                        TerritoryRow.state_id,
                        TerritoryRow.code_system,
                    )
                ],
            )
            if row is None:
                return None
            return self._territory_dict(row)

    def list_territories(self, state_id: str | None = None) -> list[dict[str, str]]:
        with self.session() as session:
            statement = select(TerritoryRow).options(
                load_only(
                    TerritoryRow.id,
                    TerritoryRow.name,
                    TerritoryRow.level,
                    TerritoryRow.state_id,
                    TerritoryRow.code_system,
                )
            ).order_by(TerritoryRow.id)
            if state_id is not None:
                statement = statement.where(TerritoryRow.state_id == state_id)
            return [self._territory_dict(row) for row in session.scalars(statement)]

    def list_elections(self) -> list[dict[str, object]]:
        with self.session() as session:
            rows = session.scalars(select(ElectionRow).order_by(ElectionRow.year))
            return [self._election_dict(row) for row in rows]

    def get_election(self, election_id: str) -> dict[str, object] | None:
        with self.session() as session:
            row = session.get(ElectionRow, election_id)
            return self._election_dict(row) if row is not None else None

    def list_participation(self, territory_id: str, election_id: str | None = None) -> list[dict[str, object]]:
        with self.session() as session:
            statement = select(ParticipationRow, ElectionRow).join(
                ElectionRow, ParticipationRow.election_id == ElectionRow.election_id
            ).where(ParticipationRow.territory_id == territory_id)
            if election_id is not None:
                statement = statement.where(ParticipationRow.election_id == election_id)
            statement = statement.order_by(ElectionRow.year)
            return [self._observation_dict(participation, election) for participation, election in session.execute(statement)]

    def get_prediction(self, territory_id: str, election_id: str) -> dict[str, object] | None:
        with self.session() as session:
            row = session.get(PredictionRow, (territory_id, election_id))
            if row is None:
                return None
            return {
                "territory_id": row.territory_id,
                "election_id": row.election_id,
                "abstention_pct": row.abstention_pct,
                "participation_pct": row.participation_pct,
                "model_version": row.model_version,
                "mae_pp": row.mae_pp,
                "baseline_mae_pp": row.baseline_mae_pp,
                "n_test": row.n_test,
                "interval": self._load_json(row.interval_json),
                "warnings": self._load_json(row.warnings_json) or [],
                "strategy": row.strategy,
                "evaluation_mode": row.evaluation_mode,
            }

    def get_geometry(self, territory_id: str) -> str | None:
        with self.session() as session:
            if self.is_postgres:
                return session.execute(
                    text("SELECT ST_AsGeoJSON(geometry) FROM territories WHERE id = :territory_id"),
                    {"territory_id": territory_id},
                ).scalar_one_or_none()
            row = session.get(TerritoryRow, territory_id)
            return row.geometry_json if row is not None else None

    def all_source_ids(self) -> list[str]:
        with self.session() as session:
            return list(session.scalars(select(SourceRow.id).order_by(SourceRow.id)))

    def source_records(self, source_ids: list[str]) -> list[dict[str, object]]:
        if not source_ids:
            return []
        with self.session() as session:
            rows = session.scalars(select(SourceRow).where(SourceRow.id.in_(source_ids))).all()
            by_id = {row.id: row for row in rows}
            return [self._source_dict(by_id[source_id]) for source_id in source_ids if source_id in by_id]

    @staticmethod
    def _load_json(value: object | None) -> object:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        return json.loads(value)

    @staticmethod
    def _territory_dict(row: TerritoryRow) -> dict[str, str]:
        return {
            "id": row.id,
            "name": row.name,
            "level": row.level,
            "state_id": row.state_id,
            "code_system": row.code_system,
        }

    @staticmethod
    def _election_dict(row: ElectionRow) -> dict[str, object]:
        return {
            "election_id": row.election_id,
            "year": row.year,
            "election_date": row.election_date,
            "election_type": row.election_type,
        }

    @staticmethod
    def _observation_dict(row: ParticipationRow, election: ElectionRow) -> dict[str, object]:
        return {
            "election_id": row.election_id,
            "year": election.year,
            "participation_pct": row.participation_pct,
            "abstention_pct": row.abstention_pct,
            "source_id": row.source_id,
            "territory_id": row.territory_id,
            "nominal_count": row.nominal_count,
            "voted_count": row.voted_count,
            "not_voted_count": row.not_voted_count,
            "unknown_count": row.unknown_count,
            "known_count": row.known_count,
            "unknown_pct": row.unknown_pct,
            "participation_lower_pct": row.participation_lower_pct,
            "participation_upper_pct": row.participation_upper_pct,
            "denominator": row.denominator,
            "election_date": election.election_date,
            "election_type": election.election_type,
        }

    @staticmethod
    def _source_dict(row: SourceRow) -> dict[str, object]:
        retrieved_at = row.retrieved_at
        if retrieved_at.tzinfo is None:
            retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)
        return {
            "id": row.id,
            "url": row.url,
            "title": row.title,
            "retrieved_at": retrieved_at,
        }

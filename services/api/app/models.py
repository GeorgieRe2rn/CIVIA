from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SourceRow(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TerritoryRow(Base):
    __tablename__ = "territories"

    id: Mapped[str] = mapped_column(String(5), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    state_id: Mapped[str] = mapped_column(String(2), nullable=False)
    code_system: Mapped[str] = mapped_column(String(64), nullable=False)
    # JSON is used by the portable test database; the PostGIS migration maps
    # this same field to a nullable geometry column.
    geometry_json: Mapped[str | None] = mapped_column("geometry", Text, nullable=True)


class ElectionRow(Base):
    __tablename__ = "elections"

    election_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    election_type: Mapped[str] = mapped_column(String(32), nullable=False)


class ParticipationRow(Base):
    __tablename__ = "participation"
    __table_args__ = (
        UniqueConstraint("territory_id", "election_id", name="uq_participation_territory_election"),
        CheckConstraint("nominal_count = voted_count + not_voted_count + unknown_count", name="ck_participation_counts"),
        CheckConstraint("participation_pct BETWEEN 0 AND 100", name="ck_participation_pct"),
        CheckConstraint("abstention_pct BETWEEN 0 AND 100", name="ck_abstention_pct"),
    )

    territory_id: Mapped[str] = mapped_column(ForeignKey("territories.id"), primary_key=True)
    election_id: Mapped[str] = mapped_column(ForeignKey("elections.election_id"), primary_key=True)
    nominal_count: Mapped[int] = mapped_column(Integer, nullable=False)
    voted_count: Mapped[int] = mapped_column(Integer, nullable=False)
    not_voted_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unknown_count: Mapped[int] = mapped_column(Integer, nullable=False)
    known_count: Mapped[int] = mapped_column(Integer, nullable=False)
    participation_pct: Mapped[float] = mapped_column(Float, nullable=False)
    abstention_pct: Mapped[float] = mapped_column(Float, nullable=False)
    unknown_pct: Mapped[float] = mapped_column(Float, nullable=False)
    participation_lower_pct: Mapped[float] = mapped_column(Float, nullable=False)
    participation_upper_pct: Mapped[float] = mapped_column(Float, nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), nullable=False)
    data_status: Mapped[str] = mapped_column(String(16), nullable=False)
    denominator: Mapped[str] = mapped_column(String(16), nullable=False)


class ModelVersionRow(Base):
    __tablename__ = "model_versions"

    model_version: Mapped[str] = mapped_column(String(160), primary_key=True)
    source_version: Mapped[str] = mapped_column(String(160), nullable=False)
    strategy: Mapped[str] = mapped_column(String(32), nullable=False)
    evaluation_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    mae_pp: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_mae_pp: Mapped[float] = mapped_column(Float, nullable=False)
    n_test: Mapped[int] = mapped_column(Integer, nullable=False)
    interval_json: Mapped[object | None] = mapped_column(JSON, nullable=True)
    warnings_json: Mapped[object] = mapped_column(JSON, nullable=False)


class PredictionRow(Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("territory_id", "election_id", name="uq_prediction_territory_election"),
        CheckConstraint("abstention_pct BETWEEN 0 AND 100", name="ck_prediction_abstention_pct"),
        CheckConstraint("participation_pct BETWEEN 0 AND 100", name="ck_prediction_participation_pct"),
    )

    territory_id: Mapped[str] = mapped_column(ForeignKey("territories.id"), primary_key=True)
    election_id: Mapped[str] = mapped_column(ForeignKey("elections.election_id"), primary_key=True)
    model_version: Mapped[str] = mapped_column(ForeignKey("model_versions.model_version"), nullable=False)
    abstention_pct: Mapped[float] = mapped_column(Float, nullable=False)
    participation_pct: Mapped[float] = mapped_column(Float, nullable=False)
    mae_pp: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_mae_pp: Mapped[float] = mapped_column(Float, nullable=False)
    n_test: Mapped[int] = mapped_column(Integer, nullable=False)
    interval_json: Mapped[object | None] = mapped_column(JSON, nullable=True)
    warnings_json: Mapped[object] = mapped_column(JSON, nullable=False)
    strategy: Mapped[str] = mapped_column(String(32), nullable=False)
    evaluation_mode: Mapped[str] = mapped_column(String(64), nullable=False)

from sqlalchemy import create_engine, text

from .config import Settings


def apply_migrations(settings: Settings) -> list[str]:
    database_url = settings.resolved_database_url
    if not database_url.startswith("postgresql"):
        raise RuntimeError("Las migraciones PostGIS requieren DATABASE_URL postgresql")

    migration_dir = settings.project_root / "services/api/migrations"
    paths = sorted(migration_dir.glob("*.sql"))
    if not paths:
        raise RuntimeError("No hay archivos de migracion")

    engine = create_engine(database_url, future=True)
    applied_now: list[str] = []
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
        )
        applied = set(connection.execute(text("SELECT version FROM schema_migrations")).scalars())
        for path in paths:
            version = path.name
            if version in applied:
                continue
            script = path.read_text(encoding="utf-8")
            for statement in _statements(script):
                connection.exec_driver_sql(statement)
            connection.execute(text("INSERT INTO schema_migrations(version) VALUES (:version)"), {"version": version})
            applied_now.append(version)
    engine.dispose()
    return applied_now


def _statements(script: str) -> list[str]:
    return [statement.strip() for statement in script.split(";") if statement.strip()]

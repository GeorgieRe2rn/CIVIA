import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from app.config import Settings
from app.main import create_app


EXPECTED_COUNTS = {
    "sources": 6,
    "territories": 125,
    "elections": 6,
    "participation": 750,
    "model_versions": 1,
    "predictions": 125,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    settings = Settings()
    database_url = settings.resolved_database_url
    require(database_url.startswith("postgresql+psycopg://"), "La validacion PostGIS requiere DATABASE_URL PostgreSQL")

    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            postgis_version = str(connection.execute(text("SELECT PostGIS_Full_Version()")).scalar_one())
            counts = {
                table: int(connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())
                for table in EXPECTED_COUNTS
            }
            geometry_count = int(connection.execute(text("SELECT COUNT(*) FROM territories WHERE geometry IS NOT NULL")).scalar_one())
            duplicate_participation = int(
                connection.execute(
                    text(
                        "SELECT COUNT(*) FROM ("
                        "SELECT territory_id, election_id FROM participation "
                        "GROUP BY territory_id, election_id HAVING COUNT(*) > 1"
                        ") duplicates"
                    )
                ).scalar_one()
            )
            duplicate_predictions = int(
                connection.execute(
                    text(
                        "SELECT COUNT(*) FROM ("
                        "SELECT territory_id, election_id FROM predictions "
                        "GROUP BY territory_id, election_id HAVING COUNT(*) > 1"
                        ") duplicates"
                    )
                ).scalar_one()
            )
    finally:
        engine.dispose()

    require(counts == EXPECTED_COUNTS, f"Conteos inesperados: {counts}")
    require(duplicate_participation == 0, "La tabla participation contiene duplicados")
    require(duplicate_predictions == 0, "La tabla predictions contiene duplicados")

    app = create_app(settings)
    with TestClient(app) as client:
        health = client.get("/api/health")
        territories = client.get("/api/territorios")
        elections = client.get("/api/elecciones")
        participation = client.get("/api/participacion", params={"territorio": "14001"})
        prediction = client.post(
            "/api/predicciones",
            json={"territory_id": "14001", "election_id": "federal-2024"},
        )
        scenario = client.post(
            "/api/escenarios",
            json={"territory_id": "14001", "election_id": "federal-2024", "delta_pp": 5},
        )
        assistant = client.post(
            "/api/asistente",
            json={"territory_id": "14001", "question": "¿Qué significa la participación?"},
        )
        map_response = client.get("/api/mapa", params={"territorio": "14001"})
        openapi = client.get("/openapi.json")

    require(health.status_code == 200 and health.json()["data"]["status"] == "ok", "health no esta listo")
    require(territories.status_code == 200 and len(territories.json()["data"]) == 125, "territorios no coincide")
    require(elections.status_code == 200 and len(elections.json()["data"]) == 6, "elecciones no coincide")
    require(participation.status_code == 200 and len(participation.json()["data"]) == 6, "participacion no coincide")
    require(prediction.status_code == 200, "predicciones no responde 200")
    require(scenario.status_code == 200, "escenarios no responde 200")
    require(assistant.status_code == 200, "asistente no responde 200")
    if geometry_count == 0:
        require(map_response.status_code == 503, "mapa debe conservar 503 sin geometria")
        require(map_response.json()["error"]["code"] == "DATA_UNAVAILABLE", "mapa no reporta DATA_UNAVAILABLE")
    else:
        require(map_response.status_code == 200, "mapa no responde 200 con geometria")
    require(openapi.status_code == 200 and openapi.json()["info"]["version"] == "1.1.0", "OpenAPI no coincide")

    print(f"PostGIS: {postgis_version}")
    print(f"Conteos: {counts}")
    print(f"Geometrias no nulas: {geometry_count}")
    print("API PostgreSQL: health, catalogos, historial, prediccion, escenario, asistente y OpenAPI OK")
    print(f"API mapa: {map_response.status_code} ({'geometria verificada' if geometry_count else 'DATA_UNAVAILABLE'})")


if __name__ == "__main__":
    main()

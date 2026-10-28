import json
from pathlib import Path

from fastapi.testclient import TestClient
from openapi_schema_validator import OAS30Validator
from sqlalchemy import func, select

from app.config import Settings
from app.main import create_app
from app.models import ParticipationRow, PredictionRow, TerritoryRow
from app.store import DataStore


ROOT = Path(__file__).resolve().parents[1]


def expand_schema(contract, value):
    if isinstance(value, dict):
        if "$ref" in value:
            return expand_schema(contract, contract["components"]["schemas"][value["$ref"].split("/")[-1]])
        return {key: expand_schema(contract, item) for key, item in value.items()}
    if isinstance(value, list):
        return [expand_schema(contract, item) for item in value]
    return value


def make_client(**overrides) -> TestClient:
    values = {
        "project_root": ROOT,
        "database_url": "sqlite://",
        "cors_origins": "http://localhost:5173",
        "rate_limit": 0,
    }
    values.update(overrides)
    return TestClient(create_app(Settings(**values)))


def test_health_reports_real_source_and_ai_off():
    with make_client() as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["ai_enabled"] is False
    assert body["meta"]["source_version"] == "ine-ccpc-jal-b76f8fc46187"


def test_catalogs_and_observed_history_are_loaded_from_g1():
    with make_client() as client:
        territories = client.get("/api/territorios")
        elections = client.get("/api/elecciones")
        history = client.get("/api/participacion", params={"territorio": "14041"})

    assert territories.status_code == 200
    assert len(territories.json()["data"]) == 125
    assert elections.status_code == 200
    assert [item["year"] for item in elections.json()["data"]] == [2009, 2012, 2015, 2018, 2021, 2024]
    assert history.status_code == 200
    assert len(history.json()["data"]) == 6
    assert history.json()["meta"]["data_status"] == "observado"
    assert history.json()["data"][-1]["territory_id"] == "14041"


def test_prediction_and_scenario_use_server_artifact():
    with make_client() as client:
        prediction = client.post(
            "/api/predicciones",
            json={"territory_id": "14041", "election_id": "federal-2024"},
        )
        scenario = client.post(
            "/api/escenarios",
            json={"territory_id": "14041", "election_id": "federal-2024", "delta_pp": 0},
        )
        lower_scenario = client.post(
            "/api/escenarios",
            json={"territory_id": "14041", "election_id": "federal-2024", "delta_pp": -20},
        )
        invalid_scenario = client.post(
            "/api/escenarios",
            json={"territory_id": "14041", "election_id": "federal-2024", "delta_pp": 21},
        )

    assert prediction.status_code == 200
    prediction_data = prediction.json()["data"]
    assert prediction_data["interval"] is None
    assert prediction_data["n_test"] == 125
    assert len(prediction.json()["sources"]) == 6
    assert scenario.status_code == 200
    scenario_data = scenario.json()["data"]
    assert scenario_data["final_participation_pct"] == scenario_data["base_participation_pct"]
    assert scenario_data["clamped"] is False
    assert scenario_data["label"] == "Simulación hipotética"
    assert lower_scenario.status_code == 200
    lower_data = lower_scenario.json()["data"]
    assert 0 <= lower_data["final_participation_pct"] <= 100
    assert lower_data["final_abstention_pct"] == 100 - lower_data["final_participation_pct"]
    assert invalid_scenario.status_code == 422


def test_ingestion_preserves_optional_geometry():
    settings = Settings(
        project_root=ROOT,
        database_url="sqlite://",
        cors_origins="http://localhost:5173",
        rate_limit=0,
    )
    store = DataStore(settings)
    with store.session() as session:
        territory = session.get(TerritoryRow, "14041")
        territory.geometry_json = '{"type":"Polygon","coordinates":[]}'
        session.commit()
    store.seed_from_artifacts()
    assert store.get_geometry("14041") == '{"type":"Polygon","coordinates":[]}'


def test_postgresql_url_uses_psycopg_driver():
    settings = Settings(database_url="postgresql://localhost/civia")
    assert settings.resolved_database_url.startswith("postgresql+psycopg://")


def test_body_limit_is_structured():
    with make_client(max_body_bytes=1024) as client:
        response = client.post(
            "/api/asistente",
            json={"territory_id": "14041", "question": "x" * 1000},
        )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_valid_empty_catalog_filter_returns_200_empty_data():
    with make_client() as client:
        response = client.get("/api/territorios", params={"estado": "15"})

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_missing_map_is_structured_503_and_assistant_is_deterministic():
    with make_client() as client:
        map_response = client.get("/api/mapa", params={"territorio": "14041"})
        assistant = client.post(
            "/api/asistente",
            json={"territory_id": "14041", "question": "Que representa la tasa?"},
        )

    assert map_response.status_code == 503
    assert map_response.json()["error"]["code"] == "DATA_UNAVAILABLE"
    assert assistant.status_code == 200
    assert assistant.json()["data"]["mode"] == "determinista"
    assert assistant.json()["data"]["source_ids"]


def test_invalid_inputs_and_unknown_territory_use_contract_errors():
    with make_client() as client:
        missing = client.get("/api/participacion")
        unknown = client.get("/api/participacion", params={"territorio": "14999"})
        future = client.post(
            "/api/predicciones",
            json={"territory_id": "14041", "election_id": "federal-2030"},
        )

    assert missing.status_code == 422
    assert missing.json()["error"]["code"] == "VALIDATION_ERROR"
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "TERRITORY_NOT_FOUND"
    assert future.status_code == 422
    assert future.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cors_is_explicit_and_rate_limit_is_structured():
    with make_client(rate_limit=1) as client:
        first = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
        second = client.get("/api/health", headers={"Origin": "http://localhost:5173"})

    assert first.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "RATE_LIMITED"


def test_ingestion_is_idempotent_and_openapi_is_frozen():
    settings = Settings(
        project_root=ROOT,
        database_url="sqlite://",
        cors_origins="http://localhost:5173",
        rate_limit=0,
    )
    store = DataStore(settings)
    store.seed_from_artifacts()
    with store.session() as session:
        territory_count = session.scalar(select(func.count()).select_from(TerritoryRow))
        participation_count = session.scalar(select(func.count()).select_from(ParticipationRow))
        prediction_count = session.scalar(select(func.count()).select_from(PredictionRow))
    assert (territory_count, participation_count, prediction_count) == (125, 750, 125)

    with make_client() as client:
        published = client.get("/openapi.json")
    assert published.status_code == 200
    assert published.json()["info"]["version"] == "1.1.0"
    assert set(published.json()["paths"]) == {
        "/api/health",
        "/api/territorios",
        "/api/participacion",
        "/api/predicciones",
        "/api/escenarios",
        "/api/mapa",
        "/api/asistente",
        "/api/elecciones",
    }


def test_real_api_responses_match_frozen_openapi_schemas():
    contract = json.loads((ROOT / "contracts/openapi.yaml").read_text(encoding="utf-8"))
    with make_client() as client:
        responses = [
            ("/api/health", "get", 200, client.get("/api/health")),
            ("/api/territorios", "get", 200, client.get("/api/territorios")),
            ("/api/elecciones", "get", 200, client.get("/api/elecciones")),
            (
                "/api/participacion",
                "get",
                200,
                client.get("/api/participacion", params={"territorio": "14041"}),
            ),
            (
                "/api/predicciones",
                "post",
                200,
                client.post("/api/predicciones", json={"territory_id": "14041", "election_id": "federal-2024"}),
            ),
            (
                "/api/escenarios",
                "post",
                200,
                client.post(
                    "/api/escenarios",
                    json={"territory_id": "14041", "election_id": "federal-2024", "delta_pp": 3},
                ),
            ),
            (
                "/api/mapa",
                "get",
                503,
                client.get("/api/mapa", params={"territorio": "14041"}),
            ),
            (
                "/api/asistente",
                "post",
                200,
                client.post(
                    "/api/asistente",
                    json={"territory_id": "14041", "question": "Que representa la tasa?"},
                ),
            ),
        ]

    for path, method, status, response in responses:
        assert response.status_code == status
        response_schema = contract["paths"][path][method]["responses"][str(status)]["content"]["application/json"]["schema"]
        OAS30Validator(expand_schema(contract, response_schema)).validate(response.json())

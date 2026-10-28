import json
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import Body, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import Settings, get_settings
from .errors import ApiError, error_response
from .schemas import (
    AssistantRequest,
    AssistantResponse,
    Election,
    Feature,
    FeatureCollection,
    Meta,
    Observation,
    Prediction,
    PredictionRequest,
    Scenario,
    ScenarioRequest,
    Source,
    Territory,
)
from .store import DataStore, StoreUnavailable


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.events: defaultdict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        if self.limit <= 0:
            return True
        now = time.monotonic()
        events = self.events[key]
        cutoff = now - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True


class RequestTooLarge(Exception):
    pass


def _store(request: Request) -> DataStore:
    return request.app.state.store


def _ready_store(request: Request) -> DataStore:
    store = _store(request)
    if not store.ready:
        raise ApiError(503, "DATA_UNAVAILABLE", "Los datos de CIVIA no estan disponibles")
    return store


def _model_data(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _envelope(store: DataStore, data: Any, status: str, source_ids: list[str] | None = None, warnings: list[str] | None = None) -> dict[str, Any]:
    meta = Meta(
        source_version=store.source_version,
        timestamp=datetime.now(timezone.utc),
        data_status=status,
        warnings=list(store.warnings if warnings is None else warnings),
    )
    sources = [Source.model_validate(source).model_dump(mode="json") for source in store.source_records(source_ids or [])]
    return {"meta": meta.model_dump(mode="json"), "data": _model_data(data), "sources": sources}


def _territory_or_404(store: DataStore, territory_id: str) -> dict[str, str]:
    territory = store.get_territory(territory_id)
    if territory is None:
        raise ApiError(404, "TERRITORY_NOT_FOUND", "No existe el territorio solicitado")
    return territory


def _election_or_422(store: DataStore, election_id: str) -> None:
    if store.get_election(election_id) is None:
        raise ApiError(422, "INVALID_ELECTION", "La eleccion no existe en el catalogo")


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime = settings or get_settings()
    origins = runtime.cors_origin_list
    store = DataStore(runtime)

    app = FastAPI(title=runtime.app_name, version=runtime.app_version)
    app.state.settings = runtime
    app.state.store = store
    app.state.rate_limiter = RateLimiter(runtime.rate_limit, runtime.rate_window_seconds)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.middleware("http")
    async def request_limits(request: Request, call_next):
        request.state.request_id = str(uuid4())
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                oversized = int(content_length) > runtime.max_body_bytes
            except ValueError:
                oversized = True
            if oversized:
                return error_response(
                    request,
                    413,
                    "PAYLOAD_TOO_LARGE",
                    "El cuerpo de la solicitud excede el limite permitido",
                    store.source_version,
                    store.warnings,
                )

        original_receive = request._receive
        received_bytes = 0

        async def limited_receive():
            nonlocal received_bytes
            message = await original_receive()
            if message.get("type") == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > runtime.max_body_bytes:
                    raise RequestTooLarge
            return message

        request._receive = limited_receive
        if request.url.path.startswith("/api/"):
            client_host = request.client.host if request.client else "unknown"
            if not app.state.rate_limiter.allow(client_host):
                return error_response(
                    request,
                    429,
                    "RATE_LIMITED",
                    "Se excedio el limite temporal de solicitudes",
                    store.source_version,
                    store.warnings,
                )
        try:
            response = await call_next(request)
        except RequestTooLarge:
            return error_response(
                request,
                413,
                "PAYLOAD_TOO_LARGE",
                "El cuerpo de la solicitud excede el limite permitido",
                store.source_version,
                store.warnings,
            )
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        return error_response(request, exc.status_code, exc.code, exc.message, store.source_version, store.warnings)

    @app.exception_handler(StoreUnavailable)
    async def handle_store_error(request: Request, exc: StoreUnavailable):
        return error_response(
            request,
            503,
            "DATA_UNAVAILABLE",
            "Los datos de CIVIA no estan disponibles",
            store.source_version,
            store.warnings,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        return error_response(
            request,
            422,
            "VALIDATION_ERROR",
            "La solicitud no cumple el contrato de CIVIA",
            store.source_version,
            store.warnings,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            code, message = "NOT_FOUND", "El recurso solicitado no existe"
        elif exc.status_code == 405:
            code, message = "METHOD_NOT_ALLOWED", "El metodo HTTP no esta permitido"
        else:
            code, message = "HTTP_ERROR", "La solicitud no pudo procesarse"
        return error_response(request, exc.status_code, code, message, store.source_version, store.warnings)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        # Do not expose database URLs, stack traces, or provider credentials.
        return error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Ocurrio un error interno",
            store.source_version,
            store.warnings,
        )

    @app.get("/api/health")
    def health(request: Request):
        current_store = _store(request)
        ready = current_store.check_connection()
        return _envelope(
            current_store,
            {
                "status": "ok" if ready else "degraded",
                "version": runtime.app_version,
                "ai_enabled": runtime.generative_ai_available,
            },
            "no_aplica",
        )

    @app.get("/api/territorios")
    def territories(request: Request, estado: str | None = Query(default=None, max_length=2)):
        current_store = _ready_store(request)
        data = [Territory.model_validate(value) for value in current_store.list_territories(estado)]
        source_ids = ["ine-ccpc-2024-jal"] if data else []
        return _envelope(current_store, data, "no_aplica", source_ids)

    @app.get("/api/elecciones")
    def elections(request: Request):
        current_store = _ready_store(request)
        data = [Election.model_validate(value) for value in current_store.list_elections()]
        source_ids = [f"ine-ccpc-{election.year}-jal" for election in data]
        return _envelope(current_store, data, "no_aplica", source_ids)

    @app.get("/api/participacion")
    def participation(
        request: Request,
        territorio: str = Query(..., pattern=r"^14[0-9]{3}$"),
        eleccion: str | None = Query(default=None, max_length=40),
    ):
        current_store = _ready_store(request)
        _territory_or_404(current_store, territorio)
        if eleccion is not None:
            _election_or_422(current_store, eleccion)
        data = [Observation.model_validate(value) for value in current_store.list_participation(territorio, eleccion)]
        source_ids = list(dict.fromkeys(value.source_id for value in data))
        return _envelope(current_store, data, "observado", source_ids)

    @app.post("/api/predicciones")
    def predictions(request: Request, payload: PredictionRequest = Body(...)):
        current_store = _ready_store(request)
        _territory_or_404(current_store, payload.territory_id)
        prediction = current_store.get_prediction(payload.territory_id, payload.election_id)
        if prediction is None:
            raise ApiError(503, "MODEL_UNAVAILABLE", "No hay un modelo valido para el territorio solicitado")
        data = Prediction.model_validate(prediction)
        return _envelope(current_store, data, "predicho", current_store.all_source_ids())

    @app.post("/api/escenarios")
    def scenarios(request: Request, payload: ScenarioRequest = Body(...)):
        current_store = _ready_store(request)
        _territory_or_404(current_store, payload.territory_id)
        prediction = current_store.get_prediction(payload.territory_id, payload.election_id)
        if prediction is None:
            raise ApiError(503, "MODEL_UNAVAILABLE", "No hay un modelo valido para el territorio solicitado")
        base = 100.0 - float(prediction["abstention_pct"])
        if abs(base - float(prediction["participation_pct"])) > 1e-9:
            raise ApiError(503, "MODEL_UNAVAILABLE", "La prediccion no conserva participacion y abstencion complementarias")
        requested_final = base + payload.delta_pp
        final = min(100.0, max(0.0, requested_final))
        data = Scenario(
            base_participation_pct=base,
            final_participation_pct=final,
            final_abstention_pct=100.0 - final,
            delta_pp=payload.delta_pp,
            clamped=final != requested_final,
            label="Simulación hipotética",
            territory_id=payload.territory_id,
            election_id=payload.election_id,
            base_status="predicho",
            base_evaluation_mode="retrospective_holdout",
        )
        return _envelope(current_store, data, "simulado", current_store.all_source_ids())

    @app.get("/api/mapa")
    def map_data(request: Request, territorio: str = Query(..., pattern=r"^14[0-9]{3}$")):
        current_store = _ready_store(request)
        territory = _territory_or_404(current_store, territorio)
        geometry_json = current_store.get_geometry(territorio)
        if geometry_json is None:
            raise ApiError(503, "DATA_UNAVAILABLE", "No hay geometria verificada para este territorio")
        try:
            geometry = json.loads(geometry_json)
        except (TypeError, ValueError):
            raise ApiError(503, "DATA_UNAVAILABLE", "La geometria disponible no es valida") from None
        if not isinstance(geometry, dict):
            raise ApiError(503, "DATA_UNAVAILABLE", "La geometria disponible no es valida")
        data = FeatureCollection(
            type="FeatureCollection",
            features=[
                Feature(
                    type="Feature",
                    geometry=geometry,
                    properties={"territory_id": territory["id"], "name": territory["name"]},
                )
            ],
        )
        return _envelope(current_store, data, "observado", ["ine-ccpc-2024-jal"])

    @app.post("/api/asistente")
    def assistant(request: Request, payload: AssistantRequest = Body(...)):
        current_store = _ready_store(request)
        territory = _territory_or_404(current_store, payload.territory_id)
        if not payload.question.strip():
            raise ApiError(422, "VALIDATION_ERROR", "La pregunta no puede estar vacia")
        observations = current_store.list_participation(payload.territory_id, "federal-2024")
        if not observations:
            data = AssistantResponse(answer="No hay informacion observada para este territorio.", mode="sin_informacion", source_ids=[])
            return _envelope(current_store, data, "no_aplica")

        observation = observations[0]
        prediction = current_store.get_prediction(payload.territory_id, "federal-2024")
        answer = (
            f"{territory['name']} registro una participacion observada de "
            f"{float(observation['participation_pct']):.2f}% en 2024. "
            "La tasa usa SV/(SV+NV); NS se informa por separado."
        )
        source_ids = [str(observation["source_id"])]
        if prediction is not None:
            answer += (
                f" El artefacto de backtest reporta una participacion predicha de "
                f"{float(prediction['participation_pct']):.2f}%; no es un pronostico futuro."
            )
        data = AssistantResponse(answer=answer, mode="determinista", source_ids=source_ids)
        return _envelope(current_store, data, "no_aplica", source_ids)

    # Keep route declarations discoverable for tooling that inspects the app.
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/"):
            route.tags = ["api"]

    def frozen_openapi():
        if app.openapi_schema is not None:
            return app.openapi_schema
        contract_path = runtime.project_root / "contracts/openapi.yaml"
        try:
            schema = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            schema = get_openapi(title=runtime.app_name, version=runtime.app_version, routes=app.routes)
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = frozen_openapi
    return app


app = create_app()

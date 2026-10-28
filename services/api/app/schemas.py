from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Meta(StrictModel):
    source_version: str
    timestamp: datetime
    data_status: Literal["observado", "predicho", "simulado", "no_aplica"]
    warnings: list[str] = Field(default_factory=list)


class Source(StrictModel):
    id: str
    url: str
    title: str
    retrieved_at: datetime


class Territory(StrictModel):
    id: str = Field(pattern=r"^14[0-9]{3}$")
    name: str
    level: Literal["municipio"]
    state_id: Literal["14"]
    code_system: Literal["INE_EDOCVE_MPIOCVE"]


class Election(StrictModel):
    election_id: str
    year: int
    election_date: date
    election_type: Literal["federal_concurrente", "federal_intermedia"]


class Observation(StrictModel):
    election_id: str
    year: int
    participation_pct: float = Field(ge=0, le=100)
    abstention_pct: float = Field(ge=0, le=100)
    source_id: str
    territory_id: str
    election_date: date
    election_type: Literal["federal_concurrente", "federal_intermedia"]
    nominal_count: int = Field(ge=0)
    voted_count: int = Field(ge=0)
    not_voted_count: int = Field(ge=0)
    unknown_count: int = Field(ge=0)
    known_count: int = Field(ge=0)
    unknown_pct: float = Field(ge=0, le=100)
    participation_lower_pct: float = Field(ge=0, le=100)
    participation_upper_pct: float = Field(ge=0, le=100)
    denominator: Literal["SV+NV"]


class PredictionRequest(StrictModel):
    territory_id: str = Field(pattern=r"^14[0-9]{3}$")
    election_id: Literal["federal-2024"]


class PredictionInterval(StrictModel):
    lower: float = Field(ge=0, le=100)
    upper: float = Field(ge=0, le=100)
    level: float = Field(ge=0, le=1)
    empirical_coverage: float = Field(ge=0, le=1)


class Prediction(StrictModel):
    abstention_pct: float = Field(ge=0, le=100)
    model_version: str
    mae_pp: float = Field(ge=0)
    baseline_mae_pp: float = Field(ge=0)
    n_test: int = Field(ge=1)
    interval: PredictionInterval | None
    warnings: list[str]
    territory_id: str
    election_id: Literal["federal-2024"]
    participation_pct: float = Field(ge=0, le=100)
    strategy: Literal["random_forest", "baseline_lag6"]
    evaluation_mode: Literal["retrospective_holdout"]


class ScenarioRequest(StrictModel):
    territory_id: str = Field(pattern=r"^14[0-9]{3}$")
    election_id: Literal["federal-2024"]
    delta_pp: float = Field(ge=-20, le=20)


class Scenario(StrictModel):
    base_participation_pct: float = Field(ge=0, le=100)
    final_participation_pct: float = Field(ge=0, le=100)
    final_abstention_pct: float = Field(ge=0, le=100)
    delta_pp: float
    clamped: bool
    label: Literal["Simulación hipotética"]
    territory_id: str
    election_id: Literal["federal-2024"]
    base_status: Literal["predicho"]
    base_evaluation_mode: Literal["retrospective_holdout"]


class AssistantRequest(StrictModel):
    question: str = Field(min_length=1, max_length=1000)
    territory_id: str


class AssistantResponse(StrictModel):
    answer: str
    mode: Literal["determinista", "generativa", "sin_informacion"]
    source_ids: list[str]


class Feature(StrictModel):
    type: Literal["Feature"]
    geometry: dict[str, Any] | None
    properties: dict[str, Any]


class FeatureCollection(StrictModel):
    type: Literal["FeatureCollection"]
    features: list[Feature]


class ErrorDetails(StrictModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorEnvelope(StrictModel):
    meta: Meta
    error: ErrorDetails

export type DataStatus = "observado" | "predicho" | "simulado" | "no_aplica";

export interface Meta {
  source_version: string;
  timestamp: string;
  data_status: DataStatus;
  warnings: string[];
}

export interface Source {
  id: string;
  url: string;
  title: string;
  retrieved_at: string;
}

export interface Envelope<T> {
  meta: Meta;
  data: T;
  sources: Source[];
}

export interface ApiErrorBody {
  meta?: Meta;
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
  };
}

export interface Territory {
  id: string;
  name: string;
  level: "municipio";
  state_id: "14";
  code_system: "INE_EDOCVE_MPIOCVE";
}

export interface Election {
  election_id: string;
  year: number;
  election_date: string;
  election_type: "federal_concurrente" | "federal_intermedia";
}

export interface Observation {
  election_id: string;
  year: number;
  participation_pct: number;
  abstention_pct: number;
  source_id: string;
  territory_id: string;
  election_date: string;
  election_type: "federal_concurrente" | "federal_intermedia";
  nominal_count: number;
  voted_count: number;
  not_voted_count: number;
  unknown_count: number;
  known_count: number;
  unknown_pct: number;
  participation_lower_pct: number;
  participation_upper_pct: number;
  denominator: "SV+NV";
}

export interface PredictionInterval {
  lower: number;
  upper: number;
  level: number;
  empirical_coverage: number;
}

export interface Prediction {
  abstention_pct: number;
  model_version: string;
  mae_pp: number;
  baseline_mae_pp: number;
  n_test: number;
  interval: PredictionInterval | null;
  warnings: string[];
  territory_id: string;
  election_id: "federal-2024";
  participation_pct: number;
  strategy: "random_forest" | "baseline_lag6";
  evaluation_mode: "retrospective_holdout";
}

export interface Scenario {
  base_participation_pct: number;
  final_participation_pct: number;
  final_abstention_pct: number;
  delta_pp: number;
  clamped: boolean;
  label: "Simulación hipotética";
  territory_id: string;
  election_id: "federal-2024";
  base_status: "predicho";
  base_evaluation_mode: "retrospective_holdout";
}

export interface GeoFeature {
  type: "Feature";
  geometry: Record<string, unknown> | null;
  properties: Record<string, unknown>;
}

export interface FeatureCollection {
  type: "FeatureCollection";
  features: GeoFeature[];
}

export interface Health {
  status: string;
  version: string;
  ai_enabled: boolean;
}

export interface AssistantResponse {
  answer: string;
  mode: "determinista" | "generativa" | "sin_informacion";
  source_ids: string[];
}

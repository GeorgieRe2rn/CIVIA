import { Platform } from "react-native";

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

export interface Prediction {
  abstention_pct: number;
  model_version: string;
  mae_pp: number;
  baseline_mae_pp: number;
  n_test: number;
  interval: { lower: number; upper: number; level: number; empirical_coverage: number } | null;
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

export interface FeatureCollection {
  type: "FeatureCollection";
  features: Array<{
    type: "Feature";
    geometry: Record<string, unknown> | null;
    properties: Record<string, unknown>;
  }>;
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

export interface ApiErrorBody {
  error?: { code?: string; message?: string };
}

const configuredBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
const fallbackBaseUrl = Platform.OS === "android" ? "http://10.0.2.2:8000" : "http://localhost:8000";
export const API_BASE_URL = (configuredBaseUrl || fallbackBaseUrl).replace(/\/+$/, "");

export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function request<T>(path: string, options: { method?: "GET" | "POST"; body?: object } = {}): Promise<Envelope<T>> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method || "GET",
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiRequestError(0, "NETWORK_ERROR", "No se pudo conectar con la API de CIVIA.");
  }

  const body = (await response.json().catch(() => ({}))) as Envelope<T> & ApiErrorBody;
  if (!response.ok) {
    throw new ApiRequestError(
      response.status,
      body.error?.code || "API_ERROR",
      body.error?.message || "La API no pudo completar la solicitud.",
    );
  }
  return body;
}

export const api = {
  getHealth: () => request<Health>("/api/health"),
  getTerritories: () => request<Territory[]>("/api/territorios"),
  getElections: () => request<Election[]>("/api/elecciones"),
  getParticipation: (territoryId: string) => request<Observation[]>(`/api/participacion?territorio=${encodeURIComponent(territoryId)}`),
  getPrediction: (territoryId: string) => request<Prediction>("/api/predicciones", { method: "POST", body: { territory_id: territoryId, election_id: "federal-2024" } }),
  getScenario: (territoryId: string, deltaPp: number) => request<Scenario>("/api/escenarios", { method: "POST", body: { territory_id: territoryId, election_id: "federal-2024", delta_pp: deltaPp } }),
  getMap: (territoryId: string) => request<FeatureCollection>(`/api/mapa?territorio=${encodeURIComponent(territoryId)}`),
  askAssistant: (territoryId: string, question: string) => request<AssistantResponse>("/api/asistente", { method: "POST", body: { territory_id: territoryId, question } }),
};

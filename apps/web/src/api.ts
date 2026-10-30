import type {
  AssistantResponse,
  Election,
  Envelope,
  FeatureCollection,
  Health,
  Observation,
  Prediction,
  Scenario,
  Territory,
} from "./types";
import type { ApiErrorBody } from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");

export class ApiRequestError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<Envelope<T>> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
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
  getParticipation: (territoryId: string) =>
    request<Observation[]>(`/api/participacion?territorio=${encodeURIComponent(territoryId)}`),
  getPrediction: (territoryId: string) =>
    request<Prediction>("/api/predicciones", {
      method: "POST",
      body: JSON.stringify({ territory_id: territoryId, election_id: "federal-2024" }),
    }),
  getScenario: (territoryId: string, deltaPp: number) =>
    request<Scenario>("/api/escenarios", {
      method: "POST",
      body: JSON.stringify({ territory_id: territoryId, election_id: "federal-2024", delta_pp: deltaPp }),
    }),
  getMap: (territoryId: string) =>
    request<FeatureCollection>(`/api/mapa?territorio=${encodeURIComponent(territoryId)}`),
  askAssistant: (territoryId: string, question: string) =>
    request<AssistantResponse>("/api/asistente", {
      method: "POST",
      body: JSON.stringify({ territory_id: territoryId, question }),
    }),
};

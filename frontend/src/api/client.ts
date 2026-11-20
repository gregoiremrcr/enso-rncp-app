import type {
  CompareResponse,
  Episode,
  ObservationResponse,
  SourceInfo,
} from "../types";

const API = "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API}${path}`, { signal });
  if (!response.ok) {
    let message = "Le service est momentanément indisponible.";
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "error" in body) {
        const error = body.error;
        if (
          typeof error === "object" &&
          error !== null &&
          "message" in error &&
          typeof error.message === "string"
        )
          message = error.message;
      }
    } catch {
      /* Le message générique couvre les réponses non JSON. */
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export function getObservations(
  start: string,
  end: string,
  signal?: AbortSignal,
): Promise<ObservationResponse> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return request(`/observations${params.size ? `?${params}` : ""}`, signal);
}
export const getSource = (signal?: AbortSignal) =>
  request<SourceInfo>("/source", signal);
export const getEpisodes = (signal?: AbortSignal) =>
  request<Episode[]>("/episodes", signal);
export const compareEpisodes = (a: string, b: string, signal?: AbortSignal) =>
  request<CompareResponse>(
    `/episodes/compare?${new URLSearchParams({ a, b })}`,
    signal,
  );

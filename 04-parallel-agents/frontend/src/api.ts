import type { ApiProblem, ExampleTask, Health, RunSnapshot, StreamEnvelope } from "./types";

export class ApiError extends Error {
  readonly status: number;
  readonly problem: ApiProblem;

  constructor(status: number, problem: ApiProblem) {
    const detail = problem.detail;
    let message = `La API respondió con estado ${status}.`;
    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail.map((item) => item.msg ?? "Dato inválido").join(" · ");
    } else if (detail?.message) {
      message = detail.message;
    }
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.problem = problem;
  }
}

async function readJson<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as T | ApiProblem;
  if (!response.ok) {
    throw new ApiError(response.status, payload as ApiProblem);
  }
  return payload as T;
}

export function fetchHealth(): Promise<Health> {
  return fetch("/api/v1/health").then((response) => readJson<Health>(response));
}

export function fetchExample(): Promise<ExampleTask> {
  return fetch("/api/v1/examples/i-parallel-002").then((response) => readJson<ExampleTask>(response));
}

export function startExperiment(body: {
  task: string;
  include_sequential: boolean;
  include_parallel: boolean;
}): Promise<{ run_id: string; status: string; case_id: string }> {
  return fetch("/api/v1/experiments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((response) => readJson(response));
}

export function fetchRun(runId: string): Promise<RunSnapshot> {
  return fetch(`/api/v1/runs/${runId}`).then((response) => readJson<RunSnapshot>(response));
}

export function subscribeRun(
  runId: string,
  onMessage: (envelope: StreamEnvelope) => void,
  onError: (message: string) => void,
): () => void {
  const source = new EventSource(`/api/v1/runs/${runId}/events`);
  source.onmessage = (message) => {
    try {
      onMessage(JSON.parse(message.data) as StreamEnvelope);
    } catch {
      onError("El flujo SSE devolvió un evento que no es JSON.");
    }
  };
  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      return;
    }
    onError("Se perdió la conexión SSE con el backend.");
    source.close();
  };
  return () => source.close();
}

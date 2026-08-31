import type { Health, RunSnapshot } from "./types";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function readJson<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as T | { detail?: unknown };
  if (!response.ok) {
    const detail = (payload as { detail?: unknown }).detail;
    const message =
      typeof detail === "string"
        ? detail
        : `La API respondió con estado ${response.status}.`;
    throw new ApiError(response.status, message);
  }
  return payload as T;
}

export function fetchHealth(): Promise<Health> {
  return fetch("/api/health").then((response) => readJson<Health>(response));
}

export function startAudit(): Promise<RunSnapshot> {
  return fetch("/api/runs/audit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_dir: "fixtures/corpus" }),
  }).then((response) => readJson<RunSnapshot>(response));
}

export function getRun(runId: string): Promise<RunSnapshot> {
  return fetch(`/api/runs/${runId}`).then((response) => readJson<RunSnapshot>(response));
}

export function submitReview(body: {
  run_id: string;
  object_type: "claim" | "release_candidate";
  object_id: string;
  decision: "approved" | "rejected";
  reviewer: string;
  reason: string;
  expected_hash: string;
}): Promise<unknown> {
  return fetch("/api/reviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((response) => readJson(response));
}

export function buildRelease(body: {
  run_id: string;
  reviewer: string;
  reason: string;
}): Promise<RunSnapshot> {
  return fetch("/api/releases/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((response) => readJson<RunSnapshot>(response));
}

export function getCurrentRelease(): Promise<Record<string, string>> {
  return fetch("/api/releases/current").then((response) =>
    readJson<Record<string, string>>(response),
  );
}

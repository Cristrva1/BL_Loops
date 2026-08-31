import type {
  ApiProblem,
  ExportResult,
  FactoryIntake,
  FactoryResult,
  GuidanceResult,
} from "./types";

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

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = (await response.json()) as T | ApiProblem;
  if (!response.ok) {
    throw new ApiError(response.status, payload as ApiProblem);
  }
  return payload as T;
}

export function analyzeIntake(intake: FactoryIntake): Promise<GuidanceResult> {
  return postJson<GuidanceResult>("/api/v1/factory/questions", intake);
}

export function buildDraft(intake: FactoryIntake): Promise<FactoryResult> {
  return postJson<FactoryResult>("/api/v1/factory/draft", intake);
}

export function exportArtifact(artifact: FactoryResult["artifact"]): Promise<ExportResult> {
  return postJson<ExportResult>("/api/v1/artifacts/export", { artifact });
}


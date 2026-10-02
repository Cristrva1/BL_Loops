export type FlowStatus =
  | "idle"
  | "queued"
  | "running"
  | "waiting"
  | "retrying"
  | "done"
  | "failed"
  | "blocked";

export interface NodeView {
  id: string;
  title: string;
  state: FlowStatus;
  detail: string;
}

export interface CheckView {
  check_id: string;
  title: string;
  passed: boolean;
  evidence: string;
}

export interface VariantView {
  status: "idle" | "running" | "passed" | "failed";
  word_count: number | null;
  checks_passed: number | null;
  checks_total: number | null;
  passed: boolean | null;
  revision_used: boolean;
  headings: string[];
  preview: string;
  latency_ms: number | null;
  prompt_tokens: number | null;
  output_tokens: number | null;
  checks: CheckView[];
  llm_review_passed: boolean | null;
  llm_review_available: boolean;
}

export interface ComparisonView {
  winner: "baseline" | "orchestrated" | "tie" | "incomplete";
  baseline_passed: boolean | null;
  orchestrated_passed: boolean | null;
  check_delta: number | null;
  latency_delta_ms: number | null;
  explanation: string[];
}

export interface RunSnapshot {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  case_id: string;
  model: string;
  include_baseline: boolean;
  include_orchestrated: boolean;
  nodes: NodeView[];
  event_count: number;
  baseline: VariantView | null;
  orchestrated: VariantView | null;
  comparison: ComparisonView | null;
  jsonl_path: string | null;
  error: string | null;
}

export interface Health {
  version: string;
  lab_id: "03-orchestration";
  model: string;
  local_ollama_configured: boolean;
  llm_used: boolean;
  phase: string;
}

export interface ExampleTask {
  case_id: string;
  title: string;
  task: string;
  include_baseline: boolean;
  include_orchestrated: boolean;
}

export interface StreamEnvelope {
  event: {
    event_type: string;
    sequence: number;
    node?: { id: string; state: string } | null;
  };
  snapshot: RunSnapshot;
}

export interface ApiProblem {
  detail?: string | { message?: string } | Array<{ msg?: string }>;
}

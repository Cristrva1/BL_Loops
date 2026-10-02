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

export interface FactRowView {
  fact_id: string;
  topic: string;
  value: string;
  source_id: string;
  evidence: string;
}

export interface BranchView {
  source_id: string;
  node_id: string;
  title: string;
  status: "completed" | "failed" | "timeout";
  fact_ids: string[];
  facts: FactRowView[];
  latency_ms: number | null;
  error: string | null;
}

export interface TableView {
  rows: FactRowView[];
  completed_sources: string[];
  failed_sources: string[];
  preview: string;
}

export interface LaneView {
  status: "idle" | "running" | "passed" | "failed";
  passed: boolean | null;
  wall_ms: number | null;
  overlap_observed: boolean;
  max_in_flight: number | null;
  completed_sources: string[];
  failed_sources: string[];
  fact_count: number;
  preview: string;
  checks: CheckView[];
  branches: BranchView[];
  table: TableView | null;
  prompt_tokens: number | null;
  output_tokens: number | null;
}

export interface ComparisonView {
  winner: "sequential" | "parallel" | "tie" | "incomplete";
  sequential_passed: boolean | null;
  parallel_passed: boolean | null;
  sequential_ms: number | null;
  parallel_ms: number | null;
  speedup: number | null;
  completed_delta: number | null;
  overlap_observed: boolean;
  explanation: string[];
}

export interface RunSnapshot {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  case_id: string;
  model: string;
  include_sequential: boolean;
  include_parallel: boolean;
  nodes: NodeView[];
  event_count: number;
  sequential: LaneView | null;
  parallel: LaneView | null;
  comparison: ComparisonView | null;
  jsonl_path: string | null;
  error: string | null;
}

export interface Health {
  version: string;
  lab_id: "04-parallel-agents";
  model: string;
  local_ollama_configured: boolean;
  llm_used: boolean;
  phase: string;
  max_in_flight: number;
}

export interface SourceSummary {
  source_id: string;
  title: string;
  filename: string;
  chars: number;
  required_fact_ids: string[];
}

export interface ExampleTask {
  case_id: string;
  title: string;
  task: string;
  include_sequential: boolean;
  include_parallel: boolean;
  sources: SourceSummary[];
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

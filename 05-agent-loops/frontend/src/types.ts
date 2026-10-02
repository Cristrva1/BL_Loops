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

export interface BudgetView {
  max_iterations: number;
  max_errors: number;
  timeout_seconds: number;
  threshold: number;
}

export interface LoopDeclaration {
  objective: string;
  initial_score: number | null;
  best_known_score: number | null;
  budget: BudgetView;
  improvement_condition: string;
  stop_condition: string;
  stop_reason: string | null;
}

export interface CandidateView {
  iteration: number;
  checks_passed: number;
  checks_total: number;
  passed: boolean;
  is_best: boolean;
  prompt_chars: number;
  output_chars: number;
  preview: string;
  checks: CheckView[];
}

export interface IterationView {
  iteration: number;
  checks_passed: number;
  checks_total: number;
  passed: boolean;
  is_best: boolean;
  prompt_chars: number;
  output_chars: number;
  failed_checks: string[];
  error: string | null;
}

export interface RunSnapshot {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  case_id: string;
  model: string;
  nodes: NodeView[];
  event_count: number;
  declaration: LoopDeclaration | null;
  iterations: IterationView[];
  best: CandidateView | null;
  stop_reason: string | null;
  jsonl_path: string | null;
  error: string | null;
}

export interface Health {
  version: string;
  lab_id: "05-agent-loops";
  model: string;
  local_ollama_configured: boolean;
  llm_used: boolean;
  phase: string;
}

export interface ExampleTask {
  case_id: string;
  title: string;
  task: string;
  initial_prompt: string;
  budget: BudgetView;
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

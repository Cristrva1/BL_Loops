export type ArtifactType = "prompt" | "agent" | "skill";
export type OutputFormat = "json" | "markdown" | "text" | "yaml" | "code";
export type FlowStatus =
  | "idle"
  | "queued"
  | "running"
  | "waiting"
  | "retrying"
  | "done"
  | "failed"
  | "blocked";

export interface FactoryIntake {
  artifact_type: ArtifactType;
  idea: string;
  title: string | null;
  audience: string | null;
  context: string | null;
  input_name: string | null;
  output_format: OutputFormat | null;
  success_criteria: string[];
  constraints: string[];
  source_refs: string[];
  allowed_tools: string[];
  tools_confirmed: boolean;
  requires_human_approval: boolean;
}

export interface GuidedQuestion {
  question_id: string;
  field: string;
  prompt: string;
  why: string;
  example: string;
  required: boolean;
}

export interface FlowEvent {
  sequence: number;
  node_id: "capture" | "clarify" | "contract" | "validate" | "export";
  status: FlowStatus;
  title: string;
  detail: string;
}

export interface GuidanceResult {
  ready: boolean;
  readiness: number;
  completed_fields: string[];
  required_fields: string[];
  questions: GuidedQuestion[];
  events: FlowEvent[];
}

export interface Artifact {
  artifact_id: string;
  artifact_type: ArtifactType;
  title: string;
  content_hash: string;
  [key: string]: unknown;
}

export interface FactoryResult {
  artifact: Artifact;
  events: FlowEvent[];
  explanation: string[];
}

export interface ExportResult {
  artifact_id: string;
  relative_path: string;
  content_hash: string;
  events: FlowEvent[];
}

export interface ApiProblem {
  detail?:
    | string
    | {
        code?: string;
        message?: string;
        guidance?: GuidanceResult;
      }
    | Array<{ msg?: string; loc?: Array<string | number> }>;
}


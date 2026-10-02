export type WorkflowState =
  | "scope_draft"
  | "inventory_running"
  | "gaps_ready"
  | "research_planned"
  | "awaiting_external_authorization"
  | "collecting_local"
  | "sources_normalized"
  | "claims_extracted"
  | "verification_running"
  | "conflicts_open"
  | "review_pending"
  | "changes_requested"
  | "approved"
  | "rejected"
  | "staging"
  | "validating"
  | "published"
  | "failed";

export interface SourceRecord {
  source_id: string;
  title: string;
  author: string;
  published_at: string | null;
  license: string;
  origin_source_id: string;
  independence: string;
  quarantine_status: string;
  content_sha256: string;
  uri: string;
  warnings: string[];
}

export interface ClaimRecord {
  claim_id: string;
  canonical_text: string;
  claim_type: string;
  topic: string;
  status: string;
  content_hash: string;
  identity_hash: string;
  population: string | null;
  evidence: Array<{ locator: string; source_id: string; support_assessment: string }>;
}

export interface ConflictRecord {
  conflict_id: string;
  topic: string;
  claim_ids: string[];
  materiality: string;
  resolution: string | null;
}

export interface GapRecord {
  gap_id: string;
  topic: string;
  reason: string;
}

export interface RunEvent {
  sequence: number;
  node_id: string;
  state: WorkflowState;
  result_sanitized: Record<string, unknown>;
  error: string | null;
}

export interface RunSnapshot {
  run_id: string;
  state: WorkflowState;
  stop_reason: string | null;
  network_enabled: boolean;
  urls_used: number;
  nodes: string[];
  sources: SourceRecord[];
  claims: ClaimRecord[];
  conflicts: ConflictRecord[];
  gaps: GapRecord[];
  events: RunEvent[];
  findings: unknown[];
  metrics: Record<string, number | null>;
  release_id: string | null;
  candidate_id: string | null;
  candidate_hash: string | null;
  candidate_diff: {
    previous_release_id?: string | null;
    included_claim_ids: string[];
    excluded_claim_ids: string[];
    source_count: number;
    conflict_count: number;
  } | null;
  jsonl_path: string | null;
}

export interface Health {
  version: string;
  network_enabled: boolean;
  telemetry: boolean;
  extractor: string;
  model_configured: boolean;
  configuration_scope: string;
  phase: string;
}

export interface LibraryWorkSummary {
  work_id: string;
  title: string;
  author: string | null;
  status: string;
  offers_count: number;
  has_legal_copy: boolean;
  gaps: string[];
  rounds_used: number;
}

export interface LibraryIndex {
  loop_id: string | null;
  inventory_count: number;
  works: LibraryWorkSummary[];
}

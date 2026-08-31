"""Contratos del laboratorio: la unidad central es la afirmación trazable."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class SourceKind(StrEnum):
    LOCAL_MARKDOWN = "local_markdown"
    LOCAL_TXT = "local_txt"


class Independence(StrEnum):
    ORIGINAL = "original"
    SYNDICATED = "syndicated"
    DERIVED = "derived"
    UNKNOWN = "unknown"


class QuarantineStatus(StrEnum):
    CLEAR = "clear"
    EMPTY = "empty"
    UNCERTAIN_RIGHTS = "uncertain_rights"
    INJECTION = "injection"
    UNSUPPORTED_MIME = "unsupported_mime"
    OVERSIZE = "oversize"


class ClaimType(StrEnum):
    EMPIRICAL = "empirical"
    PRESCRIPTIVE = "prescriptive"
    DEFINITION = "definition"
    VENDOR_SELF_CLAIM = "vendor_self_claim"
    LEGAL_OR_POLICY = "legal_or_policy"
    ANECDOTAL = "anecdotal"


class ClaimStatus(StrEnum):
    CANDIDATE = "candidate"
    SUPPORTED_SINGLE_SOURCE = "supported_single_source"
    CORROBORATED = "corroborated"
    HUMAN_APPROVED = "human_approved"
    PUBLISHED = "published"
    DISPUTED = "disputed"
    OUTDATED = "outdated"
    UNSUPPORTED = "unsupported"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    QUARANTINED = "quarantined"


class EvidenceRelation(StrEnum):
    SUPPORTS = "supports"
    REFUTES = "refutes"
    QUALIFIES = "qualifies"


class SupportAssessment(StrEnum):
    SUPPORTS = "supports"
    DOES_NOT_SUPPORT = "does_not_support"
    UNCLEAR = "unclear"


class WorkflowStatus(StrEnum):
    SCOPE_DRAFT = "scope_draft"
    INVENTORY_RUNNING = "inventory_running"
    GAPS_READY = "gaps_ready"
    RESEARCH_PLANNED = "research_planned"
    AWAITING_EXTERNAL_AUTHORIZATION = "awaiting_external_authorization"
    COLLECTING_LOCAL = "collecting_local"
    SOURCES_NORMALIZED = "sources_normalized"
    CLAIMS_EXTRACTED = "claims_extracted"
    VERIFICATION_RUNNING = "verification_running"
    CONFLICTS_OPEN = "conflicts_open"
    REVIEW_PENDING = "review_pending"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    STAGING = "staging"
    VALIDATING = "validating"
    PUBLISHED = "published"
    FAILED = "failed"


class ReviewVerdict(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ConflictType(StrEnum):
    DIRECT_CONTRADICTION = "direct_contradiction"
    SCOPE_MISMATCH = "scope_mismatch"
    DATE_COLLISION = "date_collision"


class Materiality(StrEnum):
    MATERIAL = "material"
    MINOR = "minor"


class TaskStatus(StrEnum):
    PLANNED = "planned"
    BLOCKED_NETWORK = "blocked_network"
    COLLECTED_LOCAL = "collected_local"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


HASH_PATTERN = r"^[0-9a-f]{64}$"
ID_PATTERN = r"^[a-z][a-z0-9_-]{1,80}$"
ClaimReference = Annotated[str, Field(pattern=ID_PATTERN)]


def _validate_claim_relations(
    claim_id: str,
    conflicts_with: list[str],
    supersedes: str | None,
) -> None:
    if len(conflicts_with) != len(set(conflicts_with)):
        raise ValueError("conflicts_with no admite IDs duplicados")
    if claim_id in conflicts_with:
        raise ValueError("una afirmación no puede entrar en conflicto consigo misma")
    if supersedes == claim_id:
        raise ValueError("una afirmación no puede reemplazarse a sí misma")


class QualityScores(StrictModel):
    """Dimensiones 0-4. Un promedio no publica nada por sí solo."""

    authority: int = Field(ge=0, le=4)
    evidence_proximity: int = Field(ge=0, le=4)
    recency: int = Field(ge=0, le=4)
    independence: int = Field(ge=0, le=4)
    applicability: int = Field(ge=0, le=4)
    extraction_integrity: int = Field(ge=0, le=4)
    rights_clarity: int = Field(ge=0, le=4)


class SourceRecord(StrictModel):
    source_id: str = Field(pattern=ID_PATTERN)
    kind: SourceKind
    title: str = Field(min_length=3, max_length=200)
    author: str = Field(min_length=1, max_length=160)
    editor: str | None = Field(default=None, max_length=160)
    uri: str = Field(min_length=1, max_length=500)
    published_at: date | None = None
    updated_at: date | None = None
    retrieved_at: datetime
    license: str = Field(min_length=1, max_length=80)
    usage_basis: str = Field(min_length=3, max_length=80)
    redistribution_allowed: bool
    content_sha256: str = Field(pattern=HASH_PATTERN)
    language: str = Field(min_length=2, max_length=12)
    jurisdiction: str = Field(min_length=2, max_length=40)
    origin_source_id: str = Field(pattern=ID_PATTERN)
    independence: Independence
    topics: list[str] = Field(default_factory=list, max_length=20)
    quarantine_status: QuarantineStatus
    rights_clarity: int = Field(ge=0, le=4)
    warnings: list[str] = Field(default_factory=list, max_length=20)
    content_hash: str = Field(pattern=HASH_PATTERN)

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("retrieved_at debe incluir zona horaria")
        return value


class DocumentArtifact(StrictModel):
    artifact_id: str = Field(pattern=ID_PATTERN)
    source_id: str = Field(pattern=ID_PATTERN)
    mime: Literal["text/markdown", "text/plain"]
    extractor: str = Field(min_length=3, max_length=80)
    extractor_version: str = Field(min_length=1, max_length=20)
    original_hash: str = Field(pattern=HASH_PATTERN)
    normalized_hash: str = Field(pattern=HASH_PATTERN)
    size_bytes: int = Field(ge=0, le=20_000_000)
    quarantine_status: QuarantineStatus
    warnings: list[str] = Field(default_factory=list, max_length=20)
    locators: list[str] = Field(default_factory=list, max_length=200)
    content_hash: str = Field(pattern=HASH_PATTERN)


class ClaimCandidate(StrictModel):
    claim_id: str = Field(pattern=ID_PATTERN)
    text: str = Field(min_length=8, max_length=800)
    claim_type: ClaimType
    topic: str = Field(pattern=r"^[a-z][a-z0-9-]{1,40}$")
    population: str | None = Field(default=None, max_length=160)
    context: str | None = Field(default=None, max_length=300)
    jurisdiction: str | None = Field(default=None, max_length=40)
    valid_from: date | None = None
    valid_until: date | None = None
    method: str | None = Field(default=None, max_length=200)
    sample: str | None = Field(default=None, max_length=80)
    conflicts_with: list[ClaimReference] = Field(default_factory=list, max_length=20)
    supersedes: ClaimReference | None = None
    locator: str = Field(min_length=2, max_length=80)
    source_id: str = Field(pattern=ID_PATTERN)

    @model_validator(mode="after")
    def relations_are_consistent(self) -> Self:
        _validate_claim_relations(self.claim_id, self.conflicts_with, self.supersedes)
        return self


class EvidenceLink(StrictModel):
    claim_id: str = Field(pattern=ID_PATTERN)
    source_id: str = Field(pattern=ID_PATTERN)
    locator: str = Field(min_length=2, max_length=80)
    relation: EvidenceRelation
    fragment_min: str = Field(min_length=8, max_length=800)
    fragment_hash: str = Field(pattern=HASH_PATTERN)
    support_assessment: SupportAssessment
    content_hash: str = Field(pattern=HASH_PATTERN)


class ClaimRecord(StrictModel):
    claim_id: str = Field(pattern=ID_PATTERN)
    canonical_text: str = Field(min_length=8, max_length=800)
    claim_type: ClaimType
    topic: str = Field(pattern=r"^[a-z][a-z0-9-]{1,40}$")
    population: str | None = Field(default=None, max_length=160)
    context: str | None = Field(default=None, max_length=300)
    jurisdiction: str | None = Field(default=None, max_length=40)
    valid_from: date | None = None
    valid_until: date | None = None
    method: str | None = Field(default=None, max_length=200)
    sample: str | None = Field(default=None, max_length=80)
    status: ClaimStatus
    version: int = Field(ge=1, le=99)
    conflicts_with: list[ClaimReference] = Field(default_factory=list, max_length=20)
    supersedes: ClaimReference | None = None
    created_by: str = Field(min_length=3, max_length=80)
    created_at: datetime
    updated_at: datetime
    quality: QualityScores
    evidence: list[EvidenceLink] = Field(default_factory=list, max_length=30)
    challenge_note: str | None = Field(default=None, max_length=400)
    content_hash: str = Field(pattern=HASH_PATTERN)

    @model_validator(mode="after")
    def relations_are_consistent(self) -> Self:
        _validate_claim_relations(self.claim_id, self.conflicts_with, self.supersedes)
        return self

    @field_validator("created_at", "updated_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("las fechas deben incluir zona horaria")
        return value


class ConflictRecord(StrictModel):
    conflict_id: str = Field(pattern=ID_PATTERN)
    claim_ids: list[str] = Field(min_length=2, max_length=8)
    conflict_type: ConflictType
    topic: str = Field(min_length=2, max_length=40)
    evidence_by_side: dict[str, list[str]]
    materiality: Materiality
    resolution: str | None = Field(default=None, max_length=400)
    owner: str | None = Field(default=None, max_length=80)
    content_hash: str = Field(pattern=HASH_PATTERN)


class GapRecord(StrictModel):
    gap_id: str = Field(pattern=ID_PATTERN)
    topic: str = Field(min_length=2, max_length=40)
    reason: str = Field(min_length=8, max_length=400)
    source_ids: list[str] = Field(default_factory=list, max_length=20)
    content_hash: str = Field(pattern=HASH_PATTERN)


class ResearchTask(StrictModel):
    task_id: str = Field(pattern=ID_PATTERN)
    question: str = Field(min_length=8, max_length=400)
    motivation: str = Field(min_length=8, max_length=400)
    target_kinds: list[Literal["primary", "synthesis", "challenging", "local"]] = Field(
        min_length=1, max_length=4
    )
    allowlist: list[str] = Field(default_factory=list, max_length=20)
    budget_urls: int = Field(ge=0, le=20)
    sufficiency: str = Field(min_length=8, max_length=300)
    stop_criterion: str = Field(min_length=8, max_length=300)
    status: TaskStatus
    content_hash: str = Field(pattern=HASH_PATTERN)


class ResearchFinding(StrictModel):
    finding_id: str = Field(pattern=ID_PATTERN)
    task_id: str = Field(pattern=ID_PATTERN)
    source_id: str | None = Field(default=None, pattern=ID_PATTERN)
    summary: str = Field(min_length=8, max_length=500)
    failed: bool = False
    failure_reason: str | None = Field(default=None, max_length=300)
    content_hash: str = Field(pattern=HASH_PATTERN)


class SourceAssessment(StrictModel):
    source_id: str = Field(pattern=ID_PATTERN)
    quarantine_status: QuarantineStatus
    independence: Independence
    duplicate_of: str | None = Field(default=None, pattern=ID_PATTERN)
    origin_source_id: str = Field(pattern=ID_PATTERN)
    notes: list[str] = Field(default_factory=list, max_length=20)
    content_hash: str = Field(pattern=HASH_PATTERN)


class ReviewDecision(StrictModel):
    decision_id: str = Field(pattern=ID_PATTERN)
    object_type: Literal["claim", "release_candidate"]
    object_id: str = Field(pattern=ID_PATTERN)
    decision: ReviewVerdict
    reviewer: str = Field(min_length=2, max_length=80)
    reason: str = Field(min_length=8, max_length=500)
    decided_at: datetime
    conditions: list[str] = Field(default_factory=list, max_length=10)
    approved_hash: str = Field(pattern=HASH_PATTERN)
    content_hash: str = Field(pattern=HASH_PATTERN)

    @field_validator("decided_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decided_at debe incluir zona horaria")
        return value

    @field_validator("reviewer")
    @classmethod
    def reviewer_is_person(cls, value: str) -> str:
        lowered = value.casefold()
        if lowered in {"model", "llm", "orchestrator", "system", "ollama"}:
            raise ValueError("la revisión humana no puede atribuirse a un modelo")
        return value


class KnowledgeDraft(StrictModel):
    topic: str = Field(min_length=2, max_length=40)
    markdown: str = Field(min_length=20, max_length=20000)
    claim_ids: list[str] = Field(default_factory=list, max_length=50)
    content_hash: str = Field(pattern=HASH_PATTERN)


class KnowledgeRelease(StrictModel):
    release_id: str = Field(pattern=ID_PATTERN)
    schema_version: Literal["1.0.0"] = "1.0.0"
    domain: str = Field(min_length=3, max_length=80)
    as_of: date
    file_hashes: dict[str, str]
    included_claim_ids: list[str] = Field(default_factory=list, max_length=200)
    excluded_claim_ids: list[str] = Field(default_factory=list, max_length=200)
    approval_ids: list[str] = Field(min_length=1, max_length=50)
    metrics: dict[str, float | int | None] = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)
    rollback_of: str | None = Field(default=None, pattern=ID_PATTERN)
    manifest_hash: str = Field(pattern=HASH_PATTERN)
    content_hash: str = Field(pattern=HASH_PATTERN)


class AdversarialFinding(StrictModel):
    finding_id: str = Field(pattern=ID_PATTERN)
    kind: Literal[
        "prompt_injection",
        "circular_evidence",
        "cherry_pick",
        "scope_excess",
        "rights_unclear",
    ]
    object_id: str = Field(pattern=ID_PATTERN)
    detail: str = Field(min_length=8, max_length=400)
    content_hash: str = Field(pattern=HASH_PATTERN)


class RunEvent(StrictModel):
    run_id: str = Field(pattern=ID_PATTERN)
    sequence: int = Field(ge=1)
    event_id: str = Field(pattern=ID_PATTERN)
    occurred_at: datetime
    node_id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$", max_length=80)
    state: WorkflowStatus
    tool: str | None = Field(default=None, max_length=80)
    result_sanitized: dict[str, Any] = Field(default_factory=dict)
    error: str | None = Field(default=None, max_length=400)
    tokens: int | None = Field(default=None, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)
    ram_mb: float | None = Field(default=None, ge=0)
    vram_mb: float | None = Field(default=None, ge=0)
    refs: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at debe incluir zona horaria")
        return value


class WorkflowState(StrictModel):
    run_id: str = Field(pattern=ID_PATTERN)
    state: WorkflowStatus
    previous_state: WorkflowStatus | None = None
    actor: str = Field(min_length=3, max_length=80)
    reason: str = Field(min_length=3, max_length=400)
    changed_at: datetime
    stop_reason: str | None = Field(default=None, max_length=400)
    research_round: int = Field(default=0, ge=0, le=8)
    claim_revision: int = Field(default=0, ge=0, le=5)
    network_enabled: bool = False
    urls_used: int = Field(default=0, ge=0)
    content_hash: str = Field(pattern=HASH_PATTERN)

    @field_validator("changed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("changed_at debe incluir zona horaria")
        return value


class ResourceUsage(StrictModel):
    latency_ms: float = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    ram_peak_mb: float | None = Field(default=None, ge=0)
    vram_peak_mb: float | None = Field(default=None, ge=0)


class MetricScore(StrictModel):
    name: str = Field(min_length=3, max_length=80)
    applicable: bool = True
    value: float | None = Field(default=None, ge=0, le=1)
    note: str | None = Field(default=None, max_length=500)


class RunRecord(StrictModel):
    run_id: str = Field(pattern=ID_PATTERN)
    schema_version: Literal["1.0.0"] = "1.0.0"
    lab_id: Literal["13-sales-knowledge-curator"] = "13-sales-knowledge-curator"
    variant: str = Field(min_length=1, max_length=120)
    commit_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{7,40}$")
    model_ref: str
    evaluation_case: str
    case_version: str
    events: list[RunEvent] = Field(min_length=1)
    inputs_sanitized: dict[str, Any]
    outputs_sanitized: dict[str, Any]
    errors: list[dict[str, Any]] = Field(default_factory=list)
    resource_usage: ResourceUsage
    scores: list[MetricScore]
    aggregate_score: float | None = Field(default=None, ge=0, le=1)
    status: Literal["passed", "failed", "blocked"]
    failure_reasons: list[str] = Field(default_factory=list)
    created_at: datetime
    content_hash: str = Field(pattern=HASH_PATTERN)

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at debe incluir zona horaria")
        return value

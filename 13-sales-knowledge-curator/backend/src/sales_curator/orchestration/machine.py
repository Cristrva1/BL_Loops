"""Transiciones explícitas. Toda parada guarda actor, hora y razón."""

from __future__ import annotations

from sales_curator.contracts.models import WorkflowStatus

TRANSITIONS: dict[WorkflowStatus, frozenset[WorkflowStatus]] = {
    WorkflowStatus.SCOPE_DRAFT: frozenset(
        {WorkflowStatus.INVENTORY_RUNNING, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.INVENTORY_RUNNING: frozenset({WorkflowStatus.GAPS_READY, WorkflowStatus.FAILED}),
    WorkflowStatus.GAPS_READY: frozenset({WorkflowStatus.RESEARCH_PLANNED, WorkflowStatus.FAILED}),
    WorkflowStatus.RESEARCH_PLANNED: frozenset(
        {
            WorkflowStatus.AWAITING_EXTERNAL_AUTHORIZATION,
            WorkflowStatus.COLLECTING_LOCAL,
            WorkflowStatus.FAILED,
        }
    ),
    WorkflowStatus.AWAITING_EXTERNAL_AUTHORIZATION: frozenset(
        {WorkflowStatus.COLLECTING_LOCAL, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.COLLECTING_LOCAL: frozenset(
        {WorkflowStatus.SOURCES_NORMALIZED, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.SOURCES_NORMALIZED: frozenset(
        {WorkflowStatus.CLAIMS_EXTRACTED, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.CLAIMS_EXTRACTED: frozenset(
        {WorkflowStatus.VERIFICATION_RUNNING, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.VERIFICATION_RUNNING: frozenset(
        {WorkflowStatus.CONFLICTS_OPEN, WorkflowStatus.REVIEW_PENDING, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.CONFLICTS_OPEN: frozenset(
        {WorkflowStatus.REVIEW_PENDING, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.REVIEW_PENDING: frozenset(
        {
            WorkflowStatus.CHANGES_REQUESTED,
            WorkflowStatus.APPROVED,
            WorkflowStatus.REJECTED,
            WorkflowStatus.FAILED,
        }
    ),
    WorkflowStatus.CHANGES_REQUESTED: frozenset(
        {WorkflowStatus.RESEARCH_PLANNED, WorkflowStatus.FAILED}
    ),
    WorkflowStatus.APPROVED: frozenset({WorkflowStatus.STAGING, WorkflowStatus.FAILED}),
    WorkflowStatus.REJECTED: frozenset({WorkflowStatus.FAILED}),
    WorkflowStatus.STAGING: frozenset({WorkflowStatus.VALIDATING, WorkflowStatus.FAILED}),
    WorkflowStatus.VALIDATING: frozenset({WorkflowStatus.PUBLISHED, WorkflowStatus.FAILED}),
    WorkflowStatus.PUBLISHED: frozenset(),
    WorkflowStatus.FAILED: frozenset(),
}

NODE_FOR_STATE: dict[WorkflowStatus, str] = {
    WorkflowStatus.SCOPE_DRAFT: "ingest",
    WorkflowStatus.INVENTORY_RUNNING: "ingest",
    WorkflowStatus.GAPS_READY: "research",
    WorkflowStatus.RESEARCH_PLANNED: "research",
    WorkflowStatus.AWAITING_EXTERNAL_AUTHORIZATION: "research",
    WorkflowStatus.COLLECTING_LOCAL: "research",
    WorkflowStatus.SOURCES_NORMALIZED: "registry",
    WorkflowStatus.CLAIMS_EXTRACTED: "extraction",
    WorkflowStatus.VERIFICATION_RUNNING: "verification",
    WorkflowStatus.CONFLICTS_OPEN: "verification",
    WorkflowStatus.REVIEW_PENDING: "review",
    WorkflowStatus.CHANGES_REQUESTED: "review",
    WorkflowStatus.APPROVED: "review",
    WorkflowStatus.REJECTED: "review",
    WorkflowStatus.STAGING: "staging",
    WorkflowStatus.VALIDATING: "gate",
    WorkflowStatus.PUBLISHED: "release",
    WorkflowStatus.FAILED: "release",
}

VISIBLE_NODES = (
    "ingest",
    "registry",
    "extraction",
    "ledger",
    "research",
    "verification",
    "review",
    "staging",
    "gate",
    "release",
)


class InvalidTransition(ValueError):
    """Transición prohibida por la máquina de estados."""


def ensure_transition(current: WorkflowStatus, nxt: WorkflowStatus) -> None:
    allowed = TRANSITIONS.get(current, frozenset())
    if nxt not in allowed:
        raise InvalidTransition(f"No se puede pasar de {current.value} a {nxt.value}")

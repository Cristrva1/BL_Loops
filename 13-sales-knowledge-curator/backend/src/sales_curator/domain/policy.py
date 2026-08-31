"""Permisos denegados por defecto y catálogo de temas del dominio ficticio."""

from __future__ import annotations

from typing import Final

DEMO_DOMAIN: Final = "venta-consultiva-vivienda-demo"

EXPECTED_TOPICS: Final[tuple[str, ...]] = (
    "discovery",
    "closing",
    "price-timing",
    "after-sales",
    "vendor-tools",
)

ROLE_PERMISSIONS: Final[dict[str, frozenset[str]]] = {
    "orchestrator": frozenset({"transition", "budget", "emit_event"}),
    "source_auditor": frozenset({"read_local", "classify_source"}),
    "gap_planner": frozenset({"plan_research"}),
    "researcher": frozenset({"read_local"}),
    "claim_extractor": frozenset({"extract_claims"}),
    "claim_verifier": frozenset({"verify_claims"}),
    "editor": frozenset({"draft_knowledge"}),
    "red_team": frozenset({"scan_threats"}),
    "publisher": frozenset({"stage_release", "publish_if_approved"}),
    "human_reviewer": frozenset({"approve", "reject", "request_changes"}),
}

DENIED_TO_ALL_MODELS: Final[frozenset[str]] = frozenset(
    {
        "enable_network",
        "expand_allowlist",
        "publish_release",
        "approve_release",
        "write_outside_lab",
        "call_cloud",
    }
)


def role_may(role: str, capability: str) -> bool:
    if capability in DENIED_TO_ALL_MODELS and role != "human_reviewer":
        return False
    return capability in ROLE_PERMISSIONS.get(role, frozenset())

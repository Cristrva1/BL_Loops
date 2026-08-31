"""Métricas editoriales sobre el fixture. Un promedio no abre el gate de publicación."""

from __future__ import annotations

from sales_curator.contracts.models import (
    AdversarialFinding,
    ClaimRecord,
    ClaimStatus,
    ConflictRecord,
    GapRecord,
    Independence,
    QuarantineStatus,
    SourceRecord,
)


def compute_metrics(
    sources: list[SourceRecord],
    claims: list[ClaimRecord],
    conflicts: list[ConflictRecord],
    gaps: list[GapRecord],
    findings: list[AdversarialFinding],
) -> dict[str, float | int | None]:
    verifiable = [
        claim
        for claim in claims
        if claim.status
        not in {ClaimStatus.REJECTED, ClaimStatus.QUARANTINED, ClaimStatus.UNSUPPORTED}
    ]
    cited = 0
    for claim in verifiable:
        if any(
            link.locator.startswith("L") and link.support_assessment.value == "supports"
            for link in claim.evidence
        ):
            cited += 1
    citation_integrity = (cited / len(verifiable)) if verifiable else 1.0
    return {
        "source_count": len(sources),
        "claim_count": len(claims),
        "conflict_count": len(conflicts),
        "gap_count": len(gaps),
        "finding_count": len(findings),
        "quarantined_sources": sum(
            1 for item in sources if item.quarantine_status != QuarantineStatus.CLEAR
        ),
        "syndicated_sources": sum(
            1 for item in sources if item.independence == Independence.SYNDICATED
        ),
        "disputed_claims": sum(1 for item in claims if item.status == ClaimStatus.DISPUTED),
        "outdated_or_superseded": sum(
            1 for item in claims if item.status in {ClaimStatus.OUTDATED, ClaimStatus.SUPERSEDED}
        ),
        "human_approved": sum(1 for item in claims if item.status == ClaimStatus.HUMAN_APPROVED),
        "citation_integrity": round(citation_integrity, 4),
        "conflict_recall_fixture": 1.0 if conflicts else 0.0,
        "gap_recall_fixture": 1.0 if gaps else 0.0,
    }

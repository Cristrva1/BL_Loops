"""Gate técnico. Un score alto no publica; faltan aprobación humana y localizadores."""

from __future__ import annotations

from sales_curator.contracts.models import ClaimRecord, ClaimStatus, ReviewDecision, ReviewVerdict
from sales_curator.hashing import compute_content_hash


def claim_identity_hash(claim: ClaimRecord) -> str:
    """Huella editorial: cambia si cambia el contenido, no el estado de revisión."""

    return compute_content_hash(
        claim.model_dump(
            mode="json",
            exclude={"status", "created_at", "updated_at", "content_hash"},
        )
    )


def claim_passes_technical_gate(claim: ClaimRecord) -> list[str]:
    errors: list[str] = []
    if len(claim.canonical_text.split()) < 5:
        errors.append("texto no atómico o demasiado vago")
    if not claim.evidence:
        errors.append("sin evidencia")
    elif not any(
        item.locator.startswith("L") and item.support_assessment.value == "supports"
        for item in claim.evidence
    ):
        errors.append("sin localizador de apoyo")
    if claim.status in {
        ClaimStatus.DISPUTED,
        ClaimStatus.REJECTED,
        ClaimStatus.QUARANTINED,
        ClaimStatus.UNSUPPORTED,
        ClaimStatus.OUTDATED,
        ClaimStatus.SUPERSEDED,
    }:
        errors.append(f"estado no publicable: {claim.status.value}")
    if claim.claim_type.value == "legal_or_policy":
        errors.append("afirmación legal exige especialista humano")
    return errors


def matching_approval(claim: ClaimRecord, reviews: list[ReviewDecision]) -> ReviewDecision | None:
    digest = claim_identity_hash(claim)
    for review in reviews:
        if (
            review.object_type == "claim"
            and review.object_id == claim.claim_id
            and review.decision == ReviewVerdict.APPROVED
            and review.approved_hash == digest
        ):
            return review
    return None


def candidate_approval(
    candidate_id: str,
    candidate_hash: str,
    reviews: list[ReviewDecision],
) -> ReviewDecision | None:
    for review in reviews:
        if (
            review.object_type == "release_candidate"
            and review.object_id == candidate_id
            and review.decision == ReviewVerdict.APPROVED
            and review.approved_hash == candidate_hash
        ):
            return review
    return None

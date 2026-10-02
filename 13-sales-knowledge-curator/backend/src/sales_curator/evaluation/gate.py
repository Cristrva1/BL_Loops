"""Gate técnico. Un score alto no publica; faltan aprobación humana y localizadores."""

from __future__ import annotations

from collections.abc import Sequence

from sales_curator.contracts.models import (
    ClaimRecord,
    ClaimStatus,
    ReviewDecision,
    ReviewProjection,
    ReviewVerdict,
)
from sales_curator.hashing import compute_content_hash

ReviewLike = ReviewDecision | ReviewProjection


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


def latest_review(
    *,
    object_type: str,
    object_id: str,
    approved_hash: str,
    reviews: Sequence[ReviewLike],
) -> ReviewLike | None:
    matching = [
        review
        for review in reviews
        if review.object_type == object_type
        and review.object_id == object_id
        and review.approved_hash == approved_hash
    ]
    if not matching:
        return None
    return max(matching, key=lambda item: (item.decided_at, item.decision_id))


def matching_approval(claim: ClaimRecord, reviews: Sequence[ReviewLike]) -> ReviewLike | None:
    latest = latest_review(
        object_type="claim",
        object_id=claim.claim_id,
        approved_hash=claim_identity_hash(claim),
        reviews=reviews,
    )
    if latest is None or latest.decision != ReviewVerdict.APPROVED:
        return None
    return latest


def candidate_approval(
    candidate_id: str,
    candidate_hash: str,
    reviews: Sequence[ReviewLike],
) -> ReviewLike | None:
    latest = latest_review(
        object_type="release_candidate",
        object_id=candidate_id,
        approved_hash=candidate_hash,
        reviews=reviews,
    )
    if latest is None or latest.decision != ReviewVerdict.APPROVED:
        return None
    return latest

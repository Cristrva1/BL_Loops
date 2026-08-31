from __future__ import annotations

from datetime import timedelta

import pytest

from sales_curator.contracts.models import ClaimStatus
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.orchestration.service import CuratorService


def test_identity_hash_covers_every_editorial_field(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    original = claim_identity_hash(claim)

    mutations = {
        "context": "Otro contexto editorial",
        "jurisdiction": "MX-CMX",
        "valid_from": claim.created_at.date(),
        "valid_until": claim.created_at.date() + timedelta(days=30),
        "method": "Entrevistas estructuradas",
        "sample": "24 conversaciones",
        "supersedes": "clm-previous-budget",
        "quality": claim.quality.model_copy(
            update={"authority": (claim.quality.authority + 1) % 5}
        ),
        "challenge_note": "Se encontró una fuente desafiante adicional.",
        "evidence": [
            claim.evidence[0].model_copy(update={"locator": "L1"}),
            *claim.evidence[1:],
        ],
        "version": claim.version + 1,
        "created_by": "editorial_reviewer",
    }

    for field, value in mutations.items():
        changed = claim.model_copy(update={field: value})
        assert claim_identity_hash(changed) != original, field


@pytest.mark.parametrize("field", ["status", "created_at", "updated_at", "content_hash"])
def test_identity_hash_ignores_runtime_review_state_and_metadata(
    service: CuratorService,
    corpus,
    field: str,
) -> None:
    snapshot = service.start_audit(corpus)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    original = claim_identity_hash(claim)
    values = {
        "status": ClaimStatus.HUMAN_APPROVED,
        "created_at": claim.created_at + timedelta(seconds=1),
        "updated_at": claim.updated_at + timedelta(seconds=1),
        "content_hash": "f" * 64,
    }

    changed = claim.model_copy(update={field: values[field]})

    assert claim_identity_hash(changed) == original

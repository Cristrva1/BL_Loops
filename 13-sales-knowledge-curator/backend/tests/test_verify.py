from __future__ import annotations

import pytest

from sales_curator.contracts.models import ClaimStatus
from sales_curator.domain.verify import merge_duplicates
from sales_curator.evaluation.gate import claim_passes_technical_gate
from sales_curator.hashing import with_content_hash
from sales_curator.orchestration.service import CuratorService


def test_audit_detects_gap_duplicate_obsolete_and_conflict(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    topics = {gap.topic for gap in snapshot.gaps}
    assert "after-sales" in topics
    assert any(source.independence.value == "syndicated" for source in snapshot.sources)
    assert any(
        claim.status in {ClaimStatus.OUTDATED, ClaimStatus.SUPERSEDED} for claim in snapshot.claims
    )
    assert snapshot.conflicts
    assert any(claim.status == ClaimStatus.DISPUTED for claim in snapshot.claims)
    assert snapshot.workflow.state.value == "review_pending"


def test_syndicated_copy_does_not_corroborate(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    budget = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    assert budget.status != ClaimStatus.CORROBORATED
    origins = {link.source_id for link in budget.evidence}
    assert "src-syndicated-discovery" in origins or len(budget.evidence) >= 1
    assert all(link.claim_id == budget.claim_id for link in budget.evidence)


def test_same_words_with_different_scope_are_not_merged(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    original = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    variant_id = "clm-ask-budget-other-population"
    evidence = [
        with_content_hash(
            link.model_copy(update={"claim_id": variant_id, "content_hash": "0" * 64})
        )
        for link in original.evidence
    ]
    variant = with_content_hash(
        original.model_copy(
            update={
                "claim_id": variant_id,
                "population": "otro-contexto-educativo",
                "evidence": evidence,
                "content_hash": "0" * 64,
            }
        )
    )
    sources = {item.source_id: item for item in snapshot.sources}

    merged = merge_duplicates([original, variant], sources)

    assert {item.claim_id for item in merged} == {original.claim_id, variant_id}


def test_duplicate_claim_id_with_incompatible_content_fails(
    service: CuratorService, corpus
) -> None:
    snapshot = service.start_audit(corpus)
    original = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    incompatible = with_content_hash(
        original.model_copy(
            update={
                "canonical_text": "Una afirmacion distinta que reutiliza el mismo identificador.",
                "content_hash": "0" * 64,
            }
        )
    )
    sources = {item.source_id: item for item in snapshot.sources}

    with pytest.raises(ValueError, match="claim_id duplicado"):
        merge_duplicates([original, incompatible], sources)


def test_vendor_claim_without_method_is_unsupported(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    vendor = next(item for item in snapshot.claims if item.claim_id == "clm-crm-close-rate")
    assert vendor.status == ClaimStatus.UNSUPPORTED
    assert claim_passes_technical_gate(vendor)


def test_each_supported_claim_has_locator(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    for claim in snapshot.claims:
        if claim.status in {ClaimStatus.SUPPORTED_SINGLE_SOURCE, ClaimStatus.DISPUTED}:
            assert claim.evidence
            assert claim.evidence[0].locator.startswith("L")

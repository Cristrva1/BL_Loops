from __future__ import annotations

from sales_curator.contracts.models import ClaimStatus
from sales_curator.evaluation.gate import claim_passes_technical_gate
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

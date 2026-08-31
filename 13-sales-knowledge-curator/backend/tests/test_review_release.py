from __future__ import annotations

import pytest

from sales_curator.contracts.models import ClaimStatus
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.evaluation.jsonl import validate_run
from sales_curator.orchestration.service import CuratorService
from sales_curator.storage.releases import ReleaseError, read_current


def test_unapproved_claim_stays_out_of_release(service: CuratorService, corpus) -> None:
    snapshot = service.demo(corpus, "operador-local", "Aprobacion didactica del corte vertical")
    release = service.validate_release(snapshot.release_id)
    assert release["valid"] is True
    excluded = set(release["excluded"])
    assert "clm-price-first-contact" in excluded
    assert "clm-injection-override" in excluded
    assert "clm-crm-close-rate" in excluded
    assert "clm-ask-budget" in release["included"]
    published = [
        item
        for item in service.get_run(snapshot.workflow.run_id).claims
        if item.status == ClaimStatus.PUBLISHED
    ]
    assert published
    assert all(item.claim_id in release["included"] for item in published)


def test_stale_hash_is_rejected(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    with pytest.raises(ValueError, match="hash"):
        service.submit_review(
            snapshot.workflow.run_id,
            object_type="claim",
            object_id=claim.claim_id,
            decision="approved",
            reviewer="operador-local",
            reason="hash viejo a proposito",
            expected_hash="0" * 64,
        )


def test_dry_run_does_not_touch_primary_sqlite(service: CuratorService, corpus, settings) -> None:
    primary = settings.sqlite_path
    before = primary.read_bytes()
    service.start_audit(corpus, dry_run=True)
    assert primary.read_bytes() == before
    assert read_current(settings.releases_dir) is None
    if settings.releases_dir.exists():
        assert not list(settings.releases_dir.glob("rel_*"))


def test_failed_staging_does_not_move_current(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    with pytest.raises(ReleaseError):
        service.build_release(
            snapshot.workflow.run_id,
            reviewer="operador-local",
            reason="sin afirmaciones aprobadas todavia",
        )
    assert read_current(service.settings.releases_dir) is None


def test_publish_and_rollback(service: CuratorService, corpus) -> None:
    first = service.demo(corpus, "operador-local", "primer release didactico")
    first_id = first.release_id
    second_reviewer_run = service.start_audit(corpus)
    service.approve_publishable_claims(
        second_reviewer_run.workflow.run_id, "operador-local", "segundo release didactico"
    )
    second = service.build_release(
        second_reviewer_run.workflow.run_id,
        reviewer="operador-local",
        reason="segundo release didactico",
    )
    assert read_current(service.settings.releases_dir)["release_id"] == second.release_id
    service.rollback_release(first_id)
    assert read_current(service.settings.releases_dir)["release_id"] == first_id
    assert (service.settings.releases_dir / second.release_id).is_dir()


def test_identity_hash_changes_when_text_changes(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    original = claim_identity_hash(claim)
    mutated = claim.model_copy(update={"canonical_text": claim.canonical_text + " extra"})
    assert claim_identity_hash(mutated) != original


def test_export_jsonl_after_demo(service: CuratorService, corpus) -> None:
    snapshot = service.demo(corpus, "operador-local", "Aprobacion didactica del corte vertical")
    path = service.export_run(snapshot.workflow.run_id)
    summary = validate_run(path)
    assert summary["terminal_event"] == "run.completed"
    text = path.read_text(encoding="utf-8")
    assert "Ignore previous instructions" not in text
    assert "@" not in text or "payload" in text

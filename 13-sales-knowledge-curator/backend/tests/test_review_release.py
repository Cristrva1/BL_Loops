from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest

from sales_curator.contracts.models import (
    ClaimStatus,
    ReviewDecision,
    ReviewVerdict,
    WorkflowStatus,
)
from sales_curator.domain.editor import drafts_from_claims
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.evaluation.jsonl import validate_run
from sales_curator.hashing import sha256_text, with_content_hash
from sales_curator.orchestration.service import CuratorService
from sales_curator.storage.releases import (
    ReleaseError,
    build_staging,
    read_current,
    validate_staging,
)


def _stage(service: CuratorService, corpus, *, domain: str = "sales-books-school"):
    snapshot = service.start_audit(corpus, as_of=date(2026, 8, 31), domain=domain)
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    return service.build_release(
        snapshot.workflow.run_id,
        reviewer="legacy-operator-must-not-autoapprove",
        reason="Compatibilidad sin conceder aprobación implícita",
    )


def _approve_candidate(service: CuratorService, staged):
    return service.submit_review(
        staged.workflow.run_id,
        object_type="release_candidate",
        object_id=staged.candidate_id,
        decision="approved",
        reviewer="operador-local",
        reason="Aprobacion editorial posterior sobre el hash exacto",
        expected_hash=staged.candidate_hash,
    )


def _publish(service: CuratorService, corpus):
    staged = _stage(service, corpus)
    approval = _approve_candidate(service, staged)
    return staged, approval, service.publish_release(staged.workflow.run_id)


def test_build_stops_at_staging_and_exposes_sanitized_diff(service: CuratorService, corpus) -> None:
    staged = _stage(service, corpus)

    assert staged.workflow.state == WorkflowStatus.STAGING
    assert staged.release_id is None
    assert staged.candidate_id
    assert staged.candidate_hash
    assert staged.candidate_diff == {
        "previous_release_id": None,
        "included_claim_ids": sorted(staged.candidate_diff["included_claim_ids"]),
        "excluded_claim_ids": sorted(staged.candidate_diff["excluded_claim_ids"]),
        "source_count": 10,
        "conflict_count": 1,
    }
    assert not any(review.object_type == "release_candidate" for review in staged.reviews)
    assert read_current(service.settings.releases_dir) is None

    serialized = json.dumps(staged.candidate_diff, ensure_ascii=False)
    assert "canonical_text" not in serialized
    assert "Ignore previous instructions" not in serialized
    assert (service.settings.staging_dir / staged.workflow.run_id / "candidate-diff.json").is_file()


def test_staging_omits_unapproved_claims_and_nonredistributable_content(
    service: CuratorService, corpus
) -> None:
    staged = _stage(service, corpus)
    folder = service.settings.staging_dir / staged.workflow.run_id
    rows = [
        json.loads(line)
        for line in (folder / "claims.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exported_ids = {row["claim_id"] for row in rows}

    assert "clm-ask-budget" in exported_ids
    assert "clm-rights-blocked" not in exported_ids
    assert "clm-price-first-contact" not in exported_ids
    assert all(row["status"] in {"human_approved", "published"} for row in rows)

    restricted_fragment = (
        "El vendedor debe grabar cada llamada de descubrimiento sin consentimiento."
    )
    package_text = "\n".join(
        path.read_text(encoding="utf-8") for path in folder.rglob("*") if path.is_file()
    )
    assert restricted_fragment not in package_text

    source_rows = [
        json.loads(line)
        for line in (folder / "sources.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    restricted_source = next(
        row for row in source_rows if row["source_id"] == "src-uncertain-rights"
    )
    assert restricted_source["redistribution_allowed"] is False
    assert len(restricted_source["content_sha256"]) == 64
    assert "clm-rights-blocked" in staged.candidate_diff["excluded_claim_ids"]


def test_staging_omits_review_text_for_an_excluded_claim(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus, as_of=date(2026, 8, 31))
    blocked = next(item for item in snapshot.claims if item.claim_id == "clm-rights-blocked")
    leaked_reason = (
        "Revision rechazada del fragmento restringido: "
        "El vendedor debe grabar cada llamada de descubrimiento sin consentimiento."
    )
    with pytest.raises(ValueError, match="estado no publicable"):
        service.submit_review(
            snapshot.workflow.run_id,
            object_type="claim",
            object_id=blocked.claim_id,
            decision="approved",
            reviewer="operador-local",
            reason=leaked_reason,
            expected_hash=claim_identity_hash(blocked),
        )
    assert not any(
        review.object_id == blocked.claim_id
        for review in service.get_run(snapshot.workflow.run_id).reviews
    )
    leaked_review = with_content_hash(
        ReviewDecision(
            decision_id="rev_excluded_claim",
            object_type="claim",
            object_id=blocked.claim_id,
            decision=ReviewVerdict.APPROVED,
            reviewer="operador-local",
            reason=leaked_reason,
            decided_at=datetime.now(UTC),
            approved_hash=claim_identity_hash(blocked),
            content_hash="0" * 64,
        )
    )
    service.store.save_review(snapshot.workflow.run_id, leaked_review.model_dump(mode="json"))
    assert any(
        review.object_id == blocked.claim_id
        for review in service.get_run(snapshot.workflow.run_id).reviews
    )
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    staged = service.build_release(snapshot.workflow.run_id)
    review_text = (
        service.settings.staging_dir / staged.workflow.run_id / "review-decisions.jsonl"
    ).read_text(encoding="utf-8")

    assert blocked.claim_id not in review_text
    assert leaked_reason not in review_text


def test_staging_regenerates_knowledge_instead_of_trusting_caller_markdown(
    service: CuratorService, corpus, tmp_path
) -> None:
    snapshot = service.start_audit(corpus, as_of=date(2026, 8, 31))
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    snapshot = service.get_run(snapshot.workflow.run_id)
    drafts = drafts_from_claims(snapshot.claims)
    discovery = next(draft for draft in drafts if draft.topic == "discovery")
    caller_only_fragment = "FRAGMENTO_RESTRINGIDO_INYECTADO_POR_CALLER_849273"
    malicious = with_content_hash(
        discovery.model_copy(
            update={
                "markdown": f"{discovery.markdown}\n{caller_only_fragment}\n",
                "content_hash": "0" * 64,
            }
        )
    )
    drafts = [malicious if draft.topic == discovery.topic else draft for draft in drafts]
    candidate_diff = {
        "previous_release_id": None,
        "included_claim_ids": [],
        "excluded_claim_ids": [],
        "source_count": len(snapshot.sources),
        "conflict_count": len(snapshot.conflicts),
    }

    folder = build_staging(
        tmp_path / "staging",
        snapshot.workflow.run_id,
        candidate_id="can_untrusted_draft",
        candidate_diff=candidate_diff,
        sources=snapshot.sources,
        claims=snapshot.claims,
        conflicts=snapshot.conflicts,
        reviews=snapshot.reviews,
        drafts=drafts,
        metrics=snapshot.metrics,
        domain=snapshot.domain,
        as_of=snapshot.as_of,
        model_versions={"extractor": "deterministic-frontmatter-v1", "llm": "none"},
    )
    knowledge_text = "\n".join(
        path.read_text(encoding="utf-8") for path in (folder / "knowledge").glob("*.md")
    )

    assert caller_only_fragment not in knowledge_text
    assert "El vendedor debe preguntar presupuesto" in knowledge_text


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ("stale", "review stale o no aprobada"),
        ("extra", "review de claim no incluido"),
        ("missing", "claim sin aprobación exacta"),
    ],
)
def test_autonomous_staging_validation_rejects_nonmatching_claim_reviews(
    service: CuratorService,
    corpus,
    mutation: str,
    expected_error: str,
) -> None:
    staged = _stage(service, corpus)
    folder = service.settings.staging_dir / staged.workflow.run_id
    review_path = folder / "review-decisions.jsonl"
    reviews = [
        ReviewDecision.model_validate_json(line)
        for line in review_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    target = reviews[0]
    if mutation == "stale":
        reviews.append(
            with_content_hash(
                target.model_copy(update={"approved_hash": "0" * 64, "content_hash": "0" * 64})
            )
        )
    elif mutation == "extra":
        reviews.append(
            with_content_hash(
                target.model_copy(
                    update={
                        "decision_id": "rev_excluded_claim",
                        "object_id": "clm-rights-blocked",
                        "content_hash": "0" * 64,
                    }
                )
            )
        )
    else:
        reviews = [review for review in reviews if review.object_id != target.object_id]
    review_text = "".join(
        json.dumps(
            review.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for review in reviews
    )
    review_path.write_text(review_text, encoding="utf-8", newline="\n")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["file_hashes"]["review-decisions.jsonl"] = sha256_text(review_text)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    assert any(expected_error in error for error in validate_staging(folder))


def test_staging_excludes_mixed_evidence_instead_of_changing_approved_identity(
    service: CuratorService, corpus, tmp_path
) -> None:
    snapshot = service.start_audit(corpus, as_of=date(2026, 8, 31))
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    snapshot = service.get_run(snapshot.workflow.run_id)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    assert {link.source_id for link in claim.evidence} == {
        "src-current-discovery",
        "src-syndicated-discovery",
    }
    sources = [
        with_content_hash(source.model_copy(update={"redistribution_allowed": False}))
        if source.source_id == "src-syndicated-discovery"
        else source
        for source in snapshot.sources
    ]
    candidate_diff = {
        "previous_release_id": None,
        "included_claim_ids": sorted(
            item.claim_id for item in snapshot.claims if item.status == ClaimStatus.HUMAN_APPROVED
        ),
        "excluded_claim_ids": sorted(
            item.claim_id for item in snapshot.claims if item.status != ClaimStatus.HUMAN_APPROVED
        ),
        "source_count": len(sources),
        "conflict_count": len(snapshot.conflicts),
    }

    folder = build_staging(
        tmp_path / "staging",
        snapshot.workflow.run_id,
        candidate_id="can_rights_filter",
        candidate_diff=candidate_diff,
        sources=sources,
        claims=snapshot.claims,
        conflicts=snapshot.conflicts,
        reviews=snapshot.reviews,
        drafts=drafts_from_claims(snapshot.claims),
        metrics=snapshot.metrics,
        domain=snapshot.domain,
        as_of=snapshot.as_of,
        model_versions={"extractor": "deterministic-frontmatter-v1", "llm": "none"},
    )
    exported = [
        json.loads(line)
        for line in (folder / "claims.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert claim.claim_id not in {row["claim_id"] for row in exported}
    assert claim.claim_id in candidate_diff["excluded_claim_ids"]


def test_publish_marks_only_claims_present_in_the_approved_package(
    service: CuratorService, corpus
) -> None:
    snapshot = service.start_audit(corpus, as_of=date(2026, 8, 31))
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    snapshot = service.get_run(snapshot.workflow.run_id)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    for source in snapshot.sources:
        if any(link.source_id == source.source_id for link in claim.evidence):
            restricted = with_content_hash(
                source.model_copy(
                    update={"redistribution_allowed": False, "content_hash": "0" * 64}
                )
            )
            service.store.save_source(snapshot.workflow.run_id, restricted.model_dump(mode="json"))

    staged = service.build_release(snapshot.workflow.run_id)
    assert claim.claim_id in staged.candidate_diff["excluded_claim_ids"]
    _approve_candidate(service, staged)
    published = service.publish_release(staged.workflow.run_id)

    excluded_claim = next(item for item in published.claims if item.claim_id == claim.claim_id)
    assert excluded_claim.status == ClaimStatus.HUMAN_APPROVED
    release = service.validate_release(published.release_id)
    assert claim.claim_id not in release["included"]
    assert claim.claim_id in release["excluded"]


def test_publish_requires_a_later_exact_candidate_approval(service: CuratorService, corpus) -> None:
    staged = _stage(service, corpus)

    with pytest.raises(ReleaseError, match="aprobación"):
        service.publish_release(staged.workflow.run_id)
    assert service.get_run(staged.workflow.run_id).workflow.state == WorkflowStatus.STAGING
    assert read_current(service.settings.releases_dir) is None

    _approve_candidate(service, staged)
    published = service.publish_release(staged.workflow.run_id)
    assert published.workflow.state == WorkflowStatus.PUBLISHED
    assert read_current(service.settings.releases_dir)["release_id"] == published.release_id


def test_candidate_review_rejects_wrong_id_or_hash(service: CuratorService, corpus) -> None:
    staged = _stage(service, corpus)
    with pytest.raises(ValueError, match="candidato"):
        service.submit_review(
            staged.workflow.run_id,
            object_type="release_candidate",
            object_id="can_wrong_candidate",
            decision="approved",
            reviewer="operador-local",
            reason="Intento con identidad de candidato incorrecta",
            expected_hash=staged.candidate_hash,
        )
    with pytest.raises(ValueError, match="hash"):
        service.submit_review(
            staged.workflow.run_id,
            object_type="release_candidate",
            object_id=staged.candidate_id,
            decision="approved",
            reviewer="operador-local",
            reason="Intento con hash de candidato anterior",
            expected_hash="0" * 64,
        )


def test_unapproved_claim_stays_out_of_release(service: CuratorService, corpus) -> None:
    _, _, snapshot = _publish(service, corpus)
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
        service.build_release(snapshot.workflow.run_id)
    assert read_current(service.settings.releases_dir) is None


def test_publish_detects_candidate_tampering_after_approval(
    service: CuratorService, corpus
) -> None:
    staged = _stage(service, corpus)
    _approve_candidate(service, staged)
    manifest = service.settings.staging_dir / staged.workflow.run_id / "manifest.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(ReleaseError, match="hash"):
        service.publish_release(staged.workflow.run_id)
    assert read_current(service.settings.releases_dir) is None


def test_publish_and_rollback(service: CuratorService, corpus) -> None:
    _, _, first = _publish(service, corpus)
    first_id = first.release_id
    _, _, second = _publish(service, corpus)
    assert read_current(service.settings.releases_dir)["release_id"] == second.release_id
    service.rollback_release(first_id)
    assert read_current(service.settings.releases_dir)["release_id"] == first_id
    assert (service.settings.releases_dir / second.release_id).is_dir()


def test_published_package_is_autonomous_and_contains_candidate_approval(
    service: CuratorService, corpus, monkeypatch
) -> None:
    staged, approval, published = _publish(service, corpus)
    folder = service.settings.releases_dir / published.release_id
    release_payload = json.loads((folder / "knowledge-release.json").read_text(encoding="utf-8"))
    approval_payload = json.loads((folder / "candidate-approval.json").read_text(encoding="utf-8"))

    assert release_payload["domain"] == "sales-books-school"
    assert release_payload["as_of"] == "2026-08-31"
    assert release_payload["manifest_hash"] == staged.candidate_hash
    assert approval_payload["decision_id"] == approval.decision_id
    assert approval_payload["object_id"] == staged.candidate_id
    assert approval_payload["approved_hash"] == staged.candidate_hash
    assert approval.decision_id in release_payload["approval_ids"]

    def sqlite_must_not_be_used(*_args, **_kwargs):
        raise AssertionError("validate_release no debe consultar SQLite")

    monkeypatch.setattr(service.store, "get_release", sqlite_must_not_be_used)
    monkeypatch.setattr(service.store, "list_runs", sqlite_must_not_be_used)
    report = service.validate_release(published.release_id)
    assert report["valid"] is True
    assert report["domain"] == "sales-books-school"


@pytest.mark.parametrize(
    ("relative", "expected_error"),
    [
        ("knowledge/README.md", "hash alterado"),
        ("manifest.json", "hash del manifest"),
        ("knowledge-release.json", "content_hash"),
    ],
)
def test_validate_release_detects_package_manipulation(
    service: CuratorService, corpus, relative: str, expected_error: str
) -> None:
    _, _, published = _publish(service, corpus)
    target = service.settings.releases_dir / published.release_id / relative
    if relative.endswith(".json"):
        payload = json.loads(target.read_text(encoding="utf-8"))
        if relative == "knowledge-release.json":
            payload["domain"] = "tampered-domain"
        else:
            payload["tampered"] = True
        target.write_text(json.dumps(payload), encoding="utf-8")
    else:
        target.write_text(target.read_text(encoding="utf-8") + "alterado\n", encoding="utf-8")

    report = service.validate_release(published.release_id)
    assert report["valid"] is False
    assert any(expected_error in error for error in report["errors"])


def test_identity_hash_changes_when_text_changes(service: CuratorService, corpus) -> None:
    snapshot = service.start_audit(corpus)
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ask-budget")
    original = claim_identity_hash(claim)
    mutated = claim.model_copy(update={"canonical_text": claim.canonical_text + " extra"})
    assert claim_identity_hash(mutated) != original


def test_export_jsonl_after_explicit_publish(service: CuratorService, corpus) -> None:
    _, _, snapshot = _publish(service, corpus)
    path = service.export_run(snapshot.workflow.run_id)
    summary = validate_run(path)
    assert summary["terminal_event"] == "run.completed"
    text = path.read_text(encoding="utf-8")
    assert "Ignore previous instructions" not in text
    assert "@" not in text or "payload" in text

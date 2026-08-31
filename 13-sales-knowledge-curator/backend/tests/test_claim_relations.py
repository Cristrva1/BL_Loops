from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from sales_curator.contracts.models import ClaimStatus
from sales_curator.domain.extract import extract_from_source
from sales_curator.domain.ingest import ingest_file
from sales_curator.domain.verify import detect_conflicts, supersede_outdated
from sales_curator.orchestration.service import CuratorService


def test_claim_header_parses_typed_conflict_and_supersession_relations(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "relations.md"
    source_path.write_text(
        """---
source_id: src-relations
title: Relaciones editoriales
author: Equipo de prueba
published_at: 2026-01-01
updated_at: 2026-01-01
license: CC-BY-4.0
usage_basis: synthetic_fixture
redistribution_allowed: true
language: es
jurisdiction: MX-demo
origin_source_id: src-relations
independence: original
rights_clarity: 4
topics: closing
---

CLAIM:id=clm-current;type=prescriptive;topic=closing;valid_from=2026-01-01;supersedes=clm-old;conflicts_with=clm-opposite,clm-qualified
Esta afirmación actual reemplaza una versión antigua y declara sus conflictos explícitos.
ENDCLAIM
""",
        encoding="utf-8",
    )
    ingested = ingest_file(
        source_path,
        allowed_root=tmp_path,
        max_bytes=20_000,
        retrieved_at=datetime.now(UTC),
        lab=tmp_path,
    )

    [candidate] = extract_from_source(ingested)

    assert candidate.supersedes == "clm-old"
    assert candidate.conflicts_with == ["clm-opposite", "clm-qualified"]


def test_demo_conflict_is_declared_reciprocally(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    early = next(item for item in snapshot.claims if item.claim_id == "clm-price-first-contact")
    late = next(item for item in snapshot.claims if item.claim_id == "clm-price-after-discovery")

    assert early.conflicts_with == [late.claim_id]
    assert late.conflicts_with == [early.claim_id]
    assert [set(item.claim_ids) for item in snapshot.conflicts] == [{early.claim_id, late.claim_id}]


def test_compatible_claims_do_not_conflict_only_for_sharing_a_topic(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    original = next(item for item in snapshot.claims if item.claim_id == "clm-price-first-contact")
    compatible = original.model_copy(
        update={
            "claim_id": "clm-price-context-note",
            "canonical_text": (
                "El vendedor puede registrar el contexto del comprador antes de hablar de precio."
            ),
        }
    )

    assert detect_conflicts([original, compatible]) == []


def test_one_sided_conflict_declaration_is_not_enough(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    early = next(item for item in snapshot.claims if item.claim_id == "clm-price-first-contact")
    late = next(item for item in snapshot.claims if item.claim_id == "clm-price-after-discovery")
    one_sided = late.model_copy(update={"conflicts_with": []})

    assert detect_conflicts([early, one_sided]) == []


def test_outdated_claim_is_not_superseded_by_an_unrelated_same_topic_claim(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    outdated = next(
        item for item in snapshot.claims if item.claim_id == "clm-always-be-closing"
    ).model_copy(update={"status": ClaimStatus.OUTDATED, "supersedes": None})
    anecdote = next(
        item for item in snapshot.claims if item.claim_id == "clm-sunday-close"
    ).model_copy(update={"status": ClaimStatus.SUPPORTED_SINGLE_SOURCE, "supersedes": None})

    updated = {item.claim_id: item for item in supersede_outdated([outdated, anecdote])}

    assert updated[outdated.claim_id].status == ClaimStatus.OUTDATED
    assert updated[anecdote.claim_id].supersedes is None


def test_explicit_supersession_requires_a_non_overlapping_newer_validity(
    service: CuratorService,
    corpus,
) -> None:
    snapshot = service.start_audit(corpus)
    outdated = next(
        item for item in snapshot.claims if item.claim_id == "clm-always-be-closing"
    ).model_copy(update={"status": ClaimStatus.OUTDATED, "supersedes": None})
    template = next(item for item in snapshot.claims if item.claim_id == "clm-sunday-close")
    coherent = template.model_copy(
        update={
            "claim_id": "clm-current-closing",
            "status": ClaimStatus.SUPPORTED_SINGLE_SOURCE,
            "valid_from": date(2026, 1, 1),
            "valid_until": None,
            "supersedes": outdated.claim_id,
        }
    )
    overlapping = coherent.model_copy(
        update={"claim_id": "clm-overlapping-closing", "valid_from": date(2019, 1, 1)}
    )

    coherent_result = {item.claim_id: item for item in supersede_outdated([outdated, coherent])}
    overlapping_result = {
        item.claim_id: item for item in supersede_outdated([outdated, overlapping])
    }

    assert coherent_result[outdated.claim_id].status == ClaimStatus.SUPERSEDED
    assert coherent_result[coherent.claim_id].supersedes == outdated.claim_id
    assert overlapping_result[outdated.claim_id].status == ClaimStatus.OUTDATED

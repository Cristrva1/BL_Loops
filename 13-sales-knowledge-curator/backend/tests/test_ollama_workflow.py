from __future__ import annotations

from pathlib import Path

import pytest

from sales_curator.agents.llm_extractor import LlmExtractError
from sales_curator.contracts.models import ClaimCandidate, ClaimType, WorkflowStatus
from sales_curator.evaluation.jsonl import validate_run
from sales_curator.orchestration.service import AuditRunFailed, CuratorService


def _literal_candidate() -> ClaimCandidate:
    return ClaimCandidate(
        claim_id="clm-ollama-literal",
        text=(
            "El vendedor debe preguntar presupuesto, plazo y restriccion familiar antes de "
            "mostrar inventario."
        ),
        claim_type=ClaimType.PRESCRIPTIVE,
        topic="discovery",
        population="compradores-de-vivienda-demo",
        context=None,
        jurisdiction="MX-demo",
        valid_from=None,
        valid_until=None,
        method=None,
        sample=None,
        conflicts_with=[],
        supersedes=None,
        locator="L24",
        source_id="src-current-discovery",
    )


def test_ollama_extractor_is_a_functional_workflow_route(monkeypatch, settings, corpus) -> None:
    seen: dict[str, object] = {"instances": 0, "calls": 0}

    class FakeExtractor:
        def __init__(self, *, base_url: str, model: str) -> None:
            seen["instances"] = int(seen["instances"]) + 1
            seen["base_url"] = base_url
            seen["model"] = model

        def extract_documents(self, documents, *, max_chunks_per_document: int):
            seen["calls"] = int(seen["calls"]) + 1
            materialized = tuple(documents)
            seen["documents"] = materialized
            seen["max_chunks"] = max_chunks_per_document
            return {
                source_id: [_literal_candidate()] if source_id == "src-current-discovery" else []
                for source_id, _text in materialized
            }

    monkeypatch.setattr("sales_curator.orchestration.service.OllamaExtractor", FakeExtractor)
    configured = settings.model_copy(
        update={"curator_model": "qwen3.5:4b", "max_llm_chunks_per_document": 5}
    )
    service = CuratorService(configured)
    try:
        snapshot = service.start_audit(corpus, extractor="ollama", domain="school-sales")
    finally:
        service.close()

    assert snapshot.workflow.state == WorkflowStatus.REVIEW_PENDING
    assert snapshot.domain == "school-sales"
    assert seen["instances"] == 1
    assert seen["calls"] == 1
    assert seen["model"] == "qwen3.5:4b"
    assert seen["max_chunks"] == 5
    assert len(seen["documents"]) == 10
    claim = next(item for item in snapshot.claims if item.claim_id == "clm-ollama-literal")
    assert claim.evidence[0].locator == "L24"
    assert claim.evidence[0].support_assessment.value == "supports"
    extraction_event = next(
        item for item in snapshot.events if item.tool == "claim_extractor" and item.result_sanitized
    )
    assert extraction_event.result_sanitized["extractor"] == "ollama"


def test_ollama_failure_persists_failed_run_and_terminal_jsonl(
    monkeypatch, settings, corpus
) -> None:
    class FailingExtractor:
        def __init__(self, *, base_url: str, model: str) -> None:
            del base_url, model

        def extract_documents(self, documents, *, max_chunks_per_document: int):
            del documents, max_chunks_per_document
            raise LlmExtractError("respuesta Ollama deliberadamente inválida")

    monkeypatch.setattr("sales_curator.orchestration.service.OllamaExtractor", FailingExtractor)
    configured = settings.model_copy(update={"curator_model": "qwen3.5:4b"})
    service = CuratorService(configured)
    try:
        with pytest.raises(AuditRunFailed, match="deliberadamente inválida") as caught:
            service.start_audit(corpus, extractor="ollama")
        failed = service.get_run(caught.value.run_id)
        jsonl_path = Path(caught.value.jsonl_path)
    finally:
        service.close()

    assert failed.workflow.state == WorkflowStatus.FAILED
    assert jsonl_path.is_file()
    summary = validate_run(jsonl_path)
    assert summary["run_id"] == failed.workflow.run_id
    assert summary["terminal_event"] == "run.failed"

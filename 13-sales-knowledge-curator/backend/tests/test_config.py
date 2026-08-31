from __future__ import annotations

import pytest
from pydantic import ValidationError

from sales_curator.config import Settings, lab_root, resolve_lab_output_root
from sales_curator.connectors.network import NetworkDisabled


def test_cloud_model_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("CURATOR_MODEL", "llama3:cloud")
    with pytest.raises(ValidationError):
        Settings()


def test_telemetry_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("TELEMETRY_ENABLED", "true")
    with pytest.raises(ValidationError):
        Settings()


def test_embeddings_are_rejected_in_this_phase(monkeypatch) -> None:
    monkeypatch.setenv("CURATOR_EMBEDDING_MODEL", "qwen3-embedding:latest")
    with pytest.raises(ValidationError):
        Settings()


def test_real_connector_and_research_settings_are_visible(monkeypatch) -> None:
    monkeypatch.setenv("BL_LOOPS_ALLOW_REAL_CONNECTORS", "true")
    monkeypatch.setenv("RESEARCH_JURISDICTION", "MX")
    monkeypatch.setenv("RESEARCH_LANGUAGES", "en,es")
    settings = Settings()
    assert settings.allow_real_connectors is True
    assert settings.research_jurisdiction == "MX"
    assert settings.research_language_list == ("en", "es")


def test_raw_pii_storage_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("BL_LOOPS_STORE_RAW_PII", "true")
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("value", ["0", "65"])
def test_llm_chunk_budget_is_bounded(monkeypatch, value: str) -> None:
    monkeypatch.setenv("MAX_LLM_CHUNKS_PER_DOCUMENT", value)
    with pytest.raises(ValidationError, match="MAX_LLM_CHUNKS_PER_DOCUMENT"):
        Settings()


def test_research_domain_is_a_valid_workflow_default(monkeypatch) -> None:
    monkeypatch.setenv("RESEARCH_DOMAIN", "school-sales")
    settings = Settings()
    assert settings.research_domain == "school-sales"
    assert settings.max_llm_chunks_per_document == 8


def test_settings_wires_max_urls_as_network_cap(monkeypatch) -> None:
    monkeypatch.setenv("NETWORK_ENABLED", "true")
    monkeypatch.setenv("BL_LOOPS_RUNTIME_NETWORK", "true")
    monkeypatch.setenv("BL_LOOPS_ALLOW_REAL_CONNECTORS", "true")
    monkeypatch.setenv("ALLOWED_DOMAINS", "openlibrary.org")
    monkeypatch.setenv("MAX_URLS_PER_RUN", "2")
    policy = Settings().network_policy()
    with pytest.raises(NetworkDisabled, match="supera"):
        policy.authorize(run_authorized=True, url_budget=3)


def test_research_output_root_cannot_escape_the_lab() -> None:
    with pytest.raises(ValueError, match="laboratorio"):
        resolve_lab_output_root(lab_root().parent / "forbidden-research-output")

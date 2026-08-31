from __future__ import annotations

import pytest
from pydantic import ValidationError

from sales_curator.config import Settings


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

from __future__ import annotations

import pytest
from prompt_agent_factory.config import Settings, configuration_scope, find_env_file
from pydantic import ValidationError


def test_workspace_env_is_discovered_without_exposing_values() -> None:
    env_file = find_env_file()

    assert env_file is not None
    assert env_file.name == ".env"
    assert configuration_scope(env_file) == "workspace"


def test_remote_ollama_is_rejected_when_runtime_network_is_false(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("BL_LOOPS_RUNTIME_NETWORK", "false")

    with pytest.raises(ValidationError, match="OLLAMA_BASE_URL debe ser local"):
        Settings()


def test_external_writes_are_rejected_in_part_one(monkeypatch) -> None:
    monkeypatch.setenv("BL_LOOPS_ALLOW_EXTERNAL_WRITES", "true")

    with pytest.raises(ValidationError, match="no admite escrituras externas"):
        Settings()

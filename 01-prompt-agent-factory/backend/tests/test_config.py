from __future__ import annotations

from pathlib import Path

import pytest
from prompt_agent_factory.config import Settings, configuration_scope, find_env_file
from pydantic import ValidationError


def _synthetic_workspace(tmp_path: Path) -> Path:
    """Crea un BL_Loops mínimo para no depender del `.env` real de la máquina."""

    workspace = tmp_path / "BL_Loops"
    lab = workspace / "01-prompt-agent-factory"
    lab.mkdir(parents=True)
    (workspace / "AGENTS.md").write_text("# Reglas sintéticas\n", encoding="utf-8")
    (workspace / ".env.example").write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")
    (workspace / "Prompts").mkdir()
    (workspace / "menu_portable").mkdir()
    return lab


def test_workspace_env_is_discovered_without_exposing_values(tmp_path: Path) -> None:
    lab = _synthetic_workspace(tmp_path)
    workspace_env = lab.parent / ".env"
    workspace_env.write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")

    env_file = find_env_file(lab)

    assert env_file == workspace_env
    assert configuration_scope(env_file, lab) == "workspace"


def test_local_env_has_priority_over_workspace_env(tmp_path: Path) -> None:
    lab = _synthetic_workspace(tmp_path)
    (lab.parent / ".env").write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")
    local_env = lab / ".env"
    local_env.write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")

    env_file = find_env_file(lab)

    assert env_file == local_env
    assert configuration_scope(env_file, lab) == "lab"


def test_env_from_a_folder_that_is_not_bl_loops_is_ignored(tmp_path: Path) -> None:
    foreign_root = tmp_path / "otra-carpeta"
    lab = foreign_root / "01-prompt-agent-factory"
    lab.mkdir(parents=True)
    foreign_env = foreign_root / ".env"
    foreign_env.write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")

    assert find_env_file(lab) != foreign_env
    assert configuration_scope(None, lab) == "defaults"


def test_remote_ollama_is_rejected_when_runtime_network_is_false(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("BL_LOOPS_RUNTIME_NETWORK", "false")

    with pytest.raises(ValidationError, match="OLLAMA_BASE_URL debe ser local"):
        Settings()


def test_external_writes_are_rejected_in_part_one(monkeypatch) -> None:
    monkeypatch.setenv("BL_LOOPS_ALLOW_EXTERNAL_WRITES", "true")

    with pytest.raises(ValidationError, match="no admite escrituras externas"):
        Settings()

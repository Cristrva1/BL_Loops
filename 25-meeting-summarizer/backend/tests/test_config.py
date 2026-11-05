from pathlib import Path

import pytest
from pydantic import ValidationError

from meeting_summarizer.config import Settings, find_env_file


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:11434",
        "http://example.com:11434",
        "http://user:secret@127.0.0.1:11434",
        "http://127.0.0.1:11434/api",
        "http://127.0.0.1",
    ],
)
def test_non_local_or_unsafe_ollama_endpoint_is_rejected(
    url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", url)

    with pytest.raises(ValidationError, match="OLLAMA_BASE_URL debe ser HTTP local"):
        Settings()


def test_cloud_model_tag_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3.5:cloud")

    with pytest.raises(ValidationError, match="modelo local, no cloud"):
        Settings()


def test_local_endpoint_is_accepted_and_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/")

    assert Settings().ollama_base_url == "http://localhost:11434"


def test_dashboard_uses_its_own_port_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRONTEND_PORT", raising=False)

    assert Settings().frontend_port == 5177


def _synthetic_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "BL_Loops"
    lab = workspace / "25-meeting-summarizer"
    lab.mkdir(parents=True)
    (workspace / "AGENTS.md").write_text("# Reglas\n", encoding="utf-8")
    (workspace / ".env.example").write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")
    (workspace / "Prompts").mkdir()
    (workspace / "menu_portable").mkdir()
    return lab


def test_workspace_env_is_used_only_inside_bl_loops(tmp_path: Path) -> None:
    lab = _synthetic_workspace(tmp_path)
    workspace_env = lab.parent / ".env"
    workspace_env.write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")

    assert find_env_file(lab) == workspace_env


def test_env_from_a_folder_that_is_not_bl_loops_is_ignored(tmp_path: Path) -> None:
    lab = tmp_path / "otra-carpeta" / "25-meeting-summarizer"
    lab.mkdir(parents=True)
    (lab.parent / ".env").write_text("BL_LOOPS_ENV=development\n", encoding="utf-8")

    assert find_env_file(lab) is None

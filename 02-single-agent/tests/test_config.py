from pathlib import Path

import pytest

from single_agent.config import ConfigurationError, Settings

RELEVANT_ENVIRONMENT = (
    "OLLAMA_BASE_URL",
    "SIMPLE_AGENT_MODEL",
    "BL_LOOPS_MODEL_ALT_STANDARD",
    "SIMPLE_AGENT_TIMEOUT_SECONDS",
    "SIMPLE_AGENT_RUNS_DIR",
    "BL_LOOPS_RUNS_DIR",
)


def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in RELEVANT_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)


def test_defaults_use_local_ollama_and_gemma4_e4b(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()

    settings = Settings.load(root)

    assert settings.base_url == "http://127.0.0.1:11434"
    assert settings.model == "gemma4:e4b"
    assert settings.runs_dir == root / ".local" / "runs"
    assert "acéptalo como contexto" in settings.system_prompt


def test_local_dotenv_overrides_parent_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    (tmp_path / ".env").write_text("SIMPLE_AGENT_MODEL=gemma4:e2b\n", encoding="utf-8")
    (root / ".env").write_text("SIMPLE_AGENT_MODEL=gemma4:e4b\n", encoding="utf-8")

    settings = Settings.load(root)

    assert settings.model == "gemma4:e4b"


@pytest.mark.parametrize(
    "base_url",
    [
        "https://127.0.0.1:11434",
        "http://example.com:11434",
        "http://user:password@127.0.0.1:11434",
        "http://127.0.0.1:11434/api",
    ],
)
def test_non_local_or_unsafe_endpoint_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    base_url: str,
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("OLLAMA_BASE_URL", base_url)

    with pytest.raises(ConfigurationError, match="HTTP local"):
        Settings.load(root)


def test_runs_directory_cannot_escape_the_lab(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("SIMPLE_AGENT_RUNS_DIR", "../outside")

    with pytest.raises(ConfigurationError, match="no puede salir"):
        Settings.load(root)


@pytest.mark.parametrize("model", ["gemma4:cloud", "gemma4:31b-cloud"])
def test_cloud_model_tag_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    model: str,
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("SIMPLE_AGENT_MODEL", model)

    with pytest.raises(ConfigurationError, match="modelo local, no cloud"):
        Settings.load(root)

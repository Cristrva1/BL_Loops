from pathlib import Path

import pytest

from parallel_agents.config import ConfigurationError, Settings

RELEVANT_ENVIRONMENT = (
    "OLLAMA_BASE_URL",
    "PARALLEL_MODEL",
    "BL_LOOPS_MODEL_BASIC",
    "PARALLEL_TIMEOUT_SECONDS",
    "PARALLEL_BRANCH_TIMEOUT_SECONDS",
    "PARALLEL_MAX_IN_FLIGHT",
    "PARALLEL_RUNS_DIR",
    "BL_LOOPS_RUNS_DIR",
    "BL_LOOPS_TELEMETRY",
    "BL_LOOPS_RUNTIME_NETWORK",
    "BL_LOOPS_ALLOW_EXTERNAL_WRITES",
)


def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in RELEVANT_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)


def test_defaults_use_local_ollama_and_qwen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()

    settings = Settings.load(root)

    assert settings.base_url == "http://127.0.0.1:11434"
    assert settings.model == "qwen3.5:4b"
    assert settings.max_in_flight == 3
    assert settings.runs_dir == root / ".local" / "runs"


def test_local_dotenv_overrides_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    (tmp_path / ".env").write_text("PARALLEL_MODEL=gemma4:e2b\n", encoding="utf-8")
    (root / ".env").write_text(
        "PARALLEL_MODEL=qwen3.5:9b\nPARALLEL_MAX_IN_FLIGHT=1\n",
        encoding="utf-8",
    )

    settings = Settings.load(root)

    assert settings.model == "qwen3.5:9b"
    assert settings.max_in_flight == 1


@pytest.mark.parametrize(
    "base_url",
    [
        "https://127.0.0.1:11434",
        "http://example.com:11434",
        "http://user:password@127.0.0.1:11434",
        "http://127.0.0.1:11434/api",
    ],
)
def test_non_local_endpoint_is_rejected(
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
    monkeypatch.setenv("PARALLEL_RUNS_DIR", "../outside")

    with pytest.raises(ConfigurationError, match="no puede salir"):
        Settings.load(root)


def test_cloud_model_tag_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("PARALLEL_MODEL", "qwen3.5:cloud")

    with pytest.raises(ConfigurationError, match="modelo local, no cloud"):
        Settings.load(root)

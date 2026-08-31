from pathlib import Path

import pytest

from naive_rag.config import ConfigurationError, Settings

RELEVANT_ENVIRONMENT = (
    "OLLAMA_BASE_URL",
    "NAIVE_RAG_MODEL",
    "BL_LOOPS_MODEL_BASIC",
    "NAIVE_RAG_TIMEOUT_SECONDS",
    "NAIVE_RAG_INDEX_PATH",
    "NAIVE_RAG_RUNS_DIR",
    "NAIVE_RAG_TOP_K",
    "NAIVE_RAG_CHUNK_CHARS",
    "BL_LOOPS_DATA_DIR",
    "BL_LOOPS_RUNS_DIR",
)


def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in RELEVANT_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)


def test_defaults_use_local_ollama_and_lab_owned_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()

    settings = Settings.load(root)

    assert settings.base_url == "http://127.0.0.1:11434"
    assert settings.model == "qwen3.5:4b"
    assert settings.index_path == root / ".local" / "data" / "books.sqlite3"
    assert settings.runs_dir == root / ".local" / "runs"
    assert settings.top_k == 4
    assert settings.chunk_chars == 1200


def test_local_dotenv_overrides_parent_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    (tmp_path / ".env").write_text("NAIVE_RAG_MODEL=qwen3.5:9b\n", encoding="utf-8")
    (root / ".env").write_text("NAIVE_RAG_MODEL=qwen3.5:4b\n", encoding="utf-8")

    assert Settings.load(root).model == "qwen3.5:4b"


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


@pytest.mark.parametrize("name", ["NAIVE_RAG_INDEX_PATH", "NAIVE_RAG_RUNS_DIR"])
def test_generated_paths_cannot_escape_the_lab(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv(name, "../outside")

    with pytest.raises(ConfigurationError, match="no puede salir"):
        Settings.load(root)


@pytest.mark.parametrize("model", ["qwen3.5:cloud", "qwen3.5:4b-cloud"])
def test_cloud_model_tag_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    model: str,
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("NAIVE_RAG_MODEL", model)

    with pytest.raises(ConfigurationError, match="modelo local, no cloud"):
        Settings.load(root)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("NAIVE_RAG_TOP_K", "0", "entre 1 y 10"),
        ("NAIVE_RAG_TOP_K", "abc", "entero"),
        ("NAIVE_RAG_CHUNK_CHARS", "399", "entre 400 y 4000"),
    ],
)
def test_numeric_limits_are_explained(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
    message: str,
) -> None:
    _clean_environment(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv(name, value)

    with pytest.raises(ConfigurationError, match=message):
        Settings.load(root)

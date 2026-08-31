from pathlib import Path

import pytest

from vector_rag.config import ConfigurationError, Settings

NAMES = (
    "OLLAMA_BASE_URL",
    "VECTOR_RAG_CHAT_MODEL",
    "VECTOR_RAG_EMBEDDING_MODEL",
    "BL_LOOPS_MODEL_BASIC",
    "BL_LOOPS_EMBEDDING_MODEL",
    "VECTOR_RAG_EMBEDDING_DIMENSIONS",
    "VECTOR_RAG_EMBEDDING_BATCH_SIZE",
    "VECTOR_RAG_TIMEOUT_SECONDS",
    "VECTOR_RAG_INDEX_PATH",
    "VECTOR_RAG_RUNS_DIR",
    "VECTOR_RAG_TOP_K",
    "VECTOR_RAG_CHUNK_CHARS",
    "VECTOR_RAG_MODE",
    "BL_LOOPS_DATA_DIR",
    "BL_LOOPS_RUNS_DIR",
)


def _clean(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in NAMES:
        monkeypatch.delenv(name, raising=False)


def test_defaults_are_local_hybrid_and_lab_owned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()

    settings = Settings.load(root)

    assert settings.base_url == "http://127.0.0.1:11434"
    assert settings.chat_model == "qwen3.5:4b"
    assert settings.embedding_model == "qwen3-embedding:latest"
    assert settings.embedding_dimensions == 768
    assert settings.embedding_batch_size == 16
    assert settings.retrieval_mode == "hybrid"
    assert settings.index_path == root / ".local" / "data" / "books-hybrid.sqlite3"


@pytest.mark.parametrize(
    "url",
    ["https://127.0.0.1:11434", "http://example.com:11434", "http://127.0.0.1/api"],
)
def test_endpoint_must_be_local_http_with_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("OLLAMA_BASE_URL", url)

    with pytest.raises(ConfigurationError, match="HTTP local"):
        Settings.load(root)


@pytest.mark.parametrize("name", ["VECTOR_RAG_INDEX_PATH", "VECTOR_RAG_RUNS_DIR"])
def test_generated_paths_cannot_escape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv(name, "../outside")

    with pytest.raises(ConfigurationError, match="no puede salir"):
        Settings.load(root)


@pytest.mark.parametrize("name", ["VECTOR_RAG_CHAT_MODEL", "VECTOR_RAG_EMBEDDING_MODEL"])
def test_cloud_models_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv(name, "modelo:cloud")

    with pytest.raises(ConfigurationError, match="local, no cloud"):
        Settings.load(root)


@pytest.mark.parametrize("mode", ["lexical", "vector", "hybrid"])
def test_supported_modes_are_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("VECTOR_RAG_MODE", mode)

    assert Settings.load(root).retrieval_mode == mode


def test_unknown_mode_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clean(monkeypatch)
    root = tmp_path / "lab"
    root.mkdir()
    monkeypatch.setenv("VECTOR_RAG_MODE", "magic")

    with pytest.raises(ConfigurationError, match="lexical, vector o hybrid"):
        Settings.load(root)

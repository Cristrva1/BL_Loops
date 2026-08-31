"""Configuracion portable para chat, embeddings e indice local."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_CHAT_MODEL = "qwen3.5:4b"
DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:latest"
DEFAULT_DIMENSIONS = 768
DEFAULT_BATCH_SIZE = 16
DEFAULT_TIMEOUT = 300.0
DEFAULT_INDEX_PATH = ".local/data/books-hybrid.sqlite3"
DEFAULT_RUNS_DIR = ".local/runs"
DEFAULT_TOP_K = 5
DEFAULT_CHUNK_CHARS = 1200
SUPPORTED_MODES = frozenset({"lexical", "vector", "hybrid"})
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class ConfigurationError(ValueError):
    """La configuracion viola los limites locales del laboratorio."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def _environment(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    values.update(_read_dotenv(root.parent / ".env"))
    values.update(_read_dotenv(root / ".env"))
    values.update(os.environ)
    return values


def _local_url(value: str) -> str:
    candidate = value.rstrip("/")
    parsed = urlparse(candidate)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("OLLAMA_BASE_URL contiene un puerto invalido.") from exc
    if (
        parsed.scheme != "http"
        or parsed.hostname not in LOCAL_HOSTS
        or port is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise ConfigurationError(
            "OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434."
        )
    return candidate


def _model(value: str, name: str) -> str:
    model = value.strip()
    if not model:
        raise ConfigurationError(f"{name} no puede estar vacio.")
    tag = model.casefold().rsplit(":", 1)[-1]
    if tag == "cloud" or tag.endswith("-cloud"):
        raise ConfigurationError(f"{name} debe usar un modelo local, no cloud.")
    return model


def _lab_path(root: Path, value: str, name: str) -> Path:
    configured = Path(value)
    if configured.is_absolute():
        raise ConfigurationError(f"{name} debe ser relativa al laboratorio.")
    resolved = (root / configured).resolve()
    if not resolved.is_relative_to(root):
        raise ConfigurationError(f"{name} no puede salir de la raiz del laboratorio.")
    return resolved


def _integer(env: dict[str, str], name: str, default: int, low: int, high: int) -> int:
    try:
        value = int(env.get(name, str(default)).strip())
    except ValueError as exc:
        raise ConfigurationError(f"{name} debe ser un entero.") from exc
    if not low <= value <= high:
        raise ConfigurationError(f"{name} debe estar entre {low} y {high}.")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    root: Path
    base_url: str
    chat_model: str
    embedding_model: str
    embedding_dimensions: int
    embedding_batch_size: int
    timeout_seconds: float
    index_path: Path
    runs_dir: Path
    top_k: int
    chunk_chars: int
    retrieval_mode: str

    @classmethod
    def load(cls, root: Path | None = None) -> Settings:
        actual_root = (root or project_root()).resolve()
        env = _environment(actual_root)
        raw_embedding_model = env.get("VECTOR_RAG_EMBEDDING_MODEL") or env.get(
            "BL_LOOPS_EMBEDDING_MODEL"
        )
        embedding_model = _model(
            raw_embedding_model or DEFAULT_EMBEDDING_MODEL,
            "VECTOR_RAG_EMBEDDING_MODEL",
        )
        chat_model = _model(
            env.get(
                "VECTOR_RAG_CHAT_MODEL",
                env.get("BL_LOOPS_MODEL_BASIC", DEFAULT_CHAT_MODEL),
            ),
            "VECTOR_RAG_CHAT_MODEL",
        )
        try:
            timeout = float(env.get("VECTOR_RAG_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT)))
        except ValueError as exc:
            raise ConfigurationError("VECTOR_RAG_TIMEOUT_SECONDS debe ser numerico.") from exc
        if not 0 < timeout <= 1800:
            raise ConfigurationError("VECTOR_RAG_TIMEOUT_SECONDS debe estar entre 0 y 1800.")

        raw_index = env.get("VECTOR_RAG_INDEX_PATH")
        if raw_index is None:
            raw_index = str(
                Path(env.get("BL_LOOPS_DATA_DIR", ".local/data")) / "books-hybrid.sqlite3"
            )
        mode = env.get("VECTOR_RAG_MODE", "hybrid").strip().casefold()
        if mode not in SUPPORTED_MODES:
            raise ConfigurationError("VECTOR_RAG_MODE debe ser lexical, vector o hybrid.")
        return cls(
            root=actual_root,
            base_url=_local_url(env.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).strip()),
            chat_model=chat_model,
            embedding_model=embedding_model,
            embedding_dimensions=_integer(
                env, "VECTOR_RAG_EMBEDDING_DIMENSIONS", DEFAULT_DIMENSIONS, 32, 4096
            ),
            embedding_batch_size=_integer(
                env, "VECTOR_RAG_EMBEDDING_BATCH_SIZE", DEFAULT_BATCH_SIZE, 1, 64
            ),
            timeout_seconds=timeout,
            index_path=_lab_path(
                actual_root, raw_index.strip() or DEFAULT_INDEX_PATH, "VECTOR_RAG_INDEX_PATH"
            ),
            runs_dir=_lab_path(
                actual_root,
                env.get("VECTOR_RAG_RUNS_DIR", env.get("BL_LOOPS_RUNS_DIR", DEFAULT_RUNS_DIR)),
                "VECTOR_RAG_RUNS_DIR",
            ),
            top_k=_integer(env, "VECTOR_RAG_TOP_K", DEFAULT_TOP_K, 1, 12),
            chunk_chars=_integer(env, "VECTOR_RAG_CHUNK_CHARS", DEFAULT_CHUNK_CHARS, 400, 4000),
            retrieval_mode=mode,
        )

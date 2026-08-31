"""Configuracion pequena, portable y cerrada a Ollama local."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_MODEL = "qwen3.5:4b"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT_SECONDS = 300.0
DEFAULT_INDEX_PATH = ".local/data/books.sqlite3"
DEFAULT_RUNS_DIR = ".local/runs"
DEFAULT_TOP_K = 4
DEFAULT_CHUNK_CHARS = 1200
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class ConfigurationError(ValueError):
    """La configuracion no cumple el contrato local del laboratorio."""


def project_root() -> Path:
    """Devuelve la raiz del laboratorio aunque el comando parta de otro cwd."""

    return Path(__file__).resolve().parents[2]


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def _load_environment(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    values.update(_read_dotenv(root.parent / ".env"))
    values.update(_read_dotenv(root / ".env"))
    values.update(os.environ)
    return values


def _validate_local_base_url(value: str) -> str:
    candidate = value.rstrip("/")
    parsed = urlparse(candidate)
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("OLLAMA_BASE_URL contiene un puerto invalido.") from exc

    if (
        parsed.scheme != "http"
        or parsed.hostname not in LOCAL_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.params
        or parsed.query
        or parsed.fragment
        or parsed_port is None
    ):
        raise ConfigurationError(
            "OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434."
        )
    return candidate


def _validate_model(value: str) -> str:
    model = value.strip()
    if not model:
        raise ConfigurationError("NAIVE_RAG_MODEL no puede estar vacio.")
    tag = model.casefold().rsplit(":", 1)[-1]
    if tag == "cloud" or tag.endswith("-cloud"):
        raise ConfigurationError("NAIVE_RAG_MODEL debe referirse a un modelo local, no cloud.")
    return model


def _resolve_lab_path(root: Path, value: str, name: str) -> Path:
    configured = Path(value)
    if configured.is_absolute():
        raise ConfigurationError(f"{name} debe ser una ruta relativa al laboratorio.")
    resolved = (root / configured).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ConfigurationError(f"{name} no puede salir de la raiz del laboratorio.")
    return resolved


def _parse_int(
    environment: dict[str, str],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw_value = environment.get(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} debe ser un entero.") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} debe estar entre {minimum} y {maximum}.")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    """Valores efectivos del RAG, sin secretos ni servicios cloud."""

    root: Path
    base_url: str
    model: str
    timeout_seconds: float
    index_path: Path
    runs_dir: Path
    top_k: int
    chunk_chars: int

    @classmethod
    def load(cls, root: Path | None = None) -> Settings:
        actual_root = (root or project_root()).resolve()
        environment = _load_environment(actual_root)

        base_url = _validate_local_base_url(
            environment.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).strip()
        )
        model = _validate_model(
            environment.get(
                "NAIVE_RAG_MODEL",
                environment.get("BL_LOOPS_MODEL_BASIC", DEFAULT_MODEL),
            )
        )

        raw_timeout = environment.get("NAIVE_RAG_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError as exc:
            raise ConfigurationError("NAIVE_RAG_TIMEOUT_SECONDS debe ser numerico.") from exc
        if not 0 < timeout_seconds <= 1800:
            raise ConfigurationError(
                "NAIVE_RAG_TIMEOUT_SECONDS debe estar entre 0 y 1800 segundos."
            )

        if "NAIVE_RAG_INDEX_PATH" in environment:
            raw_index_path = environment["NAIVE_RAG_INDEX_PATH"].strip()
        else:
            data_dir = environment.get("BL_LOOPS_DATA_DIR", ".local/data").strip()
            raw_index_path = str(Path(data_dir) / "books.sqlite3")

        index_path = _resolve_lab_path(
            actual_root,
            raw_index_path or DEFAULT_INDEX_PATH,
            "NAIVE_RAG_INDEX_PATH",
        )
        runs_dir = _resolve_lab_path(
            actual_root,
            environment.get(
                "NAIVE_RAG_RUNS_DIR",
                environment.get("BL_LOOPS_RUNS_DIR", DEFAULT_RUNS_DIR),
            ).strip(),
            "NAIVE_RAG_RUNS_DIR",
        )
        top_k = _parse_int(environment, "NAIVE_RAG_TOP_K", DEFAULT_TOP_K, 1, 10)
        chunk_chars = _parse_int(
            environment,
            "NAIVE_RAG_CHUNK_CHARS",
            DEFAULT_CHUNK_CHARS,
            400,
            4000,
        )

        return cls(
            root=actual_root,
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            index_path=index_path,
            runs_dir=runs_dir,
            top_k=top_k,
            chunk_chars=chunk_chars,
        )

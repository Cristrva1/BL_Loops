"""Configuración pequeña, portable y cerrada a endpoints locales.

Estrategia de **fusión por clave**: se lee el `.env` de la raíz de BL_Loops, después el `.env` del
laboratorio (gana clave a clave) y, por último, las variables del proceso (ganan siempre).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8022


class ConfigurationError(ValueError):
    """La configuración no cumple el contrato local del laboratorio."""


def lab_root() -> Path:
    """Raíz del laboratorio aunque el comando se lance desde otra carpeta."""

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
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def load_environment(root: Path | None = None) -> dict[str, str]:
    base = root or lab_root()
    values: dict[str, str] = {}
    values.update(_read_dotenv(base.parent / ".env"))
    values.update(_read_dotenv(base / ".env"))
    values.update(os.environ)
    return values


def validate_base_url(value: str) -> str:
    candidate = value.strip().rstrip("/")
    parsed = urlparse(candidate)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("OLLAMA_BASE_URL contiene un puerto inválido.") from exc
    if (
        parsed.scheme != "http"
        or parsed.hostname not in LOCAL_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or port is None
    ):
        raise ConfigurationError(
            "OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434."
        )
    return candidate


def validate_model(value: str) -> str:
    model = value.strip()
    tag = model.casefold().rsplit(":", 1)[-1]
    if not model or tag == "cloud" or tag.endswith("-cloud"):
        raise ConfigurationError(
            "El modelo debe ser local, no cloud: revisa OLLAMA_MODEL o el campo model."
        )
    return model


@dataclass(frozen=True, slots=True)
class Settings:
    """Valores efectivos del estudio, sin secretos ni servicios cloud."""

    ollama_base_url: str
    ollama_model: str
    host: str
    port: int

    @classmethod
    def load(cls, root: Path | None = None) -> Settings:
        env = load_environment(root)
        host = env.get("HOST", DEFAULT_HOST).strip()
        if host not in LOCAL_HOSTS:
            raise ConfigurationError("HOST debe ser 127.0.0.1, localhost o ::1.")
        try:
            port = int(env.get("PORT", str(DEFAULT_PORT)))
        except ValueError as exc:
            raise ConfigurationError("PORT debe ser un número entero.") from exc
        if not 1024 <= port <= 65535:
            raise ConfigurationError("PORT debe estar entre 1024 y 65535.")
        model = env.get("OLLAMA_MODEL") or env.get("BL_LOOPS_MODEL_STANDARD") or DEFAULT_MODEL
        return cls(
            ollama_base_url=validate_base_url(env.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL)),
            ollama_model=validate_model(model),
            host=host,
            port=port,
        )

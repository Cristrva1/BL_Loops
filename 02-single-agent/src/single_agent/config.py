"""Configuracion pequena, portable y cerrada a endpoints locales."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_MODEL = "gemma4:e4b"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT_SECONDS = 300.0
DEFAULT_SYSTEM_PROMPT = (
    "Eres un asistente de IA local, util y conversacional. "
    "Responde con claridad, de forma congruente y en el idioma del usuario. "
    "Mantén el contexto de los turnos anteriores. Cuando el usuario defina una clave, "
    "un color o cualquier dato para esta conversación, acéptalo como contexto y recuérdalo."
)
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class ConfigurationError(ValueError):
    """La configuracion no cumple el contrato local del laboratorio."""


def project_root() -> Path:
    """Devuelve la raiz del laboratorio incluso si el comando parte de otro cwd."""

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
    # Dentro de BL_Loops, la configuracion compartida vive un nivel arriba.
    values.update(_read_dotenv(root.parent / ".env"))
    # Al copiar el laboratorio, el .env local es autosuficiente y tiene prioridad.
    values.update(_read_dotenv(root / ".env"))
    # Las variables explicitas del proceso siempre tienen la maxima prioridad.
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


def _resolve_runs_dir(root: Path, value: str) -> Path:
    configured = Path(value)
    if configured.is_absolute():
        raise ConfigurationError("SIMPLE_AGENT_RUNS_DIR debe ser una ruta relativa al laboratorio.")
    resolved = (root / configured).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ConfigurationError("SIMPLE_AGENT_RUNS_DIR no puede salir de la raiz del laboratorio.")
    return resolved


def _validate_model(value: str) -> str:
    model = value.strip()
    if not model:
        raise ConfigurationError("SIMPLE_AGENT_MODEL no puede estar vacio.")
    tag = model.casefold().rsplit(":", 1)[-1]
    if tag == "cloud" or tag.endswith("-cloud"):
        raise ConfigurationError("SIMPLE_AGENT_MODEL debe referirse a un modelo local, no cloud.")
    return model


@dataclass(frozen=True, slots=True)
class Settings:
    """Valores efectivos que necesita el chat, sin secretos ni servicios cloud."""

    root: Path
    base_url: str
    model: str
    timeout_seconds: float
    runs_dir: Path
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    @classmethod
    def load(cls, root: Path | None = None) -> Settings:
        actual_root = (root or project_root()).resolve()
        environment = _load_environment(actual_root)

        base_url = _validate_local_base_url(
            environment.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).strip()
        )
        model = _validate_model(
            environment.get(
                "SIMPLE_AGENT_MODEL",
                environment.get("BL_LOOPS_MODEL_ALT_STANDARD", DEFAULT_MODEL),
            )
        )

        raw_timeout = environment.get("SIMPLE_AGENT_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError as exc:
            raise ConfigurationError("SIMPLE_AGENT_TIMEOUT_SECONDS debe ser numerico.") from exc
        if not 0 < timeout_seconds <= 1800:
            raise ConfigurationError(
                "SIMPLE_AGENT_TIMEOUT_SECONDS debe estar entre 0 y 1800 segundos."
            )

        runs_dir = _resolve_runs_dir(
            actual_root,
            environment.get(
                "SIMPLE_AGENT_RUNS_DIR",
                environment.get("BL_LOOPS_RUNS_DIR", ".local/runs"),
            ).strip(),
        )
        return cls(
            root=actual_root,
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            runs_dir=runs_dir,
        )

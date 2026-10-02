"""Configuracion portable y cerrada a endpoints locales."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_MODEL = "qwen3.5:4b"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT_SECONDS = 180.0
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class ConfigurationError(ValueError):
    """La configuracion no cumple el contrato local del laboratorio."""


def lab_root() -> Path:
    return Path(__file__).resolve().parents[3]


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


def _resolve_inside_lab(root: Path, value: str, name: str) -> Path:
    configured = Path(value)
    if configured.is_absolute():
        raise ConfigurationError(f"{name} debe ser una ruta relativa al laboratorio.")
    resolved = (root / configured).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ConfigurationError(f"{name} no puede salir de la raiz del laboratorio.")
    return resolved


def _validate_model(value: str) -> str:
    model = value.strip()
    if not model:
        raise ConfigurationError("ORCH_MODEL no puede estar vacio.")
    tag = model.casefold().rsplit(":", 1)[-1]
    if tag == "cloud" or tag.endswith("-cloud"):
        raise ConfigurationError("ORCH_MODEL debe referirse a un modelo local, no cloud.")
    return model


@dataclass(frozen=True, slots=True)
class Settings:
    root: Path
    base_url: str
    model: str
    timeout_seconds: float
    runs_dir: Path
    artifacts_dir: Path

    @classmethod
    def load(cls, root: Path | None = None) -> Settings:
        actual_root = (root or lab_root()).resolve()
        environment = _load_environment(actual_root)

        telemetry = environment.get("BL_LOOPS_TELEMETRY", "false").strip().casefold()
        if telemetry in {"1", "true", "yes"}:
            raise ConfigurationError("La telemetria remota esta desactivada en este laboratorio.")
        if environment.get("BL_LOOPS_ALLOW_EXTERNAL_WRITES", "false").strip().casefold() in {
            "1",
            "true",
            "yes",
        }:
            raise ConfigurationError("Este laboratorio no admite escrituras externas.")

        runtime_flag = environment.get("BL_LOOPS_RUNTIME_NETWORK", "false").strip().casefold()
        runtime_network = runtime_flag in {"1", "true", "yes"}
        base_url = environment.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).strip()
        if runtime_network:
            raise ConfigurationError(
                "BL_LOOPS_RUNTIME_NETWORK=true no esta autorizado en 03-orchestration."
            )
        base_url = _validate_local_base_url(base_url)

        model = _validate_model(
            environment.get(
                "ORCH_MODEL",
                environment.get("BL_LOOPS_MODEL_BASIC", DEFAULT_MODEL),
            )
        )

        raw_timeout = environment.get("ORCH_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError as exc:
            raise ConfigurationError("ORCH_TIMEOUT_SECONDS debe ser numerico.") from exc
        if not 0 < timeout_seconds <= 1800:
            raise ConfigurationError("ORCH_TIMEOUT_SECONDS debe estar entre 0 y 1800 segundos.")

        runs_dir = _resolve_inside_lab(
            actual_root,
            environment.get(
                "ORCH_RUNS_DIR",
                environment.get("BL_LOOPS_RUNS_DIR", ".local/runs"),
            ).strip(),
            "ORCH_RUNS_DIR",
        )
        artifacts_dir = _resolve_inside_lab(actual_root, ".local/artifacts", "ORCH_ARTIFACTS_DIR")
        return cls(
            root=actual_root,
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            runs_dir=runs_dir,
            artifacts_dir=artifacts_dir,
        )

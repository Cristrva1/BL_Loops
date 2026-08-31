"""Carga segura del `.env` local o del `.env` global del workspace."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def lab_root() -> Path:
    return Path(__file__).resolve().parents[3]


def find_env_file() -> Path | None:
    """Busca un `.env` local o el del workspace BL_Loops, no uno ajeno."""

    start = lab_root()
    local_candidate = start / ".env"
    if local_candidate.is_file():
        return local_candidate

    for candidate_root in start.parents:
        is_workspace = all(
            (
                (candidate_root / "AGENTS.md").is_file(),
                (candidate_root / ".env.example").is_file(),
                (candidate_root / "Prompts").is_dir(),
                (candidate_root / "menu_portable").is_dir(),
            )
        )
        workspace_candidate = candidate_root / ".env"
        if is_workspace and workspace_candidate.is_file():
            return workspace_candidate
    return None


def configuration_scope(env_file: Path | None) -> str:
    if env_file is None:
        return "defaults"
    if env_file.parent == lab_root():
        return "lab"
    return "workspace"


class Settings(BaseSettings):
    """Solo expone configuración necesaria; nunca devuelve valores secretos."""

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_BASE_URL",
    )
    runtime_network: bool = Field(
        default=False,
        validation_alias="BL_LOOPS_RUNTIME_NETWORK",
    )
    allow_external_writes: bool = Field(
        default=False,
        validation_alias="BL_LOOPS_ALLOW_EXTERNAL_WRITES",
    )
    telemetry: bool = Field(default=False, validation_alias="BL_LOOPS_TELEMETRY")

    @model_validator(mode="after")
    def enforce_local_runtime(self) -> Settings:
        host = (urlparse(self.ollama_base_url).hostname or "").casefold()
        local_hosts = {"127.0.0.1", "localhost", "::1"}
        if not self.runtime_network and host not in local_hosts:
            raise ValueError("OLLAMA_BASE_URL debe ser local cuando BL_LOOPS_RUNTIME_NETWORK=false")
        if self.allow_external_writes:
            raise ValueError("La Parte 1 no admite escrituras externas")
        if self.telemetry:
            raise ValueError("La telemetría remota está desactivada en este laboratorio")
        return self

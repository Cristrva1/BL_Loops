"""Carga fail-closed del `.env` local o del workspace. Nunca expone secretos."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def lab_root() -> Path:
    return Path(__file__).resolve().parents[3]


def find_env_file() -> Path | None:
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
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_BASE_URL",
    )
    curator_model: str = Field(default="", validation_alias="CURATOR_MODEL")
    curator_embedding_model: str = Field(default="", validation_alias="CURATOR_EMBEDDING_MODEL")
    network_enabled: bool = Field(default=False, validation_alias="NETWORK_ENABLED")
    allowed_domains: str = Field(default="", validation_alias="ALLOWED_DOMAINS")
    max_urls_per_run: int = Field(default=0, validation_alias="MAX_URLS_PER_RUN")
    max_bytes_per_source: int = Field(default=2_000_000, validation_alias="MAX_BYTES_PER_SOURCE")
    max_research_rounds: int = Field(default=3, validation_alias="MAX_RESEARCH_ROUNDS")
    max_claim_revisions: int = Field(default=2, validation_alias="MAX_CLAIM_REVISIONS")
    telemetry_enabled: bool = Field(default=False, validation_alias="TELEMETRY_ENABLED")
    raw_content_in_run_logs: bool = Field(default=False, validation_alias="RAW_CONTENT_IN_RUN_LOGS")
    runtime_network: bool = Field(default=False, validation_alias="BL_LOOPS_RUNTIME_NETWORK")
    allow_external_writes: bool = Field(
        default=False, validation_alias="BL_LOOPS_ALLOW_EXTERNAL_WRITES"
    )
    telemetry: bool = Field(default=False, validation_alias="BL_LOOPS_TELEMETRY")
    data_dir: str = Field(default=".local/data", validation_alias="BL_LOOPS_DATA_DIR")
    runs_dir: str = Field(default=".local/runs", validation_alias="BL_LOOPS_RUNS_DIR")

    @model_validator(mode="after")
    def enforce_local_runtime(self) -> Settings:
        host = (urlparse(self.ollama_base_url).hostname or "").casefold()
        local_hosts = {"127.0.0.1", "localhost", "::1"}
        if host not in local_hosts:
            raise ValueError("OLLAMA_BASE_URL debe ser local")
        if self.allow_external_writes:
            raise ValueError("Este laboratorio no admite escrituras externas")
        if self.telemetry or self.telemetry_enabled:
            raise ValueError("La telemetría remota está desactivada")
        if self.raw_content_in_run_logs:
            raise ValueError("RAW_CONTENT_IN_RUN_LOGS debe ser false en este corte")
        if self.curator_embedding_model.strip():
            raise ValueError(
                "Los embeddings no están habilitados hasta que un experimento los justifique"
            )
        if self.max_bytes_per_source < 1:
            raise ValueError("MAX_BYTES_PER_SOURCE debe ser positivo")
        if not 1 <= self.max_research_rounds <= 8:
            raise ValueError("MAX_RESEARCH_ROUNDS debe estar entre 1 y 8")
        if not 1 <= self.max_claim_revisions <= 5:
            raise ValueError("MAX_CLAIM_REVISIONS debe estar entre 1 y 5")
        tag = self.curator_model.casefold().rsplit(":", 1)[-1] if self.curator_model else ""
        if tag == "cloud" or tag.endswith("-cloud"):
            raise ValueError("CURATOR_MODEL debe ser un modelo local, no cloud")
        return self

    def resolve_lab_path(self, relative: str, name: str) -> Path:
        configured = Path(relative)
        if configured.is_absolute():
            raise ValueError(f"{name} debe ser relativa al laboratorio")
        resolved = (lab_root() / configured).resolve()
        if not resolved.is_relative_to(lab_root()):
            raise ValueError(f"{name} no puede salir de la raíz del laboratorio")
        return resolved

    @property
    def sqlite_path(self) -> Path:
        return self.resolve_lab_path(self.data_dir, "BL_LOOPS_DATA_DIR") / "curator.sqlite"

    @property
    def staging_dir(self) -> Path:
        return self.resolve_lab_path(self.data_dir, "BL_LOOPS_DATA_DIR") / "staging"

    @property
    def releases_dir(self) -> Path:
        return self.resolve_lab_path(self.data_dir, "BL_LOOPS_DATA_DIR") / "releases"

    @property
    def runs_path(self) -> Path:
        return self.resolve_lab_path(self.runs_dir, "BL_LOOPS_RUNS_DIR")

    @property
    def allowed_domain_list(self) -> tuple[str, ...]:
        return tuple(
            part.strip().casefold() for part in self.allowed_domains.split(",") if part.strip()
        )

    def with_isolated_dirs(self, data_dir: Path, runs_dir: Path) -> Settings:
        """Usa carpetas temporales dentro del laboratorio para pruebas."""

        root = lab_root()
        if not data_dir.resolve().is_relative_to(root) or not runs_dir.resolve().is_relative_to(
            root
        ):
            raise ValueError("Las rutas de prueba deben quedar dentro del laboratorio")
        return self.model_copy(
            update={
                "data_dir": data_dir.resolve().relative_to(root).as_posix(),
                "runs_dir": runs_dir.resolve().relative_to(root).as_posix(),
            }
        )

"""Configuración local del laboratorio de resúmenes de videollamadas."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
WORKSPACE_MARKERS = ("AGENTS.md", ".env.example", "Prompts", "menu_portable")


def lab_root() -> Path:
    """Devuelve la ruta absoluta a la raíz de este laboratorio."""
    return Path(__file__).resolve().parents[3]


def find_env_file(start: Path | None = None) -> Path | None:
    """Busca primero el .env del laboratorio y después el .env raíz de BL_Loops, no uno ajeno.

    `start` permite que las pruebas usen un workspace sintético; el runtime parte de la raíz
    real del laboratorio.
    """

    root = start or lab_root()
    local_env = root / ".env"
    if local_env.is_file():
        return local_env
    workspace = root.parent
    is_workspace = all((workspace / marker).exists() for marker in WORKSPACE_MARKERS)
    repo_env = workspace / ".env"
    if is_workspace and repo_env.is_file():
        return repo_env
    return None


class Settings(BaseSettings):
    """Parámetros de configuración del laboratorio."""

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bl_loops_env: str = Field(default="development", alias="BL_LOOPS_ENV")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8025, alias="PORT")
    frontend_port: int = Field(default=5177, alias="FRONTEND_PORT")

    # Inferencia Ollama
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3.5:9b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: float = Field(default=180.0, alias="OLLAMA_TIMEOUT_SECONDS")
    ollama_num_ctx: int = Field(default=8192, alias="OLLAMA_NUM_CTX")

    # Rutas locales
    data_dir: str = Field(default=".local/data", alias="DATA_DIR")
    runs_dir: str = Field(default=".local/runs", alias="RUNS_DIR")
    logs_dir: str = Field(default=".local/logs", alias="LOGS_DIR")

    @field_validator("ollama_base_url")
    @classmethod
    def ensure_local_ollama(cls, value: str) -> str:
        """Solo se admite Ollama por HTTP en loopback: no hay fallback cloud."""

        candidate = value.strip().rstrip("/")
        parsed = urlparse(candidate)
        try:
            port = parsed.port
        except ValueError as exc:
            raise ValueError("OLLAMA_BASE_URL contiene un puerto inválido.") from exc
        if (
            parsed.scheme != "http"
            or parsed.hostname not in LOCAL_HOSTS
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or port is None
        ):
            raise ValueError(
                "OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434."
            )
        return candidate

    @field_validator("ollama_model")
    @classmethod
    def ensure_local_model(cls, value: str) -> str:
        model = value.strip()
        tag = model.casefold().rsplit(":", 1)[-1]
        if not model or tag == "cloud" or tag.endswith("-cloud"):
            raise ValueError("OLLAMA_MODEL debe referirse a un modelo local, no cloud.")
        return model

    def resolve_path(self, relative_path: str) -> Path:
        """Resuelve una ruta relativa con respecto a la raíz del laboratorio."""
        p = Path(relative_path)
        if p.is_absolute():
            return p
        return lab_root() / p

    def get_db_path(self) -> Path:
        db_dir = self.resolve_path(self.data_dir)
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "meetings.db"

    def get_runs_dir(self) -> Path:
        runs = self.resolve_path(self.runs_dir)
        runs.mkdir(parents=True, exist_ok=True)
        return runs

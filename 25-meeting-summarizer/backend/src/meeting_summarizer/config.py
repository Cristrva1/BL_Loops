"""Configuración local del laboratorio de resúmenes de videollamadas."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def lab_root() -> Path:
    """Devuelve la ruta absoluta a la raíz de este laboratorio."""
    return Path(__file__).resolve().parents[3]


def find_env_file() -> Path | None:
    """Busca primero el .env del laboratorio, luego el .env raíz de BL_Loops."""
    local_env = lab_root() / ".env"
    if local_env.exists():
        return local_env
    repo_env = lab_root().parent / ".env"
    if repo_env.exists():
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
    frontend_port: int = Field(default=5175, alias="FRONTEND_PORT")

    # Inferencia Ollama
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3.5:9b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: float = Field(default=180.0, alias="OLLAMA_TIMEOUT_SECONDS")
    ollama_num_ctx: int = Field(default=8192, alias="OLLAMA_NUM_CTX")

    # Rutas locales
    data_dir: str = Field(default=".local/data", alias="DATA_DIR")
    runs_dir: str = Field(default=".local/runs", alias="RUNS_DIR")
    logs_dir: str = Field(default=".local/logs", alias="LOGS_DIR")

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

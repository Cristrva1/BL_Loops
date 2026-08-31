"""Configuracion explicita y portable del laboratorio."""

from __future__ import annotations

import ipaddress
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

LAB_ID = "14-local-code-hermes"
VARIANT_ID = "ollama-hermes-preflight"
PREFLIGHT_CASE_ID = "F-LOCAL-CODE-004@0.1.0"
BENCHMARK_CASE_ID = "B-CODE-003@0.1.0"
SCHEMA_VERSION = "1.1"
MODEL_NAME = "local-code-9b-64k"
SOURCE_MODEL = "qwen3.5:9b"
NUM_CTX = 65_536
REQUIRED_GATE_IDS = (
    "python.runtime",
    "network.endpoint",
    "network.firewall",
    "ollama.server_profile",
    "ollama.model",
    "hermes.available",
    "lmstudio.conflict",
    "git.head",
    "resource.ram",
    "resource.vram",
)
LAB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_DIR = LAB_ROOT / ".local" / "runs"

RunMode = Literal["formal", "exploratory"]
NetworkProof = Literal["unverified", "firewall-authorized"]
ServerProfileProof = Literal["unverified", "operator-authorized"]


@dataclass(frozen=True, slots=True)
class PreflightConfig:
    """Entradas del gate; no lee .env ni configuracion global por su cuenta."""

    mode: RunMode = "exploratory"
    ollama_base_url: str = "http://127.0.0.1:11434"
    model_name: str = MODEL_NAME
    expected_source_model: str = SOURCE_MODEL
    expected_num_ctx: int = NUM_CTX
    network_proof: NetworkProof = "unverified"
    firewall_proof_id: str | None = None
    server_profile_proof: ServerProfileProof = "unverified"
    server_profile_proof_id: str | None = None
    min_ram_available_gib: float = 8.0
    min_commit_headroom_gib: float = 8.0
    min_vram_free_mib: int = 12_288
    command_timeout_seconds: float = 10.0
    lab_root: Path = LAB_ROOT
    python_version: tuple[int, int] = field(
        default_factory=lambda: (sys.version_info.major, sys.version_info.minor)
    )

    def __post_init__(self) -> None:
        if self.mode not in {"formal", "exploratory"}:
            raise ValueError("mode debe ser formal o exploratory")
        if self.network_proof not in {"unverified", "firewall-authorized"}:
            raise ValueError("network_proof no es valido")
        if self.server_profile_proof not in {"unverified", "operator-authorized"}:
            raise ValueError("server_profile_proof no es valido")
        if self.expected_num_ctx <= 0:
            raise ValueError("expected_num_ctx debe ser positivo")
        if self.min_ram_available_gib < 0:
            raise ValueError("min_ram_available_gib no puede ser negativo")
        if self.min_commit_headroom_gib < 0:
            raise ValueError("min_commit_headroom_gib no puede ser negativo")
        if self.min_vram_free_mib < 0:
            raise ValueError("min_vram_free_mib no puede ser negativo")
        if self.command_timeout_seconds <= 0:
            raise ValueError("command_timeout_seconds debe ser positivo")


def is_loopback_http_endpoint(value: str) -> bool:
    """Acepta solo una URL HTTP base cuyo host sea inequivocamente loopback."""

    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    if parsed.scheme != "http" or not parsed.hostname:
        return False
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return False
    if parsed.path not in {"", "/"}:
        return False
    if port is not None and not 1 <= port <= 65_535:
        return False
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def is_safe_proof_id(value: str | None, *, required_prefix: str | None = None) -> bool:
    """Acepta solo un ID acotado y, cuando aplica, con namespace obligatorio."""

    if not value or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,63}", value):
        return False
    return required_prefix is None or value.startswith(required_prefix)


def contained_path(root: Path, relative: Path) -> Path:
    """Resuelve una ruta relativa y evita escrituras fuera de ``root``."""

    if relative.is_absolute():
        raise ValueError("La ruta debe ser relativa al laboratorio.")
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError("La ruta sale del laboratorio.")
    return resolved

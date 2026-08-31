from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from local_code_hermes.command import CommandRequest, CommandResult
from local_code_hermes.config import PreflightConfig
from local_code_hermes.preflight import RAM_SCRIPT


class FakeRunner:
    """Doble hermetico: una solicitud inesperada siempre falla la prueba."""

    def __init__(
        self,
        results: dict[
            tuple[str, ...],
            CommandResult | Exception | list[CommandResult | Exception],
        ],
    ) -> None:
        self._results = results
        self.requests: list[CommandRequest] = []

    def run(self, request: CommandRequest) -> CommandResult:
        self.requests.append(request)
        if request.args not in self._results:
            raise AssertionError(f"Comando real/no previsto: {request.args!r}")
        configured = self._results[request.args]
        if isinstance(configured, list):
            if not configured:
                raise AssertionError(f"No quedan respuestas para: {request.args!r}")
            configured = configured.pop(0)
        if isinstance(configured, Exception):
            raise configured
        return configured


def happy_results() -> dict[tuple[str, ...], CommandResult]:
    gib = 1024**3
    synthetic_blob = "D:/ollama/blobs/sha256-synthetic9b"
    return {
        ("ollama", "show", "local-code-9b-64k", "--modelfile"): CommandResult(
            0,
            stdout=f"FROM {synthetic_blob}\nPARAMETER num_ctx 65536\n",
        ),
        ("ollama", "show", "qwen3.5:9b", "--modelfile"): CommandResult(
            0,
            stdout="FROM D:\\ollama\\blobs\\sha256-synthetic9b\n",
        ),
        ("hermes", "--version"): CommandResult(0, stdout="Hermes Agent v0.3.1\n"),
        ("lms", "ps", "--json"): CommandResult(0, stdout="[]"),
        ("git", "rev-parse", "--verify", "HEAD"): CommandResult(
            0,
            stdout="a" * 40 + "\n",
        ),
        ("git", "status", "--porcelain=v1"): CommandResult(0, stdout=""),
        (
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            RAM_SCRIPT,
        ): CommandResult(
            0,
            stdout=json.dumps(
                {
                    "total_bytes": 64 * gib,
                    "available_bytes": 24 * gib,
                    "commit_limit_bytes": 96 * gib,
                    "commit_headroom_bytes": 24 * gib,
                    "pagefile_used_mib": 1024,
                }
            ),
        ),
        (
            "nvidia-smi",
            "--query-gpu=index,memory.total,memory.free",
            "--format=csv,noheader,nounits",
        ): CommandResult(0, stdout="0, 16384, 13000\n"),
    }


@pytest.fixture
def make_formal_config(tmp_path: Path) -> Callable[..., PreflightConfig]:
    def make(**overrides: object) -> PreflightConfig:
        values: dict[str, object] = {
            "mode": "formal",
            "network_proof": "firewall-authorized",
            "firewall_proof_id": "FW-LOCAL-001",
            "server_profile_proof": "operator-authorized",
            "server_profile_proof_id": "OLLAMA-PROFILE-001",
            "lab_root": tmp_path,
            "python_version": (3, 12),
        }
        values.update(overrides)
        lab_root = Path(values["lab_root"])
        lab_root.mkdir(parents=True, exist_ok=True)
        modelfile = lab_root / "Modelfile"
        if not modelfile.exists():
            modelfile.write_text(
                "FROM qwen3.5:9b\nPARAMETER num_ctx 65536\n",
                encoding="utf-8",
            )
        return PreflightConfig(**values)  # type: ignore[arg-type]

    return make

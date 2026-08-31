"""Runner controlado para una corrida viva de Hermes contra Ollama local."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from local_code_hermes.command import CommandRequest, CommandResult, SubprocessCommandRunner
from local_code_hermes.config import (
    LAB_ROOT,
    MODEL_NAME,
    NUM_CTX,
    SOURCE_MODEL,
    PreflightConfig,
    is_loopback_http_endpoint,
    is_safe_proof_id,
)
from local_code_hermes.fixture import FixtureVerification, prepare_workspace, verify_workspace
from local_code_hermes.preflight import PreflightReport, run_preflight
from local_code_hermes.sandbox import DEFAULT_IMAGE, DockerSandbox

BENCHMARK_VARIANT_ID = "ollama-hermes-benchmark"
BENCHMARK_PROFILE_ID = "local-code-ollama-64k"
HARNESS_VERSION = "0.2.0"
BENCHMARK_PROMPT = """Solve the B-CODE-003 pricing fixture in the current workspace.
Read the project README and tests first. Make the smallest correct change so a
discount of 100 percent is accepted and a discount above 100 percent is
rejected. Add the missing regression test. Run the complete unittest suite
before finishing. Modify only src/pricing.py and tests/test_pricing.py. Do not
access the network, install packages, modify files outside the fixture, or
commit/push changes. Finish with a short summary after the tests pass."""
_DIGEST_PATTERN = re.compile(r"(?i)sha256[-:]([0-9a-f]{64})")
_CONTEXT_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)([kmg])?$", re.IGNORECASE)
_SECRET_ENV_PARTS = ("API_KEY", "TOKEN", "PASSWORD", "SECRET")
_BLOCKED_ENV_NAMES = {
    "OPENAI_BASE_URL",
    "OPENROUTER_BASE_URL",
    "ANTHROPIC_BASE_URL",
    "HERMES_CONFIG",
    "HERMES_PROFILE",
}


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    lab_root: Path = LAB_ROOT
    hermes_home: Path | None = None
    runs_dir: Path | None = None
    workspace_root: Path | None = None
    model_name: str = MODEL_NAME
    source_model: str = SOURCE_MODEL
    ollama_base_url: str = "http://127.0.0.1:11434"
    context_tokens: int = NUM_CTX
    sandbox_image: str = DEFAULT_IMAGE
    hermes_timeout_seconds: float = 1_200.0
    command_timeout_seconds: float = 30.0
    allow_dirty_worktree: bool = False
    network_proof_id: str | None = None
    server_profile_proof_id: str | None = None

    def __post_init__(self) -> None:
        root = self.lab_root.resolve()
        object.__setattr__(self, "lab_root", root)
        object.__setattr__(
            self,
            "hermes_home",
            (self.hermes_home or root / ".local" / "hermes-home").resolve(),
        )
        object.__setattr__(
            self,
            "runs_dir",
            (self.runs_dir or root / ".local" / "runs").resolve(),
        )
        object.__setattr__(
            self,
            "workspace_root",
            (self.workspace_root or root / ".local" / "workspaces").resolve(),
        )
        if self.model_name != MODEL_NAME or self.source_model != SOURCE_MODEL:
            raise ValueError("La identidad del modelo no coincide con el laboratorio.")
        if self.context_tokens != NUM_CTX:
            raise ValueError("El benchmark exige exactamente 65536 tokens de contexto.")
        if not is_loopback_http_endpoint(self.ollama_base_url):
            raise ValueError("Ollama debe estar fijado a loopback HTTP.")
        if not self.sandbox_image or any(char.isspace() for char in self.sandbox_image):
            raise ValueError("La imagen del sandbox no es valida.")
        if self.hermes_timeout_seconds <= 0 or self.command_timeout_seconds <= 0:
            raise ValueError("Los timeouts deben ser positivos.")
        if self.network_proof_id is not None and not is_safe_proof_id(
            self.network_proof_id,
            required_prefix="FW-",
        ):
            raise ValueError("El ID de firewall no es valido.")
        if self.server_profile_proof_id is not None and not is_safe_proof_id(
            self.server_profile_proof_id,
            required_prefix="OLLAMA-",
        ):
            raise ValueError("El ID de perfil Ollama no es valido.")

    @property
    def ollama_api_base_url(self) -> str:
        return self.ollama_base_url.rstrip("/") + "/v1"


@dataclass(frozen=True, slots=True)
class BenchmarkProcessResult:
    returncode: int
    timed_out: bool = False
    duration_ms: int = 0
    output_digest: str | None = None
    error_kind: str | None = None


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    outcome: Literal["completed", "blocked", "failed"]
    reason: str
    run_id: str
    preflight_outcome: str
    dirty_worktree_override: bool = False
    workspace_label: str | None = None
    workspace: Path | None = None
    git_head: str | None = None
    hermes_version: str | None = None
    model_digest: str | None = None
    sandbox_image_digest: str | None = None
    process: BenchmarkProcessResult | None = None
    usage: dict[str, int] | None = None
    fixture: FixtureVerification | None = None
    ollama_observation: dict[str, object] = field(default_factory=dict)
    log_observation: dict[str, object] = field(default_factory=dict)
    comparable: bool = False
    scored: bool = False
    scores: dict[str, float | None] = field(default_factory=dict)


ProcessRunner = Callable[
    [tuple[str, ...], Path, Mapping[str, str], float],
    BenchmarkProcessResult,
]


def _ollama_environment(endpoint: str) -> dict[str, str]:
    return {
        "OLLAMA_HOST": endpoint,
        "OLLAMA_NO_CLOUD": "1",
        "NO_PROXY": "localhost,127.0.0.1,::1",
        "no_proxy": "localhost,127.0.0.1,::1",
        "HTTP_PROXY": "",
        "HTTPS_PROXY": "",
        "ALL_PROXY": "",
        "http_proxy": "",
        "https_proxy": "",
        "all_proxy": "",
    }


def _safe_environment(config: BenchmarkConfig, workspace: Path) -> dict[str, str]:
    environment = dict(os.environ)
    for name in list(environment):
        upper = name.upper()
        if name in _BLOCKED_ENV_NAMES or any(part in upper for part in _SECRET_ENV_PARTS):
            environment.pop(name, None)
    environment.update(
        {
            "HERMES_HOME": str(config.hermes_home),
            "HERMES_INFERENCE_MODEL": config.model_name,
            "TERMINAL_ENV": "docker",
            "TERMINAL_CWD": str(workspace),
            "TERMINAL_DOCKER_IMAGE": config.sandbox_image,
            "TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE": "true",
            "TERMINAL_DOCKER_NETWORK": "false",
            "TERMINAL_CONTAINER_PERSISTENT": "false",
            "TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES": "false",
            "TERMINAL_DOCKER_ORPHAN_REAPER": "true",
            "TERMINAL_DOCKER_FORWARD_ENV": "[]",
            "TERMINAL_DOCKER_VOLUMES": "[]",
            "TERMINAL_DOCKER_ENV": "{}",
            "OLLAMA_HOST": config.ollama_base_url,
            "OLLAMA_NO_CLOUD": "1",
            "NO_PROXY": "localhost,127.0.0.1,::1",
            "no_proxy": "localhost,127.0.0.1,::1",
            "HTTP_PROXY": "",
            "HTTPS_PROXY": "",
            "ALL_PROXY": "",
            "http_proxy": "",
            "https_proxy": "",
            "all_proxy": "",
            "HERMES_WRITE_SAFE_ROOT": os.pathsep.join(
                (str(config.lab_root), str(config.hermes_home), str(workspace))
            ),
        }
    )
    return environment


def build_hermes_command(
    config: BenchmarkConfig,
    workspace: Path,
    usage_path: Path,
) -> tuple[str, ...]:
    """Construye el comando explicito; no usa el proveedor configurado por el usuario."""

    workspace_resolved = workspace.resolve()
    usage_resolved = usage_path.resolve()
    return (
        "hermes",
        "-z",
        BENCHMARK_PROMPT,
        "--model",
        config.model_name,
        "--provider",
        "custom",
        "--in",
        str(workspace_resolved),
        "--no-restore-cwd",
        "--ignore-rules",
        "--usage-file",
        str(usage_resolved),
    )


def build_hermes_environment(config: BenchmarkConfig, workspace: Path) -> dict[str, str]:
    return _safe_environment(config, workspace.resolve())


def _context_value(value: str) -> int:
    match = _CONTEXT_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError("context value is not numeric")
    number = float(match.group(1))
    multiplier = {None: 1, "k": 1024, "m": 1024**2, "g": 1024**3}[
        match.group(2).lower() if match.group(2) else None
    ]
    result = int(number * multiplier)
    if result <= 0 or number * multiplier != result:
        raise ValueError("context value is not an integer")
    return result


def parse_ollama_ps(
    text: str,
    *,
    model_name: str = MODEL_NAME,
    expected_context: int = NUM_CTX,
) -> dict[str, object]:
    """Lee solo la fila objetivo de ``ollama ps`` y exige residencia GPU total."""

    target_line: str | None = None
    for line in text.splitlines():
        tokens = line.split()
        if tokens and tokens[0] == model_name:
            target_line = line
            break
    if target_line is None:
        raise ValueError("model is not loaded")

    tokens = target_line.split()
    processor_index = next(
        (index for index, token in enumerate(tokens) if re.fullmatch(r"\d+%(?:/\d+%)?", token)),
        None,
    )
    if processor_index is None or processor_index + 2 >= len(tokens):
        raise ValueError("processor or context is missing")
    processor = f"{tokens[processor_index]} {tokens[processor_index + 1]}"
    context_tokens = _context_value(tokens[processor_index + 2])
    if context_tokens != expected_context:
        raise ValueError("context does not match the configured profile")
    if processor != "100% GPU":
        raise ValueError("processor is not 100% GPU")
    return {
        "model_name": model_name,
        "processor": processor,
        "context_tokens": context_tokens,
        "gpu_resident": True,
    }


def parse_usage_report(path: Path) -> dict[str, int]:
    """Normaliza el reporte de Hermes y rechaza reportes con contenido de respuesta."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("usage report is unreadable") from exc
    if not isinstance(raw, dict):
        raise ValueError("usage report must be an object")
    if any(key in raw for key in ("response", "content", "output", "prompt", "stderr", "stdout")):
        raise ValueError("usage report contains raw content")

    aliases = {
        "prompt_tokens": ("prompt_tokens", "input_tokens"),
        "completion_tokens": ("completion_tokens", "output_tokens"),
        "total_tokens": ("total_tokens",),
        "api_calls": ("api_calls",),
    }
    result: dict[str, int] = {}
    for destination, names in aliases.items():
        value = next((raw[name] for name in names if name in raw), None)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"usage report field {destination} is invalid")
        result[destination] = value
    if result["total_tokens"] != result["prompt_tokens"] + result["completion_tokens"]:
        raise ValueError("usage report total is inconsistent")
    return result


def _extract_digest(text: str) -> str | None:
    match = _DIGEST_PATTERN.search(text)
    return f"sha256:{match.group(1).lower()}" if match else None


def _command(
    config: BenchmarkConfig,
    args: tuple[str, ...],
    *,
    timeout: float | None = None,
) -> CommandResult:
    return SubprocessCommandRunner().run(
        CommandRequest(
            args=args,
            cwd=config.lab_root,
            env_overrides=_ollama_environment(config.ollama_base_url),
            timeout_seconds=timeout or config.command_timeout_seconds,
        )
    )


def _capture_model_digest(config: BenchmarkConfig) -> str | None:
    alias = _command(config, ("ollama", "show", config.model_name, "--modelfile"))
    source = _command(config, ("ollama", "show", config.source_model, "--modelfile"))
    if alias.returncode != 0 or source.returncode != 0:
        return None
    alias_digest = _extract_digest(alias.stdout)
    source_digest = _extract_digest(source.stdout)
    return alias_digest if alias_digest and alias_digest == source_digest else None


def _run_hermes_process(
    command: tuple[str, ...],
    cwd: Path,
    environment: Mapping[str, str],
    timeout_seconds: float,
) -> BenchmarkProcessResult:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=dict(environment),
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        return BenchmarkProcessResult(
            returncode=127,
            duration_ms=int((time.monotonic() - started) * 1000),
            error_kind="not_found",
        )
    except subprocess.TimeoutExpired:
        return BenchmarkProcessResult(
            returncode=124,
            timed_out=True,
            duration_ms=int((time.monotonic() - started) * 1000),
            error_kind="timeout",
        )
    output_digest = hashlib.sha256(completed.stdout + b"\0" + completed.stderr).hexdigest()
    return BenchmarkProcessResult(
        returncode=completed.returncode,
        duration_ms=int((time.monotonic() - started) * 1000),
        output_digest=f"sha256:{output_digest}",
        error_kind=None if completed.returncode == 0 else "nonzero",
    )


class OllamaLogObserver:
    """Cuenta solo lineas nuevas de truncacion y HTTP 500, sin exportar su texto."""

    def __init__(self, log_dir: Path | None = None) -> None:
        if log_dir is None:
            local_app_data = os.environ.get("LOCALAPPDATA")
            log_dir = (
                Path(local_app_data) / "Ollama"
                if local_app_data
                else Path.home() / "AppData" / "Local" / "Ollama"
            )
        self.log_dir = log_dir.resolve()

    def snapshot(self) -> dict[str, int]:
        result: dict[str, int] = {}
        if not self.log_dir.is_dir():
            return result
        for path in sorted(self.log_dir.glob("server*.log")):
            try:
                result[path.name] = path.stat().st_size
            except OSError:
                continue
        return result

    def delta(self, before: Mapping[str, int]) -> dict[str, object]:
        truncations = 0
        http_500 = 0
        files_observed = 0
        current = self.snapshot()
        for name, size in current.items():
            start = before.get(name, 0)
            if size < start:
                start = 0
            path = self.log_dir / name
            try:
                with path.open("rb") as handle:
                    handle.seek(start)
                    text = handle.read().decode("utf-8", errors="replace")
            except OSError:
                continue
            files_observed += 1
            for line in text.splitlines():
                if "truncating input prompt" in line.casefold():
                    truncations += 1
                if re.search(r"(?i)(?:^|\s)500(?:\s|$)", line):
                    http_500 += 1
        return {
            "files_observed": files_observed,
            "truncation_count": truncations,
            "http_500_count": http_500,
            "log_delta_observed": bool(files_observed),
        }


def _gate_value(report: PreflightReport, gate_id: str, field: str) -> object | None:
    gate = next((item for item in report.gates if item.gate_id == gate_id), None)
    if gate is None or gate.outcome != "passed":
        return None
    return gate.evidence.get(field)


def _preflight_allows_execution(config: BenchmarkConfig, preflight: PreflightReport) -> bool:
    if preflight.mode != "formal":
        return False
    if preflight.outcome == "passed" and all(gate.outcome == "passed" for gate in preflight.gates):
        return True
    if not config.allow_dirty_worktree:
        return False
    blocking = [gate for gate in preflight.gates if gate.outcome in {"blocked", "failed"}]
    return (
        len(blocking) == 1
        and blocking[0].gate_id == "git.head"
        and blocking[0].code == "worktree_dirty"
        and all(gate.outcome == "passed" for gate in preflight.gates if gate.gate_id != "git.head")
    )


def _new_run_id() -> str:
    return f"run-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"


def run_benchmark(
    config: BenchmarkConfig,
    *,
    preflight: PreflightReport,
    process_runner: ProcessRunner | None = None,
    sandbox: DockerSandbox | None = None,
) -> BenchmarkReport:
    run_id = _new_run_id()
    if not _preflight_allows_execution(config, preflight):
        return BenchmarkReport(
            outcome="blocked",
            reason="preflight_not_green",
            run_id=run_id,
            preflight_outcome=preflight.outcome,
        )

    dirty_override = any(
        gate.gate_id == "git.head" and gate.code == "worktree_dirty" for gate in preflight.gates
    )
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    workspace_label = f"hermes-{timestamp}-{uuid.uuid4().hex[:8]}"
    config.workspace_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_workspace(workspace_label, workspaces_root=config.workspace_root)
    usage_dir = config.lab_root / ".local" / "usage"
    usage_dir.mkdir(parents=True, exist_ok=True)
    usage_path = usage_dir / f"{run_id}.json"
    command = build_hermes_command(config, workspace, usage_path)
    environment = build_hermes_environment(config, workspace)
    model_digest = _capture_model_digest(config)
    if model_digest is None:
        return BenchmarkReport(
            outcome="blocked",
            reason="model_digest_unverified",
            run_id=run_id,
            preflight_outcome=preflight.outcome,
            dirty_worktree_override=dirty_override,
            workspace_label=workspace_label,
            workspace=workspace,
        )

    selected_sandbox = sandbox or DockerSandbox(workspace, image=config.sandbox_image)
    sandbox_image_digest = selected_sandbox.image_identity()
    if sandbox_image_digest is None:
        return BenchmarkReport(
            outcome="blocked",
            reason="sandbox_image_unavailable",
            run_id=run_id,
            preflight_outcome=preflight.outcome,
            dirty_worktree_override=dirty_override,
            workspace_label=workspace_label,
            workspace=workspace,
            model_digest=model_digest,
        )

    config.hermes_home.mkdir(parents=True, exist_ok=True)
    (config.hermes_home / "config.yaml").write_text(
        "model:\n"
        f"  default: {config.model_name}\n"
        "  provider: custom\n"
        f"  base_url: {config.ollama_api_base_url}\n"
        f"  context_length: {config.context_tokens}\n"
        "terminal:\n"
        "  backend: docker\n"
        f"  docker_image: {config.sandbox_image}\n"
        "  docker_mount_cwd_to_workspace: true\n"
        "  docker_network: false\n"
        "  container_persistent: false\n"
        "  docker_persist_across_processes: false\n"
        "  docker_forward_env: []\n"
        "  docker_volumes: []\n"
        "  docker_env: {}\n",
        encoding="utf-8",
        newline="\n",
    )

    observer = OllamaLogObserver()
    log_before = observer.snapshot()
    runner = process_runner or _run_hermes_process
    process = runner(command, workspace, environment, config.hermes_timeout_seconds)
    usage: dict[str, int] | None = None
    usage_reason: str | None = None
    if usage_path.is_file():
        try:
            usage = parse_usage_report(usage_path)
        except ValueError:
            usage_reason = "usage_report_invalid"
    else:
        usage_reason = "usage_report_missing"

    log_observation = observer.delta(log_before)
    ps_result = _command(config, ("ollama", "ps"))
    ollama_observation: dict[str, object] = {}
    if ps_result.returncode == 0:
        try:
            ollama_observation = parse_ollama_ps(ps_result.stdout)
        except ValueError as exc:
            ollama_observation = {"runtime_identity_verified": False, "reason": str(exc)}
    else:
        ollama_observation = {"runtime_identity_verified": False}
    ollama_observation.setdefault(
        "runtime_identity_verified",
        ollama_observation.get("gpu_resident") is True
        and ollama_observation.get("context_tokens") == config.context_tokens,
    )
    fixture_result = verify_workspace(
        workspace,
        execute_tests=True,
        check_executor=selected_sandbox.execute_check,
    )

    if process.timed_out:
        outcome: Literal["completed", "blocked", "failed"] = "failed"
        reason = "hermes_timeout"
    elif process.returncode != 0:
        outcome = "failed"
        reason = "hermes_process_failed"
    elif usage_reason is not None:
        outcome = "completed"
        reason = usage_reason
    elif not fixture_result.passed:
        outcome = "completed"
        reason = "fixture_verification_failed"
    elif not ollama_observation.get("runtime_identity_verified"):
        outcome = "completed"
        reason = "runtime_identity_unverified"
    elif log_observation["truncation_count"] or log_observation["http_500_count"]:
        outcome = "completed"
        reason = "ollama_runtime_errors"
    else:
        outcome = "completed"
        reason = "run_completed_not_comparable"

    scores = {
        "fixture_correctness": 100.0 if fixture_result.passed else 0.0,
        "runtime_context": (100.0 if ollama_observation.get("runtime_identity_verified") else 0.0),
    }
    observed_git_head = next(
        (
            gate.evidence.get("head")
            for gate in preflight.gates
            if gate.gate_id == "git.head" and isinstance(gate.evidence.get("head"), str)
        ),
        None,
    )
    return BenchmarkReport(
        outcome=outcome,
        reason=reason,
        run_id=run_id,
        preflight_outcome=preflight.outcome,
        dirty_worktree_override=dirty_override,
        workspace_label=workspace_label,
        workspace=workspace,
        git_head=observed_git_head,
        hermes_version=_gate_value(preflight, "hermes.available", "version"),
        model_digest=model_digest,
        sandbox_image_digest=sandbox_image_digest,
        process=process,
        usage=usage,
        fixture=fixture_result,
        ollama_observation=ollama_observation,
        log_observation=log_observation,
        comparable=False,
        scored=False,
        scores=scores,
    )


def _build_config(args: argparse.Namespace) -> BenchmarkConfig:
    return BenchmarkConfig(
        lab_root=LAB_ROOT,
        allow_dirty_worktree=args.allow_dirty_worktree,
        network_proof_id=args.network_proof_id,
        server_profile_proof_id=args.server_profile_proof_id,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta una corrida viva y aislada de Hermes.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Autoriza la corrida viva; sin esta bandera solo se muestra el contrato.",
    )
    parser.add_argument(
        "--allow-dirty-worktree",
        action="store_true",
        help="Permite un smoke de desarrollo no puntuable con worktree sucio.",
    )
    parser.add_argument(
        "--network-proof-id",
        default="FW-LOCAL-20260830",
        help="ID humano previamente autorizado para la evidencia de firewall.",
    )
    parser.add_argument(
        "--server-profile-proof-id",
        default="OLLAMA-PROFILE-20260830",
        help="ID humano previamente autorizado para el perfil Ollama.",
    )
    args = parser.parse_args(argv)
    if not args.execute:
        print("Benchmark preparado; usa --execute solo con el host autorizado.")
        return 2
    try:
        config = _build_config(args)
        preflight_config = PreflightConfig(
            mode="formal",
            ollama_base_url=config.ollama_base_url,
            network_proof="firewall-authorized",
            firewall_proof_id=args.network_proof_id,
            server_profile_proof="operator-authorized",
            server_profile_proof_id=args.server_profile_proof_id,
            lab_root=LAB_ROOT,
        )
        preflight = run_preflight(preflight_config, SubprocessCommandRunner())
        report = run_benchmark(config, preflight=preflight)
        from local_code_hermes.benchmark_log import write_benchmark_report

        path = write_benchmark_report(report, config.runs_dir, config, preflight)
    except (OSError, ValueError, subprocess.SubprocessError):
        print("Benchmark no verificable; no se exportaron contenidos de proceso.")
        return 1
    print(f"Benchmark {report.outcome}; reason={report.reason}; JSONL=.local/runs/{path.name}")
    return {"completed": 0, "blocked": 2, "failed": 1}[report.outcome]


if __name__ == "__main__":
    main()

"""Preflight fail-closed para el futuro benchmark local de Hermes."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from local_code_hermes.command import (
    CommandRequest,
    CommandResult,
    CommandRunner,
    SubprocessCommandRunner,
)
from local_code_hermes.config import (
    DEFAULT_RUNS_DIR,
    LAB_ROOT,
    MODEL_NAME,
    PreflightConfig,
    is_loopback_http_endpoint,
    is_safe_proof_id,
)
from local_code_hermes.config import REQUIRED_GATE_IDS as CONFIG_REQUIRED_GATE_IDS

GateOutcome = Literal["passed", "warning", "blocked", "failed"]
REQUIRED_GATE_IDS = CONFIG_REQUIRED_GATE_IDS
TERMINAL_BY_OUTCOME = {
    "passed": "run.completed",
    "blocked": "run.blocked",
    "failed": "run.failed",
}
RAM_SCRIPT = (
    "$os=Get-CimInstance Win32_OperatingSystem;"
    "$page=Get-CimInstance Win32_PageFileUsage | "
    "Measure-Object -Property CurrentUsage -Sum;"
    "[pscustomobject]@{"
    "total_bytes=[int64]$os.TotalVisibleMemorySize*1KB;"
    "available_bytes=[int64]$os.FreePhysicalMemory*1KB;"
    "commit_limit_bytes=[int64]$os.TotalVirtualMemorySize*1KB;"
    "commit_headroom_bytes=[int64]$os.FreeVirtualMemory*1KB;"
    "pagefile_used_mib=[int64]$page.Sum"
    "}|ConvertTo-Json -Compress"
)

LMSTUDIO_PROCESS_SCRIPT = (
    "$all=@(Get-CimInstance Win32_Process -Filter \"Name = 'llama-server.exe'\");"
    "$items=@($all | "
    "Where-Object { $_.ExecutablePath -and "
    "$_.ExecutablePath.ToLowerInvariant().Contains('\\.lmstudio\\') });"
    "$unknown=@($all | Where-Object { -not $_.ExecutablePath });"
    "[pscustomobject]@{loaded_model_processes=[int]$items.Count;"
    "unknown_model_processes=[int]$unknown.Count} | "
    "ConvertTo-Json -Compress"
)


@dataclass(frozen=True, slots=True)
class GateResult:
    gate_id: str
    outcome: GateOutcome
    blocking: bool
    code: str
    evidence: dict[str, object]


@dataclass(frozen=True, slots=True)
class PreflightReport:
    mode: str
    gates: tuple[GateResult, ...]

    @property
    def outcome(self) -> Literal["passed", "blocked", "failed"]:
        if any(gate.outcome == "failed" for gate in self.gates):
            return "failed"
        if any(gate.outcome == "blocked" for gate in self.gates):
            return "blocked"
        return "passed"

    @property
    def terminal_event(self) -> str:
        return TERMINAL_BY_OUTCOME[self.outcome]


def _gate(
    gate_id: str,
    outcome: GateOutcome,
    code: str,
    evidence: dict[str, object] | None = None,
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        outcome=outcome,
        blocking=outcome in {"blocked", "failed"},
        code=code,
        evidence=evidence or {},
    )


def _command_failure(gate_id: str, result: CommandResult) -> GateResult:
    code = {
        "not_found": "command_not_found",
        "timeout": "command_timeout",
    }.get(result.error_kind, "command_nonzero")
    return _gate(gate_id, "blocked", code, {"returncode": result.returncode})


def _guard(gate_id: str, check: Callable[[], GateResult]) -> GateResult:
    try:
        return check()
    except Exception:
        return _gate(gate_id, "failed", "internal_check_error")


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


def check_python(config: PreflightConfig) -> GateResult:
    if config.python_version == (3, 12):
        return _gate("python.runtime", "passed", "python_3_12", {"major": 3, "minor": 12})
    return _gate(
        "python.runtime",
        "blocked",
        "python_version_mismatch",
        {"major": config.python_version[0], "minor": config.python_version[1]},
    )


def check_endpoint(config: PreflightConfig) -> GateResult:
    if is_loopback_http_endpoint(config.ollama_base_url):
        return _gate(
            "network.endpoint",
            "passed",
            "loopback_http",
            {"endpoint": config.ollama_base_url},
        )
    return _gate("network.endpoint", "blocked", "endpoint_not_loopback")


def check_firewall(config: PreflightConfig) -> GateResult:
    if config.network_proof == "firewall-authorized" and is_safe_proof_id(
        config.firewall_proof_id, required_prefix="FW-"
    ):
        return _gate(
            "network.firewall",
            "passed",
            "authorized_firewall_proof",
            {"proof_present": True, "method": "authorized_firewall"},
        )
    if config.network_proof == "firewall-authorized":
        return _gate("network.firewall", "blocked", "invalid_firewall_proof_id")
    if config.mode == "exploratory":
        return _gate(
            "network.firewall",
            "warning",
            "locality_unproven_exploratory",
            {"proof_present": False},
        )
    return _gate(
        "network.firewall",
        "blocked",
        "locality_unproven",
        {"proof_present": False},
    )


def check_server_profile(config: PreflightConfig) -> GateResult:
    """Exige una referencia humana: el entorno del cliente no prueba el servidor."""

    expected = {
        "flash_attention": "1",
        "kv_cache_type": "q8_0",
        "num_parallel": "1",
        "max_loaded_models": "1",
        "no_cloud": "1",
    }
    if config.server_profile_proof == "operator-authorized" and is_safe_proof_id(
        config.server_profile_proof_id, required_prefix="OLLAMA-"
    ):
        return _gate(
            "ollama.server_profile",
            "passed",
            "operator_profile_evidence_referenced",
            {"proof_present": True, "expected": expected},
        )
    if config.server_profile_proof == "operator-authorized":
        return _gate(
            "ollama.server_profile",
            "blocked",
            "invalid_server_profile_proof_id",
            {"proof_present": False, "expected": expected},
        )
    if config.mode == "exploratory":
        return _gate(
            "ollama.server_profile",
            "warning",
            "server_profile_unproven_exploratory",
            {"proof_present": False, "expected": expected},
        )
    return _gate(
        "ollama.server_profile",
        "blocked",
        "server_profile_unproven",
        {"proof_present": False, "expected": expected},
    )


def _parse_modelfile(text: str) -> tuple[str, int] | None:
    sources = re.findall(r"(?im)^\s*FROM\s+([^\s#]+)\s*(?:#.*)?$", text)
    contexts = re.findall(r"(?im)^\s*PARAMETER\s+num_ctx\s+(\d+)\s*(?:#.*)?$", text)
    if len(sources) != 1 or len(contexts) != 1:
        return None
    return sources[0], int(contexts[0])


def _parse_single_from(text: str) -> str | None:
    sources = re.findall(r"(?im)^\s*FROM\s+([^\s#]+)\s*(?:#.*)?$", text)
    return sources[0] if len(sources) == 1 else None


def _same_weight_reference(left: str, right: str) -> bool:
    return left.replace("\\", "/").casefold() == right.replace("\\", "/").casefold()


def check_model(
    config: PreflightConfig,
    runner: CommandRunner,
    *,
    endpoint_approved: bool,
) -> GateResult:
    if not endpoint_approved:
        return _gate("ollama.model", "blocked", "endpoint_not_approved")
    if config.model_name != MODEL_NAME:
        return _gate("ollama.model", "blocked", "model_name_mismatch")
    try:
        contract_text = (config.lab_root / "Modelfile").read_text(encoding="utf-8")
    except OSError:
        return _gate("ollama.model", "blocked", "model_contract_unreadable")
    contract = _parse_modelfile(contract_text)
    if contract is None:
        return _gate("ollama.model", "blocked", "model_contract_unparseable")
    declared_source, declared_num_ctx = contract
    if declared_source != config.expected_source_model:
        return _gate(
            "ollama.model",
            "blocked",
            "model_contract_source_mismatch",
            {"declared_source_matches": False},
        )
    if declared_num_ctx != config.expected_num_ctx:
        return _gate(
            "ollama.model",
            "blocked",
            "model_contract_num_ctx_mismatch",
            {"declared_num_ctx": declared_num_ctx},
        )

    environment = _ollama_environment(config.ollama_base_url)
    alias_result = runner.run(
        CommandRequest(
            args=("ollama", "show", config.model_name, "--modelfile"),
            cwd=config.lab_root,
            env_overrides=environment,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if alias_result.returncode != 0:
        return _command_failure("ollama.model", alias_result)
    alias = _parse_modelfile(alias_result.stdout)
    if alias is None:
        return _gate("ollama.model", "blocked", "runtime_modelfile_unparseable")
    alias_weight_reference, num_ctx = alias

    source_result = runner.run(
        CommandRequest(
            args=("ollama", "show", config.expected_source_model, "--modelfile"),
            cwd=config.lab_root,
            env_overrides=environment,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if source_result.returncode != 0:
        return _gate(
            "ollama.model",
            "blocked",
            "source_model_unavailable",
            {"returncode": source_result.returncode},
        )
    source_weight_reference = _parse_single_from(source_result.stdout)
    if source_weight_reference is None:
        return _gate("ollama.model", "blocked", "source_modelfile_unparseable")

    evidence = {
        "model_name": config.model_name,
        "source_model": config.expected_source_model,
        "num_ctx": num_ctx,
        "contract_verified": True,
        "weights_match": _same_weight_reference(alias_weight_reference, source_weight_reference),
    }
    if num_ctx != config.expected_num_ctx:
        return _gate("ollama.model", "blocked", "num_ctx_mismatch", evidence)
    if not evidence["weights_match"]:
        return _gate("ollama.model", "blocked", "source_weights_mismatch", evidence)
    return _gate("ollama.model", "passed", "model_identity_verified", evidence)


def check_hermes(config: PreflightConfig, runner: CommandRunner) -> GateResult:
    result = runner.run(
        CommandRequest(
            args=("hermes", "--version"),
            cwd=config.lab_root,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if result.returncode != 0:
        return _command_failure("hermes.available", result)
    match = re.search(
        r"(?<![A-Za-z0-9])v?(\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?)",
        f"{result.stdout}\n{result.stderr}",
    )
    if not match:
        return _gate("hermes.available", "blocked", "version_not_captured")
    return _gate(
        "hermes.available",
        "passed",
        "version_captured",
        {"version": match.group(1)},
    )


def _loaded_model_count(value: object) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("loaded_models", "models", "data"):
            models = value.get(key)
            if isinstance(models, list):
                return len(models)
    raise ValueError("Formato de lms ps desconocido")


def check_lmstudio(config: PreflightConfig, runner: CommandRunner) -> GateResult:
    result = runner.run(
        CommandRequest(
            args=("lms", "ps", "--json"),
            cwd=config.lab_root,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if result.error_kind == "not_found":
        process_result = runner.run(
            CommandRequest(
                args=(
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    LMSTUDIO_PROCESS_SCRIPT,
                ),
                cwd=config.lab_root,
                timeout_seconds=config.command_timeout_seconds,
            )
        )
        if process_result.returncode != 0:
            return _command_failure("lmstudio.conflict", process_result)
        try:
            process_state = json.loads(process_result.stdout)
            process_count = _positive_int_or_zero(
                process_state.get("loaded_model_processes")
                if isinstance(process_state, dict)
                else None
            )
            unknown_count = _positive_int_or_zero(
                process_state.get("unknown_model_processes")
                if isinstance(process_state, dict)
                else None
            )
        except (json.JSONDecodeError, ValueError):
            return _gate("lmstudio.conflict", "blocked", "lmstudio_state_unknown")
        if process_count:
            return _gate(
                "lmstudio.conflict",
                "blocked",
                "lmstudio_model_process_observed",
                {"loaded_model_count": process_count, "method": "process_fallback"},
            )
        if unknown_count:
            return _gate(
                "lmstudio.conflict",
                "blocked",
                "lmstudio_state_unknown",
                {"unknown_process_count": unknown_count},
            )
        return _gate(
            "lmstudio.conflict",
            "passed",
            "lms_absent_no_model_process_observed",
            {"loaded_model_count": 0, "method": "process_fallback"},
        )
    if result.returncode != 0:
        return _command_failure("lmstudio.conflict", result)
    try:
        loaded_count = _loaded_model_count(json.loads(result.stdout))
    except (json.JSONDecodeError, ValueError):
        return _gate("lmstudio.conflict", "blocked", "lmstudio_state_unknown")
    if loaded_count:
        return _gate(
            "lmstudio.conflict",
            "blocked",
            "lmstudio_model_loaded",
            {"loaded_model_count": loaded_count},
        )
    return _gate(
        "lmstudio.conflict",
        "passed",
        "no_lmstudio_model_loaded",
        {"loaded_model_count": 0},
    )


def check_git(config: PreflightConfig, runner: CommandRunner) -> GateResult:
    result = runner.run(
        CommandRequest(
            args=("git", "rev-parse", "--verify", "HEAD"),
            cwd=config.lab_root,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    head = result.stdout.strip()
    if result.returncode == 0:
        if re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", head):
            return _gate("git.head", "passed", "head_captured", {"head": head.lower()})
        return _gate("git.head", "blocked", "head_not_exact")
    if result.returncode == 128 and result.error_kind != "not_found":
        if config.mode == "exploratory":
            return _gate("git.head", "warning", "head_absent_exploratory")
        return _gate("git.head", "blocked", "head_absent_formal")
    return _command_failure("git.head", result)


def _positive_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("Se esperaba un entero positivo")
    return value


def _positive_int_or_zero(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Se esperaba un entero no negativo")
    return value


def check_ram(config: PreflightConfig, runner: CommandRunner) -> GateResult:
    result = runner.run(
        CommandRequest(
            args=("powershell.exe", "-NoProfile", "-NonInteractive", "-Command", RAM_SCRIPT),
            cwd=config.lab_root,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if result.returncode != 0:
        return _command_failure("resource.ram", result)
    try:
        raw = json.loads(result.stdout)
        if not isinstance(raw, dict):
            raise ValueError("Objeto esperado")
        total_bytes = _positive_int(raw.get("total_bytes"))
        available_bytes = _positive_int(raw.get("available_bytes"))
        commit_limit_bytes = _positive_int(raw.get("commit_limit_bytes"))
        commit_headroom_bytes = _positive_int(raw.get("commit_headroom_bytes"))
        pagefile_used_mib = raw.get("pagefile_used_mib")
        if isinstance(pagefile_used_mib, bool) or not isinstance(pagefile_used_mib, int):
            raise ValueError("Uso de pagefile invalido")
        if pagefile_used_mib < 0:
            raise ValueError("Uso de pagefile negativo")
        if available_bytes > total_bytes:
            raise ValueError("Memoria disponible invalida")
        if commit_headroom_bytes > commit_limit_bytes:
            raise ValueError("Headroom comprometido invalido")
    except (json.JSONDecodeError, ValueError):
        return _gate("resource.ram", "blocked", "ram_evidence_invalid")
    gib = 1024**3
    available_gib = round(available_bytes / gib, 2)
    commit_headroom_gib = round(commit_headroom_bytes / gib, 2)
    evidence = {
        "total_gib": round(total_bytes / gib, 2),
        "available_gib": available_gib,
        "minimum_available_gib": config.min_ram_available_gib,
        "commit_limit_gib": round(commit_limit_bytes / gib, 2),
        "commit_headroom_gib": commit_headroom_gib,
        "minimum_commit_headroom_gib": config.min_commit_headroom_gib,
        "pagefile_used_mib": pagefile_used_mib,
    }
    if (
        available_gib < config.min_ram_available_gib
        or commit_headroom_gib < config.min_commit_headroom_gib
    ):
        return _gate("resource.ram", "blocked", "ram_headroom_low", evidence)
    return _gate("resource.ram", "passed", "ram_headroom_recorded", evidence)


def check_vram(config: PreflightConfig, runner: CommandRunner) -> GateResult:
    result = runner.run(
        CommandRequest(
            args=(
                "nvidia-smi",
                "--query-gpu=index,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ),
            cwd=config.lab_root,
            timeout_seconds=config.command_timeout_seconds,
        )
    )
    if result.returncode != 0:
        return _command_failure("resource.vram", result)
    rows: list[tuple[int, int, int]] = []
    try:
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            index_text, total_text, free_text = (part.strip() for part in line.split(","))
            index = int(index_text)
            total_mib = int(total_text)
            free_mib = int(free_text)
            if index < 0 or total_mib <= 0 or free_mib < 0 or free_mib > total_mib:
                raise ValueError("Fila de VRAM invalida")
            rows.append((index, total_mib, free_mib))
        if not rows:
            raise ValueError("No hay GPUs")
    except (TypeError, ValueError):
        return _gate("resource.vram", "blocked", "vram_evidence_invalid")
    _, total_mib, free_mib = max(rows, key=lambda row: row[2])
    evidence = {
        "gpu_count": len(rows),
        "selected_total_mib": total_mib,
        "selected_free_mib": free_mib,
        "minimum_free_mib": config.min_vram_free_mib,
    }
    if free_mib < config.min_vram_free_mib:
        return _gate("resource.vram", "blocked", "vram_headroom_low", evidence)
    return _gate("resource.vram", "passed", "vram_headroom_recorded", evidence)


def run_preflight(config: PreflightConfig, runner: CommandRunner) -> PreflightReport:
    """Ejecuta todos los checks y convierte excepciones inesperadas en fallo cerrado."""

    endpoint = _guard("network.endpoint", lambda: check_endpoint(config))
    gates = (
        _guard("python.runtime", lambda: check_python(config)),
        endpoint,
        _guard("network.firewall", lambda: check_firewall(config)),
        _guard("ollama.server_profile", lambda: check_server_profile(config)),
        _guard(
            "ollama.model",
            lambda: check_model(
                config,
                runner,
                endpoint_approved=endpoint.outcome == "passed",
            ),
        ),
        _guard("hermes.available", lambda: check_hermes(config, runner)),
        _guard("lmstudio.conflict", lambda: check_lmstudio(config, runner)),
        _guard("git.head", lambda: check_git(config, runner)),
        _guard("resource.ram", lambda: check_ram(config, runner)),
        _guard("resource.vram", lambda: check_vram(config, runner)),
    )
    return PreflightReport(mode=config.mode, gates=gates)


def cli(argv: Sequence[str] | None = None, *, runner: CommandRunner | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostica, sin instalar ni iniciar servicios, el laboratorio Hermes local."
    )
    parser.add_argument("--mode", choices=("formal", "exploratory"), default="exploratory")
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--network-proof",
        choices=("unverified", "firewall-authorized"),
        default="unverified",
    )
    parser.add_argument("--firewall-proof-id")
    parser.add_argument(
        "--server-profile-proof",
        choices=("unverified", "operator-authorized"),
        default="unverified",
    )
    parser.add_argument("--server-profile-proof-id")
    parser.add_argument("--min-ram-available-gib", type=float, default=8.0)
    parser.add_argument("--min-commit-headroom-gib", type=float, default=8.0)
    parser.add_argument("--min-vram-free-mib", type=int, default=12_288)
    args = parser.parse_args(argv)

    try:
        config = PreflightConfig(
            mode=args.mode,
            ollama_base_url=args.ollama_base_url,
            network_proof=args.network_proof,
            firewall_proof_id=args.firewall_proof_id,
            server_profile_proof=args.server_profile_proof,
            server_profile_proof_id=args.server_profile_proof_id,
            min_ram_available_gib=args.min_ram_available_gib,
            min_commit_headroom_gib=args.min_commit_headroom_gib,
            min_vram_free_mib=args.min_vram_free_mib,
            lab_root=LAB_ROOT,
        )
    except ValueError:
        print("Configuracion invalida; no se ejecuto el preflight.")
        return 1

    report = run_preflight(config, runner or SubprocessCommandRunner())
    from local_code_hermes.run_log import write_preflight_report

    path = write_preflight_report(report, DEFAULT_RUNS_DIR, config)
    print(
        f"Preflight {report.outcome}; terminal={report.terminal_event}; "
        f"JSONL=.local/runs/{path.name}"
    )
    return {"passed": 0, "blocked": 2, "failed": 1}[report.outcome]


def main() -> None:
    raise SystemExit(cli())

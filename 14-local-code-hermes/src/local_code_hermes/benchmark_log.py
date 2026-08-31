"""Exportacion sanitaria de una corrida benchmark de Hermes."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

from local_code_hermes.benchmark import (
    BENCHMARK_PROFILE_ID,
    BENCHMARK_PROMPT,
    BENCHMARK_VARIANT_ID,
    HARNESS_VERSION,
    BenchmarkConfig,
    BenchmarkReport,
)
from local_code_hermes.config import (
    BENCHMARK_CASE_ID,
    LAB_ID,
    MODEL_NAME,
    NUM_CTX,
    SCHEMA_VERSION,
    SOURCE_MODEL,
    is_loopback_http_endpoint,
    is_safe_proof_id,
)
from local_code_hermes.preflight import PreflightReport
from local_code_hermes.run_log import sanitize_gate_evidence

_CODE_PATTERN = re.compile(r"[a-z0-9_]+")
_DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _safe_runs_dir(runs_dir: Path, lab_root: Path) -> Path:
    root = lab_root.resolve()
    resolved = runs_dir.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("La salida JSONL debe permanecer dentro del laboratorio.")
    return resolved


def _proof_reference(value: str | None, prefix: str) -> str | None:
    if value is None or not is_safe_proof_id(value, required_prefix=prefix):
        return None
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _model(report: BenchmarkReport, config: BenchmarkConfig) -> dict[str, object]:
    endpoint = (
        config.ollama_base_url
        if is_loopback_http_endpoint(config.ollama_base_url)
        else "http://127.0.0.1"
    )
    return {
        "provider": "ollama",
        "name": MODEL_NAME,
        "source_model": SOURCE_MODEL,
        "digest": report.model_digest,
        "context_configured": NUM_CTX,
        "endpoint": endpoint,
    }


def _event(
    *,
    run_id: str,
    sequence: int,
    event_type: str,
    model: dict[str, object],
    node: dict[str, object] | None,
    payload: dict[str, object],
    metrics: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": f"{run_id}-evt-{sequence:04d}",
        "run_id": run_id,
        "sequence": sequence,
        "timestamp": _utc_now(),
        "event_type": event_type,
        "lab_id": LAB_ID,
        "variant_id": BENCHMARK_VARIANT_ID,
        "case_id": BENCHMARK_CASE_ID,
        "model": model,
        "node": node,
        "payload": payload,
        "metrics": metrics or {},
        "artifact_refs": [],
    }


def _safe_code(value: str, *, default: str) -> str:
    return value if _CODE_PATTERN.fullmatch(value) else default


def _node_records(report: BenchmarkReport) -> tuple[dict[str, object], ...]:
    process = report.process
    fixture = report.fixture
    runtime = report.ollama_observation
    log = report.log_observation
    preflight_status = "passed" if report.preflight_outcome == "passed" else "blocked"
    hermes_status = (
        "blocked"
        if process is None
        else "failed"
        if process.timed_out or process.returncode != 0
        else "passed"
    )
    fixture_status = "blocked" if fixture is None else "passed" if fixture.passed else "failed"
    runtime_status = "passed" if runtime.get("runtime_identity_verified") is True else "blocked"
    return (
        {
            "node_id": "benchmark.preflight",
            "outcome": preflight_status,
            "code": "preflight_passed" if preflight_status == "passed" else "preflight_not_green",
            "blocking": preflight_status == "blocked",
            "evidence": {
                "preflight_outcome": report.preflight_outcome,
                "dirty_worktree_override": report.dirty_worktree_override,
            },
        },
        {
            "node_id": "benchmark.hermes",
            "outcome": hermes_status,
            "code": (
                "not_started"
                if process is None
                else "process_timeout"
                if process.timed_out
                else "process_nonzero"
                if process.returncode != 0
                else "process_completed"
            ),
            "blocking": hermes_status in {"blocked", "failed"},
            "evidence": {
                "returncode": process.returncode if process is not None else None,
                "timed_out": process.timed_out if process is not None else False,
            },
        },
        {
            "node_id": "benchmark.fixture",
            "outcome": fixture_status,
            "code": (
                "not_started"
                if fixture is None
                else "fixture_passed"
                if fixture.passed
                else "fixture_failed"
            ),
            "blocking": fixture_status in {"blocked", "failed"},
            "evidence": {
                "passed": fixture.passed if fixture is not None else False,
                "failure_count": len(fixture.codes) if fixture is not None else 0,
                "changed_file_count": len(fixture.changed_files) if fixture is not None else 0,
            },
        },
        {
            "node_id": "benchmark.runtime",
            "outcome": runtime_status,
            "code": "runtime_identity_verified"
            if runtime_status == "passed"
            else "runtime_identity_unverified",
            "blocking": runtime_status == "blocked",
            "evidence": {
                "runtime_identity_verified": bool(runtime.get("runtime_identity_verified")),
                "model_name": runtime.get("model_name"),
                "processor": runtime.get("processor"),
                "context_size": runtime.get("context_tokens"),
                "gpu_resident": runtime.get("gpu_resident"),
            },
        },
        {
            "node_id": "benchmark.observability",
            "outcome": "passed" if log.get("log_delta_observed") else "blocked",
            "code": "log_delta_observed"
            if log.get("log_delta_observed")
            else "log_delta_unobserved",
            "blocking": not bool(log.get("log_delta_observed")),
            "evidence": {
                "log_delta_observed": bool(log.get("log_delta_observed")),
                "files_observed": log.get("files_observed", 0),
                "truncation_count": log.get("truncation_count", 0),
                "http_500_count": log.get("http_500_count", 0),
            },
        },
    )


def build_benchmark_events(
    report: BenchmarkReport,
    config: BenchmarkConfig,
    preflight: PreflightReport,
) -> list[dict[str, object]]:
    """Construye lifecycle observable sin incluir prompts, salidas ni rutas."""

    if not is_loopback_http_endpoint(config.ollama_base_url):
        raise ValueError("No se exporta un endpoint que no sea loopback.")
    if report.model_digest is not None and not _DIGEST_PATTERN.fullmatch(report.model_digest):
        raise ValueError("Digest de modelo invalido.")
    model = _model(report, config)
    nodes = _node_records(report)
    events: list[dict[str, object]] = []

    def append(
        event_type: str,
        *,
        node: dict[str, object] | None,
        payload: dict[str, object],
        metrics: dict[str, object] | None = None,
    ) -> None:
        events.append(
            _event(
                run_id=report.run_id,
                sequence=len(events) + 1,
                event_type=event_type,
                model=model,
                node=node,
                payload=payload,
                metrics=metrics,
            )
        )

    runtime_context = report.ollama_observation.get("context_tokens")
    append(
        "run.started",
        node=None,
        payload={
            "mode": preflight.mode,
            "phase": "benchmark",
            "benchmark_profile_id": BENCHMARK_PROFILE_ID,
            "client_name": "Hermes",
            "client_version": report.hermes_version,
            "git_head": report.git_head,
            "configured_context_tokens": NUM_CTX,
            "effective_context_tokens": runtime_context,
            "local_inference_status": (
                "observed_loopback_model"
                if report.ollama_observation.get("runtime_identity_verified")
                else "unverified"
            ),
            "zero_egress_status": "sandbox_network_none_unverified",
            "network_evidence_ref": _proof_reference(config.network_proof_id, "FW-"),
            "server_profile_evidence_ref": _proof_reference(
                config.server_profile_proof_id,
                "OLLAMA-",
            ),
            "comparable": report.comparable,
            "scored": report.scored,
            "harness_version": HARNESS_VERSION,
            "benchmark_case_id": BENCHMARK_CASE_ID,
            "raw_content_stored": False,
            "preflight_outcome": preflight.outcome,
            "dirty_worktree_override": report.dirty_worktree_override,
            "sandbox_backend": "docker",
            "sandbox_network": "none",
            "sandbox_image_digest": report.sandbox_image_digest,
            "input_digest": "sha256:"
            + hashlib.sha256(BENCHMARK_PROMPT.encode("utf-8")).hexdigest(),
        },
    )
    for node_record in nodes:
        node = {"id": node_record["node_id"], "kind": "benchmark_node"}
        append("node.started", node=node, payload={"node_id": node_record["node_id"]})
        payload = {
            "node_id": node_record["node_id"],
            "outcome": node_record["outcome"],
            "code": node_record["code"],
            "blocking": node_record["blocking"],
            "evidence": sanitize_gate_evidence(node_record["evidence"]),
        }
        append(
            "node.failed" if node_record["blocking"] else "node.completed",
            node=node,
            payload=payload,
        )

    process = report.process
    usage = report.usage or {}
    metrics = {
        "duration_ms": process.duration_ms if process is not None else 0,
        "input_count": usage.get("prompt_tokens"),
        "output_count": usage.get("completion_tokens"),
        "total_count": usage.get("total_tokens"),
        "api_call_count": usage.get("api_calls"),
        "truncation_count": report.log_observation.get("truncation_count", 0),
        "http_500_count": report.log_observation.get("http_500_count", 0),
    }
    append(
        "run.completed" if report.outcome == "completed" else f"run.{report.outcome}",
        node=None,
        payload={
            "outcome": report.outcome,
            "reason": _safe_code(report.reason, default="unspecified"),
            "scored": report.scored,
            "comparable": report.comparable,
            "scores": report.scores,
        },
        metrics=metrics,
    )
    return events


def write_benchmark_report(
    report: BenchmarkReport,
    runs_dir: Path,
    config: BenchmarkConfig,
    preflight: PreflightReport,
) -> Path:
    destination = _safe_runs_dir(runs_dir, config.lab_root)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"benchmark-{report.run_id}.jsonl"
    temporary = destination / f".{path.name}.tmp"
    events = build_benchmark_events(report, config, preflight)
    from local_code_hermes.benchmark_validation import validate_benchmark_events

    validate_benchmark_events(events)
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(
                json.dumps(event, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
            )
            handle.write("\n")
    temporary.replace(path)
    return path

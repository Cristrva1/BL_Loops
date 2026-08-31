"""Exportacion JSONL sanitaria del preflight."""

from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from local_code_hermes.config import (
    BENCHMARK_CASE_ID,
    LAB_ID,
    MODEL_NAME,
    NUM_CTX,
    PREFLIGHT_CASE_ID,
    REQUIRED_GATE_IDS,
    SCHEMA_VERSION,
    SOURCE_MODEL,
    VARIANT_ID,
    PreflightConfig,
    is_loopback_http_endpoint,
    is_safe_proof_id,
)
from local_code_hermes.preflight import GateResult, PreflightReport

HARNESS_VERSION = "0.1.0"
BENCHMARK_PROFILE_ID = "local-code-ollama-64k"
COMMON_FIELDS = (
    "schema_version",
    "event_id",
    "run_id",
    "sequence",
    "timestamp",
    "event_type",
    "lab_id",
    "variant_id",
    "case_id",
    "model",
    "node",
    "payload",
    "metrics",
    "artifact_refs",
)
FORBIDDEN_EVIDENCE_KEY_PARTS = (
    "authorization",
    "credential",
    "email",
    "password",
    "path",
    "prompt",
    "secret",
    "stderr",
    "stdout",
    "token",
)
EMAIL_PATTERN = re.compile(r"(?i)(?<![\w.-])[\w.+-]+@[\w.-]+\.[a-z]{2,}")
URL_CREDENTIAL_PATTERN = re.compile(r"://[^/\s:@]+:[^/\s@]+@")
WINDOWS_PATH_PATTERN = re.compile(r"(?i)(?:^|\s)(?:[a-z]:[\\/]|\\\\)")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _safe_runs_dir(runs_dir: Path, lab_root: Path) -> Path:
    root = lab_root.resolve()
    resolved = runs_dir.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("La salida JSONL debe permanecer dentro del laboratorio.")
    return resolved


def _model(config: PreflightConfig) -> dict[str, object]:
    endpoint = (
        config.ollama_base_url
        if is_loopback_http_endpoint(config.ollama_base_url)
        else "http://127.0.0.1"
    )
    return {
        "provider": "ollama",
        "name": MODEL_NAME,
        "source_model": SOURCE_MODEL,
        "digest": None,
        "context_configured": NUM_CTX,
        "endpoint": endpoint,
    }


def _proof_reference(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def sanitize_gate_evidence(value: object, *, location: str = "evidence") -> object:
    """Copia solo evidencia estructurada que no pueda contener contenido sensible."""

    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"Clave de evidencia invalida en {location}.")
            normalized = key.casefold().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN_EVIDENCE_KEY_PARTS):
                raise ValueError(f"Campo sensible no permitido en {location}.")
            sanitized[key] = sanitize_gate_evidence(item, location=f"{location}.{key}")
        return sanitized
    if isinstance(value, list):
        return [
            sanitize_gate_evidence(item, location=f"{location}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        if (
            EMAIL_PATTERN.search(value)
            or URL_CREDENTIAL_PATTERN.search(value)
            or WINDOWS_PATH_PATTERN.search(value)
            or value.startswith("/")
        ):
            raise ValueError(f"Valor sensible no permitido en {location}.")
        return value
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError(f"Tipo de evidencia no permitido en {location}.")


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
        "variant_id": VARIANT_ID,
        "case_id": PREFLIGHT_CASE_ID,
        "model": model,
        "node": node,
        "payload": payload,
        "metrics": metrics or {},
        "artifact_refs": [],
    }


def _gate_payload(gate: GateResult) -> dict[str, object]:
    return {
        "gate_id": gate.gate_id,
        "outcome": gate.outcome,
        "code": gate.code,
        "blocking": gate.blocking,
        "evidence": sanitize_gate_evidence(gate.evidence),
    }


def _validate_report(report: PreflightReport) -> None:
    if report.mode not in {"formal", "exploratory"}:
        raise ValueError("Modo de reporte invalido.")
    if tuple(gate.gate_id for gate in report.gates) != REQUIRED_GATE_IDS:
        raise ValueError("El reporte no contiene exactamente los gates requeridos en orden.")
    for gate in report.gates:
        if gate.blocking is not (gate.outcome in {"blocked", "failed"}):
            raise ValueError(f"Gate inconsistente: {gate.gate_id}.")
        if not re.fullmatch(r"[a-z0-9_]+", gate.code):
            raise ValueError(f"Codigo de gate invalido: {gate.gate_id}.")
        sanitize_gate_evidence(gate.evidence)


def build_preflight_events(
    report: PreflightReport,
    config: PreflightConfig,
    *,
    run_id: str,
) -> list[dict[str, object]]:
    """Convierte resultados ya sanitizados en eventos observables."""

    _validate_report(report)
    model = _model(config)
    events: list[dict[str, object]] = []
    hermes_version = next(
        (
            gate.evidence.get("version")
            for gate in report.gates
            if gate.gate_id == "hermes.available" and gate.outcome == "passed"
        ),
        None,
    )
    git_head = next(
        (
            gate.evidence.get("head")
            for gate in report.gates
            if gate.gate_id == "git.head" and gate.outcome == "passed"
        ),
        None,
    )
    network_evidence_ref = (
        _proof_reference(config.firewall_proof_id)
        if config.network_proof == "firewall-authorized"
        and is_safe_proof_id(config.firewall_proof_id, required_prefix="FW-")
        else None
    )
    server_profile_evidence_ref = (
        _proof_reference(config.server_profile_proof_id)
        if config.server_profile_proof == "operator-authorized"
        and is_safe_proof_id(
            config.server_profile_proof_id,
            required_prefix="OLLAMA-",
        )
        else None
    )

    def append(
        event_type: str,
        *,
        node: dict[str, object] | None,
        payload: dict[str, object],
        metrics: dict[str, object] | None = None,
    ) -> None:
        events.append(
            _event(
                run_id=run_id,
                sequence=len(events) + 1,
                event_type=event_type,
                model=model,
                node=node,
                payload=payload,
                metrics=metrics,
            )
        )

    append(
        "run.started",
        node=None,
        payload={
            "mode": report.mode,
            "benchmark_profile_id": BENCHMARK_PROFILE_ID,
            "phase": "preflight",
            "client_name": "Hermes",
            "client_version": hermes_version,
            "git_head": git_head,
            "configured_context_tokens": config.expected_num_ctx,
            "effective_context_tokens": None,
            "local_inference_status": "configured_loopback_unverified",
            "zero_egress_status": "unverified",
            "network_evidence_ref": network_evidence_ref,
            "server_profile_evidence_ref": server_profile_evidence_ref,
            "comparable": False,
            "scored": False,
            "harness_version": HARNESS_VERSION,
            "benchmark_case_id": BENCHMARK_CASE_ID,
            "raw_content_stored": False,
        },
    )
    for gate in report.gates:
        node = {"id": gate.gate_id, "kind": "preflight_gate"}
        append(
            "node.started",
            node=node,
            payload={"gate_id": gate.gate_id},
        )
        append(
            "node.failed" if gate.blocking else "node.completed",
            node=node,
            payload=_gate_payload(gate),
        )

    counts = Counter(gate.outcome for gate in report.gates)
    append(
        report.terminal_event,
        node=None,
        payload={
            "outcome": report.outcome,
            "scored": False,
            "comparable": False,
            "gate_counts": dict(sorted(counts.items())),
        },
        metrics={"gate_total": len(report.gates)},
    )
    return events


def write_preflight_report(
    report: PreflightReport,
    runs_dir: Path,
    config: PreflightConfig,
) -> Path:
    """Escribe de forma atomica; nunca incluye stdout, stderr, prompts ni secretos."""

    destination = _safe_runs_dir(runs_dir, config.lab_root)
    destination.mkdir(parents=True, exist_ok=True)
    run_id = f"run-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    path = destination / f"preflight-{run_id}.jsonl"
    temporary = destination / f".{path.name}.tmp"
    events = build_preflight_events(report, config, run_id=run_id)
    from local_code_hermes.validation import validate_events

    validate_events(events)
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(
                json.dumps(
                    event,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                )
            )
            handle.write("\n")
    temporary.replace(path)
    return path

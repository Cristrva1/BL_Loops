"""Validador estricto del lifecycle JSONL del benchmark B-CODE-003."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from local_code_hermes.config import (
    BENCHMARK_CASE_ID,
    LAB_ID,
    MODEL_NAME,
    NUM_CTX,
    SCHEMA_VERSION,
    SOURCE_MODEL,
    is_loopback_http_endpoint,
)
from local_code_hermes.run_log import COMMON_FIELDS, sanitize_gate_evidence

BENCHMARK_VARIANT_ID = "ollama-hermes-benchmark"
EVENT_TYPES = {
    "run.started",
    "node.started",
    "node.completed",
    "node.failed",
    "run.completed",
    "run.blocked",
    "run.failed",
}
NODE_IDS = (
    "benchmark.preflight",
    "benchmark.hermes",
    "benchmark.fixture",
    "benchmark.runtime",
    "benchmark.observability",
)
SEMVER_PATTERN = re.compile(r"\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?")
DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
HEAD_PATTERN = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
FORBIDDEN_KEYS = {
    "response",
    "content",
    "prompt",
    "prompt_text",
    "stdout",
    "stderr",
    "secret",
    "password",
    "api_key",
    "token_value",
}


class ValidationError(ValueError):
    """El JSONL no cumple el contrato del benchmark."""


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"Clave JSON duplicada: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    raise ValidationError(f"Constante JSON no valida: {value}")


def _parse_line(line: str, line_number: int) -> dict[str, object]:
    try:
        value = json.loads(
            line,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValidationError(f"Linea {line_number}: JSON invalido.") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Linea {line_number}: se esperaba un objeto.")
    return value


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} debe ser texto no vacio.")
    return value


def _nonnegative_int(value: object, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{field} debe ser entero no negativo.")


def _optional_nonnegative_int(value: object, field: str) -> None:
    if value is not None:
        _nonnegative_int(value, field)


def _validate_timestamp(value: object) -> None:
    text = _text(value, "timestamp")
    if not text.endswith("Z"):
        raise ValidationError("timestamp debe terminar en Z.")
    try:
        datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError("timestamp invalido.") from exc


def _validate_model(value: object) -> None:
    if not isinstance(value, dict):
        raise ValidationError("model debe ser objeto.")
    if set(value) != {
        "provider",
        "name",
        "source_model",
        "digest",
        "context_configured",
        "endpoint",
    }:
        raise ValidationError("Campos de model incorrectos.")
    if value["provider"] != "ollama" or value["name"] != MODEL_NAME:
        raise ValidationError("Identidad de modelo incorrecta.")
    if value["source_model"] != SOURCE_MODEL:
        raise ValidationError("Modelo fuente incorrecto.")
    if value["digest"] is not None and (
        not isinstance(value["digest"], str) or not DIGEST_PATTERN.fullmatch(value["digest"])
    ):
        raise ValidationError("Digest de modelo invalido.")
    if value["context_configured"] != NUM_CTX:
        raise ValidationError("Contexto configurado incorrecto.")
    if not isinstance(value["endpoint"], str) or not is_loopback_http_endpoint(value["endpoint"]):
        raise ValidationError("Endpoint de modelo no local.")


def _validate_no_raw_keys(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key.casefold() in FORBIDDEN_KEYS:
                raise ValidationError("El evento contiene una clave de contenido crudo.")
            _validate_no_raw_keys(item)
    elif isinstance(value, list):
        for item in value:
            _validate_no_raw_keys(item)


def _validate_event_shape(event: dict[str, object]) -> None:
    if set(event) != set(COMMON_FIELDS):
        raise ValidationError("Campos de evento incorrectos.")
    if event["schema_version"] != SCHEMA_VERSION:
        raise ValidationError("schema_version no soportada.")
    if event["lab_id"] != LAB_ID or event["case_id"] != BENCHMARK_CASE_ID:
        raise ValidationError("Identidad de laboratorio o caso incorrecta.")
    if event["variant_id"] != BENCHMARK_VARIANT_ID:
        raise ValidationError("variant_id incorrecto.")
    for field in ("event_id", "run_id", "event_type", "variant_id"):
        _text(event[field], field)
    if event["event_type"] not in EVENT_TYPES:
        raise ValidationError("event_type no reconocido.")
    _nonnegative_int(event["sequence"], "sequence")
    if event["sequence"] == 0:
        raise ValidationError("sequence debe iniciar en uno.")
    _validate_timestamp(event["timestamp"])
    _validate_model(event["model"])
    if event["node"] is not None and not isinstance(event["node"], dict):
        raise ValidationError("node debe ser objeto o null.")
    if not isinstance(event["payload"], dict):
        raise ValidationError("payload debe ser objeto.")
    if not isinstance(event["metrics"], dict):
        raise ValidationError("metrics debe ser objeto.")
    if event["artifact_refs"] != []:
        raise ValidationError("No se permiten artefactos en esta corrida.")
    _validate_no_raw_keys(event["payload"])
    _validate_no_raw_keys(event["metrics"])


def _validate_reference(value: object) -> None:
    if value is not None and (not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value)):
        raise ValidationError("Referencia de evidencia invalida.")


def _validate_started(event: dict[str, object]) -> None:
    if event["node"] is not None or event["metrics"] != {}:
        raise ValidationError("run.started contiene node o metrics.")
    payload = event["payload"]
    assert isinstance(payload, dict)
    required = {
        "mode",
        "phase",
        "benchmark_profile_id",
        "client_name",
        "client_version",
        "git_head",
        "configured_context_tokens",
        "effective_context_tokens",
        "local_inference_status",
        "zero_egress_status",
        "network_evidence_ref",
        "server_profile_evidence_ref",
        "comparable",
        "scored",
        "harness_version",
        "benchmark_case_id",
        "raw_content_stored",
        "preflight_outcome",
        "dirty_worktree_override",
        "sandbox_backend",
        "sandbox_network",
        "sandbox_image_digest",
        "input_digest",
    }
    if set(payload) != required:
        raise ValidationError("Payload run.started incorrecto.")
    if payload["mode"] != "formal" or payload["phase"] != "benchmark":
        raise ValidationError("El benchmark exige modo formal.")
    if payload["benchmark_profile_id"] != "local-code-ollama-64k":
        raise ValidationError("Perfil de benchmark incorrecto.")
    if payload["client_name"] != "Hermes":
        raise ValidationError("Cliente benchmark incorrecto.")
    if payload["client_version"] is not None and (
        not isinstance(payload["client_version"], str)
        or not SEMVER_PATTERN.fullmatch(payload["client_version"])
    ):
        raise ValidationError("Version Hermes invalida.")
    if payload["git_head"] is not None and (
        not isinstance(payload["git_head"], str) or not HEAD_PATTERN.fullmatch(payload["git_head"])
    ):
        raise ValidationError("HEAD invalido.")
    if payload["configured_context_tokens"] != NUM_CTX:
        raise ValidationError("Contexto benchmark incorrecto.")
    effective = payload["effective_context_tokens"]
    if effective is not None:
        _nonnegative_int(effective, "effective_context_tokens")
    if payload["local_inference_status"] not in {"observed_loopback_model", "unverified"}:
        raise ValidationError("Estado de inferencia local invalido.")
    if payload["zero_egress_status"] != "sandbox_network_none_unverified":
        raise ValidationError("El benchmark no puede afirmar zero egress.")
    _validate_reference(payload["network_evidence_ref"])
    _validate_reference(payload["server_profile_evidence_ref"])
    for field in ("comparable", "scored", "raw_content_stored", "dirty_worktree_override"):
        if not isinstance(payload[field], bool):
            raise ValidationError(f"{field} debe ser booleano.")
    if payload["scored"] and not payload["comparable"]:
        raise ValidationError("Una corrida puntuada debe ser comparable.")
    if payload["harness_version"] != "0.2.0":
        raise ValidationError("Version de harness incorrecta.")
    if payload["benchmark_case_id"] != BENCHMARK_CASE_ID:
        raise ValidationError("Caso benchmark incorrecto.")
    if payload["raw_content_stored"] is not False:
        raise ValidationError("No se permite contenido crudo.")
    if payload["preflight_outcome"] not in {"passed", "blocked", "failed"}:
        raise ValidationError("Outcome de preflight incorrecto.")
    if payload["sandbox_backend"] != "docker" or payload["sandbox_network"] != "none":
        raise ValidationError("Sandbox benchmark incorrecto.")
    _validate_reference(payload["sandbox_image_digest"])
    if not isinstance(payload["input_digest"], str) or not DIGEST_PATTERN.fullmatch(
        payload["input_digest"]
    ):
        raise ValidationError("Digest de entrada invalido.")


def _validate_evidence(evidence: object) -> None:
    if not isinstance(evidence, dict):
        raise ValidationError("Evidencia benchmark no estructurada.")
    try:
        sanitize_gate_evidence(evidence)
    except ValueError as exc:
        raise ValidationError("Evidencia benchmark no sanitaria.") from exc


def _validate_nodes(events: list[dict[str, object]]) -> None:
    middle = events[1:-1]
    if len(middle) != len(NODE_IDS) * 2:
        raise ValidationError("Lifecycle benchmark incompleto.")
    for index, node_id in enumerate(NODE_IDS):
        started = middle[index * 2]
        finished = middle[index * 2 + 1]
        node = {"id": node_id, "kind": "benchmark_node"}
        if started["event_type"] != "node.started" or started["node"] != node:
            raise ValidationError(f"Inicio de nodo invalido: {node_id}.")
        if started["payload"] != {"node_id": node_id} or started["metrics"] != {}:
            raise ValidationError(f"Payload de inicio invalido: {node_id}.")
        if finished["node"] != node:
            raise ValidationError(f"Nodo terminal invalido: {node_id}.")
        payload = finished["payload"]
        if not isinstance(payload, dict) or set(payload) != {
            "node_id",
            "outcome",
            "code",
            "blocking",
            "evidence",
        }:
            raise ValidationError(f"Payload de nodo invalido: {node_id}.")
        if payload["node_id"] != node_id or payload["outcome"] not in {
            "passed",
            "blocked",
            "failed",
        }:
            raise ValidationError(f"Outcome de nodo invalido: {node_id}.")
        if not isinstance(payload["blocking"], bool):
            raise ValidationError(f"Blocking de nodo invalido: {node_id}.")
        if payload["blocking"] is not (payload["outcome"] in {"blocked", "failed"}):
            raise ValidationError(f"Blocking inconsistente: {node_id}.")
        expected_event = "node.failed" if payload["blocking"] else "node.completed"
        if finished["event_type"] != expected_event:
            raise ValidationError(f"Evento de nodo inconsistente: {node_id}.")
        if not isinstance(payload["code"], str) or not re.fullmatch(r"[a-z0-9_]+", payload["code"]):
            raise ValidationError(f"Codigo de nodo invalido: {node_id}.")
        _validate_evidence(payload["evidence"])
        if finished["metrics"] != {}:
            raise ValidationError(f"Metrics inesperadas en nodo: {node_id}.")


def _validate_metric_value(value: object, field: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"Metric {field} invalida.")


def _validate_terminal(event: dict[str, object]) -> str:
    if event["node"] is not None or event["artifact_refs"] != []:
        raise ValidationError("Terminal benchmark contiene datos inesperados.")
    payload = event["payload"]
    if not isinstance(payload, dict) or set(payload) != {
        "outcome",
        "reason",
        "scored",
        "comparable",
        "scores",
    }:
        raise ValidationError("Payload terminal benchmark incorrecto.")
    outcome = payload["outcome"]
    if outcome not in {"completed", "blocked", "failed"}:
        raise ValidationError("Outcome terminal benchmark incorrecto.")
    expected_event = "run.completed" if outcome == "completed" else f"run.{outcome}"
    if event["event_type"] != expected_event:
        raise ValidationError("Evento terminal no coincide con outcome.")
    if not isinstance(payload["reason"], str) or not re.fullmatch(r"[a-z0-9_]+", payload["reason"]):
        raise ValidationError("Reason terminal invalido.")
    for field in ("scored", "comparable"):
        if not isinstance(payload[field], bool):
            raise ValidationError(f"{field} terminal debe ser booleano.")
    if payload["scored"] and not payload["comparable"]:
        raise ValidationError("Terminal puntuada no comparable.")
    scores = payload["scores"]
    if not isinstance(scores, dict):
        raise ValidationError("Scores terminales invalidos.")
    for value in scores.values():
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or not 0 <= float(value) <= 100
        ):
            raise ValidationError("Valor de score invalido.")

    metrics = event["metrics"]
    if set(metrics) != {
        "duration_ms",
        "input_count",
        "output_count",
        "total_count",
        "api_call_count",
        "truncation_count",
        "http_500_count",
    }:
        raise ValidationError("Metrics terminales incorrectas.")
    for field in metrics:
        _validate_metric_value(metrics[field], field)
    return str(outcome)


def validate_benchmark_events(events: list[dict[str, object]]) -> dict[str, object]:
    if not events:
        raise ValidationError("El JSONL benchmark esta vacio.")
    event_ids: set[str] = set()
    run_ids: set[str] = set()
    model_values: set[str] = set()
    for index, event in enumerate(events, start=1):
        _validate_event_shape(event)
        if event["sequence"] != index:
            raise ValidationError("sequence no es consecutiva.")
        event_id = str(event["event_id"])
        if event_id in event_ids:
            raise ValidationError("event_id duplicado.")
        event_ids.add(event_id)
        run_ids.add(str(event["run_id"]))
        model_values.add(json.dumps(event["model"], sort_keys=True, separators=(",", ":")))
    if len(run_ids) != 1 or len(model_values) != 1:
        raise ValidationError("La corrida mezcla identidades.")
    if events[0]["event_type"] != "run.started":
        raise ValidationError("El primer evento debe ser run.started.")
    if sum(event["event_type"] == "run.started" for event in events) != 1:
        raise ValidationError("Debe existir un unico run.started.")
    if events[-1]["event_type"] not in {"run.completed", "run.blocked", "run.failed"}:
        raise ValidationError("Falta terminal benchmark.")
    _validate_started(events[0])
    _validate_nodes(events)
    outcome = _validate_terminal(events[-1])
    return {
        "run_id": next(iter(run_ids)),
        "event_count": len(events),
        "terminal_event": str(events[-1]["event_type"]),
        "outcome": outcome,
    }


def validate_path(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValidationError("La ruta JSONL benchmark no existe.")
    data = path.read_bytes().decode("utf-8", errors="strict")
    if not data or not data.endswith("\n"):
        raise ValidationError("El JSONL benchmark debe ser UTF-8 y terminar con newline.")
    lines = data.splitlines()
    if any(not line.strip() for line in lines):
        raise ValidationError("El JSONL benchmark no admite lineas vacias.")
    return validate_benchmark_events(
        [_parse_line(line, index) for index, line in enumerate(lines, start=1)]
    )

"""Validador stdlib estricto para el JSONL 1.1 de este laboratorio."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from local_code_hermes.config import (
    LAB_ID,
    MODEL_NAME,
    NUM_CTX,
    PREFLIGHT_CASE_ID,
    REQUIRED_GATE_IDS,
    SCHEMA_VERSION,
    SOURCE_MODEL,
    VARIANT_ID,
    is_loopback_http_endpoint,
)
from local_code_hermes.run_log import COMMON_FIELDS, sanitize_gate_evidence

TERMINAL_EVENTS = {"run.completed", "run.failed", "run.blocked"}
EVENT_TYPES = {
    "run.started",
    "node.started",
    "node.completed",
    "node.failed",
    *TERMINAL_EVENTS,
}
EXPECTED_SERVER_PROFILE = {
    "flash_attention": "1",
    "kv_cache_type": "q8_0",
    "num_parallel": "1",
    "max_loaded_models": "1",
    "no_cloud": "1",
}
PASSED_CODES = {
    "python.runtime": "python_3_12",
    "network.endpoint": "loopback_http",
    "network.firewall": "authorized_firewall_proof",
    "ollama.server_profile": "operator_profile_evidence_referenced",
    "ollama.model": "model_identity_verified",
    "hermes.available": "version_captured",
    "git.head": "head_captured",
    "resource.ram": "ram_headroom_recorded",
    "resource.vram": "vram_headroom_recorded",
}
BLOCKED_CODES = {
    "python.runtime": {"python_version_mismatch"},
    "network.endpoint": {"endpoint_not_loopback"},
    "network.firewall": {"invalid_firewall_proof_id", "locality_unproven"},
    "ollama.server_profile": {
        "invalid_server_profile_proof_id",
        "server_profile_unproven",
    },
    "ollama.model": {
        "endpoint_not_approved",
        "model_name_mismatch",
        "model_contract_unreadable",
        "model_contract_unparseable",
        "model_contract_source_mismatch",
        "model_contract_num_ctx_mismatch",
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "runtime_modelfile_unparseable",
        "source_model_unavailable",
        "source_modelfile_unparseable",
        "num_ctx_mismatch",
        "source_weights_mismatch",
    },
    "hermes.available": {
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "version_not_captured",
    },
    "lmstudio.conflict": {
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "lmstudio_state_unknown",
        "lmstudio_model_process_observed",
        "lmstudio_model_loaded",
    },
    "git.head": {
        "head_absent_formal",
        "head_not_exact",
        "command_not_found",
        "command_timeout",
        "command_nonzero",
    },
    "resource.ram": {
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "ram_evidence_invalid",
        "ram_headroom_low",
    },
    "resource.vram": {
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "vram_evidence_invalid",
        "vram_headroom_low",
    },
}
WARNING_CODES = {
    "network.firewall": "locality_unproven_exploratory",
    "ollama.server_profile": "server_profile_unproven_exploratory",
    "git.head": "head_absent_exploratory",
}


class ValidationError(ValueError):
    """El archivo no cumple el contrato del laboratorio."""


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
        raise ValidationError(f"Linea {line_number}: JSON invalido: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Linea {line_number}: se esperaba un objeto JSON.")
    return value


def _non_empty_string(value: object, field: str, line_number: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Linea {line_number}: {field} debe ser texto no vacio.")
    return value


def _validate_timestamp(value: object, line_number: int) -> None:
    text = _non_empty_string(value, "timestamp", line_number)
    if not text.endswith("Z"):
        raise ValidationError(f"Linea {line_number}: timestamp debe estar en UTC y terminar en Z.")
    try:
        datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError(f"Linea {line_number}: timestamp invalido.") from exc


def _validate_model(value: object, line_number: int) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"Linea {line_number}: model debe ser objeto.")
    required = {
        "provider",
        "name",
        "source_model",
        "digest",
        "context_configured",
        "endpoint",
    }
    if set(value) != required:
        raise ValidationError(f"Linea {line_number}: campos de model incorrectos.")
    if value["provider"] != "ollama":
        raise ValidationError(f"Linea {line_number}: provider debe ser ollama.")
    if value["name"] != MODEL_NAME or value["source_model"] != SOURCE_MODEL:
        raise ValidationError(f"Linea {line_number}: identidad de modelo incorrecta.")
    context = value["context_configured"]
    if isinstance(context, bool) or not isinstance(context, int) or context != NUM_CTX:
        raise ValidationError(f"Linea {line_number}: contexto invalido.")
    if value["digest"] is not None:
        raise ValidationError(f"Linea {line_number}: el preflight no conoce el digest.")
    if not isinstance(value["endpoint"], str) or not is_loopback_http_endpoint(value["endpoint"]):
        raise ValidationError(f"Linea {line_number}: endpoint no local.")


def _validate_event(event: dict[str, object], line_number: int) -> None:
    if set(event) != set(COMMON_FIELDS):
        missing = sorted(set(COMMON_FIELDS) - set(event))
        extra = sorted(set(event) - set(COMMON_FIELDS))
        raise ValidationError(
            f"Linea {line_number}: campos incorrectos; faltan={missing}; sobran={extra}."
        )
    if event["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(f"Linea {line_number}: schema_version no soportada.")
    if event["lab_id"] != LAB_ID:
        raise ValidationError(f"Linea {line_number}: lab_id incorrecto.")
    if event["case_id"] != PREFLIGHT_CASE_ID:
        raise ValidationError(f"Linea {line_number}: case_id no reconocido.")
    if event["variant_id"] != VARIANT_ID:
        raise ValidationError(f"Linea {line_number}: variant_id incorrecto.")
    for field in ("event_id", "run_id", "event_type", "variant_id"):
        _non_empty_string(event[field], field, line_number)
    if event["event_type"] not in EVENT_TYPES:
        raise ValidationError(f"Linea {line_number}: event_type no reconocido.")
    sequence = event["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= 0:
        raise ValidationError(f"Linea {line_number}: sequence debe ser entero positivo.")
    _validate_timestamp(event["timestamp"], line_number)
    _validate_model(event["model"], line_number)
    if event["node"] is not None and not isinstance(event["node"], dict):
        raise ValidationError(f"Linea {line_number}: node debe ser objeto o null.")
    if not isinstance(event["payload"], dict):
        raise ValidationError(f"Linea {line_number}: payload debe ser objeto.")
    if not isinstance(event["metrics"], dict):
        raise ValidationError(f"Linea {line_number}: metrics debe ser objeto.")
    if not isinstance(event["artifact_refs"], list):
        raise ValidationError(f"Linea {line_number}: artifact_refs debe ser array.")


def _exact_evidence(evidence: dict[str, object], expected: dict[str, object], gate_id: str) -> None:
    if evidence != expected:
        raise ValidationError(f"Evidencia de {gate_id} no coincide con su contrato.")


def _number(value: object, field: str, gate_id: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} invalido en {gate_id}.")
    return float(value)


def _validate_ram_evidence(evidence: dict[str, object], *, expect_enough: bool) -> None:
    required = {
        "total_gib",
        "available_gib",
        "minimum_available_gib",
        "commit_limit_gib",
        "commit_headroom_gib",
        "minimum_commit_headroom_gib",
        "pagefile_used_mib",
    }
    if set(evidence) != required:
        raise ValidationError("Campos de evidencia RAM incorrectos.")
    total = _number(evidence["total_gib"], "total_gib", "resource.ram")
    available = _number(evidence["available_gib"], "available_gib", "resource.ram")
    minimum_available = _number(
        evidence["minimum_available_gib"], "minimum_available_gib", "resource.ram"
    )
    commit_limit = _number(evidence["commit_limit_gib"], "commit_limit_gib", "resource.ram")
    commit_headroom = _number(
        evidence["commit_headroom_gib"], "commit_headroom_gib", "resource.ram"
    )
    minimum_commit = _number(
        evidence["minimum_commit_headroom_gib"],
        "minimum_commit_headroom_gib",
        "resource.ram",
    )
    pagefile = evidence["pagefile_used_mib"]
    if (
        total <= 0
        or available < 0
        or available > total
        or minimum_available < 0
        or commit_limit <= 0
        or commit_headroom < 0
        or commit_headroom > commit_limit
        or minimum_commit < 0
        or isinstance(pagefile, bool)
        or not isinstance(pagefile, int)
        or pagefile < 0
    ):
        raise ValidationError("Valores de evidencia RAM imposibles.")
    enough = available >= minimum_available and commit_headroom >= minimum_commit
    if enough is not expect_enough:
        raise ValidationError("El outcome RAM no coincide con sus umbrales.")


def _validate_vram_evidence(evidence: dict[str, object], *, expect_enough: bool) -> None:
    required = {
        "gpu_count",
        "selected_total_mib",
        "selected_free_mib",
        "minimum_free_mib",
    }
    if set(evidence) != required:
        raise ValidationError("Campos de evidencia VRAM incorrectos.")
    values = {field: evidence[field] for field in required}
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values.values()):
        raise ValidationError("Tipos de evidencia VRAM incorrectos.")
    gpu_count = int(values["gpu_count"])
    total = int(values["selected_total_mib"])
    free = int(values["selected_free_mib"])
    minimum = int(values["minimum_free_mib"])
    if gpu_count <= 0 or total <= 0 or free < 0 or free > total or minimum < 0:
        raise ValidationError("Valores de evidencia VRAM imposibles.")
    if (free >= minimum) is not expect_enough:
        raise ValidationError("El outcome VRAM no coincide con su umbral.")


def _validate_passed_gate(
    gate_id: str,
    code: str,
    evidence: dict[str, object],
    *,
    model_endpoint: str,
) -> None:
    if gate_id == "lmstudio.conflict":
        if code == "no_lmstudio_model_loaded":
            _exact_evidence(evidence, {"loaded_model_count": 0}, gate_id)
            return
        if code == "lms_absent_no_model_process_observed":
            _exact_evidence(
                evidence,
                {"loaded_model_count": 0, "method": "process_fallback"},
                gate_id,
            )
            return
        raise ValidationError("Codigo passed invalido para lmstudio.conflict.")
    if PASSED_CODES.get(gate_id) != code:
        raise ValidationError(f"Codigo passed invalido para {gate_id}.")
    if gate_id == "python.runtime":
        _exact_evidence(evidence, {"major": 3, "minor": 12}, gate_id)
    elif gate_id == "network.endpoint":
        _exact_evidence(evidence, {"endpoint": model_endpoint}, gate_id)
    elif gate_id == "network.firewall":
        _exact_evidence(
            evidence,
            {"proof_present": True, "method": "authorized_firewall"},
            gate_id,
        )
    elif gate_id == "ollama.server_profile":
        _exact_evidence(
            evidence,
            {"proof_present": True, "expected": EXPECTED_SERVER_PROFILE},
            gate_id,
        )
    elif gate_id == "ollama.model":
        _exact_evidence(
            evidence,
            {
                "model_name": MODEL_NAME,
                "source_model": SOURCE_MODEL,
                "num_ctx": NUM_CTX,
                "contract_verified": True,
                "weights_match": True,
            },
            gate_id,
        )
    elif gate_id == "hermes.available":
        if (
            set(evidence) != {"version"}
            or not isinstance(evidence["version"], str)
            or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?", evidence["version"])
        ):
            raise ValidationError("Evidencia de version Hermes invalida.")
    elif gate_id == "git.head":
        if (
            set(evidence) != {"head"}
            or not isinstance(evidence["head"], str)
            or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", evidence["head"])
        ):
            raise ValidationError("Evidencia HEAD invalida.")
    elif gate_id == "resource.ram":
        _validate_ram_evidence(evidence, expect_enough=True)
    elif gate_id == "resource.vram":
        _validate_vram_evidence(evidence, expect_enough=True)


def _validate_gate_contract(
    gate_id: str,
    outcome: str,
    code: str,
    evidence: dict[str, object],
    *,
    mode: str,
    model_endpoint: str,
) -> None:
    if outcome == "passed":
        _validate_passed_gate(gate_id, code, evidence, model_endpoint=model_endpoint)
        return
    if outcome == "warning":
        if mode != "exploratory" or WARNING_CODES.get(gate_id) != code:
            raise ValidationError(f"Warning no permitido para {gate_id} en modo {mode}.")
        if gate_id == "network.firewall":
            _exact_evidence(evidence, {"proof_present": False}, gate_id)
        elif gate_id == "ollama.server_profile":
            _exact_evidence(
                evidence,
                {"proof_present": False, "expected": EXPECTED_SERVER_PROFILE},
                gate_id,
            )
        elif gate_id == "git.head":
            _exact_evidence(evidence, {}, gate_id)
        return
    if outcome == "failed":
        if code != "internal_check_error" or evidence:
            raise ValidationError(f"Fallo interno invalido para {gate_id}.")
        return
    if outcome != "blocked" or code not in BLOCKED_CODES.get(gate_id, set()):
        raise ValidationError(f"Bloqueo no reconocido para {gate_id}.")
    if code in {
        "command_not_found",
        "command_timeout",
        "command_nonzero",
        "source_model_unavailable",
    }:
        if (
            set(evidence) != {"returncode"}
            or isinstance(evidence["returncode"], bool)
            or not isinstance(evidence["returncode"], int)
        ):
            raise ValidationError(f"Evidencia de comando invalida para {gate_id}.")
    elif code == "ram_headroom_low":
        _validate_ram_evidence(evidence, expect_enough=False)
    elif code == "vram_headroom_low":
        _validate_vram_evidence(evidence, expect_enough=False)
    elif code in {"lmstudio_model_loaded", "lmstudio_model_process_observed"}:
        count = evidence.get("loaded_model_count")
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValidationError("Conteo LM Studio invalido.")


def _validate_started_payload(event: dict[str, object]) -> None:
    payload = event["payload"]
    assert isinstance(payload, dict)
    required = {
        "mode",
        "benchmark_profile_id",
        "phase",
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
    }
    if set(payload) != required:
        raise ValidationError("run.started no tiene el payload exacto del preflight.")
    if payload["mode"] not in {"formal", "exploratory"}:
        raise ValidationError("Modo de preflight invalido.")
    if payload["benchmark_profile_id"] != "local-code-ollama-64k":
        raise ValidationError("Perfil de benchmark incorrecto.")
    if payload["phase"] != "preflight" or payload["client_name"] != "Hermes":
        raise ValidationError("Identidad de fase o cliente incorrecta.")
    client_version = payload["client_version"]
    if client_version is not None and (
        not isinstance(client_version, str)
        or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?", client_version)
    ):
        raise ValidationError("Version de Hermes invalida.")
    git_head = payload["git_head"]
    if git_head is not None and (
        not isinstance(git_head, str)
        or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", git_head)
    ):
        raise ValidationError("HEAD invalido en run.started.")
    context = payload["configured_context_tokens"]
    if isinstance(context, bool) or not isinstance(context, int) or context != NUM_CTX:
        raise ValidationError("Contexto configurado invalido.")
    if payload["effective_context_tokens"] is not None:
        raise ValidationError("El preflight inicial no puede afirmar contexto efectivo.")
    if payload["local_inference_status"] != "configured_loopback_unverified":
        raise ValidationError("Estado de inferencia local invalido.")
    if payload["zero_egress_status"] != "unverified":
        raise ValidationError("El preflight no puede afirmar zero egress.")
    for field in ("network_evidence_ref", "server_profile_evidence_ref"):
        proof_ref = payload[field]
        if proof_ref is not None and (
            not isinstance(proof_ref, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", proof_ref)
        ):
            raise ValidationError(f"Referencia de evidencia invalida: {field}.")
    for field in ("comparable", "scored", "raw_content_stored"):
        if payload[field] is not False:
            raise ValidationError(f"{field} debe ser false en el preflight.")
    if payload["harness_version"] != "0.1.0":
        raise ValidationError("Version de harness incorrecta.")
    if payload["benchmark_case_id"] != "B-CODE-003@0.1.0":
        raise ValidationError("Caso futuro de benchmark incorrecto.")
    if event["node"] is not None or event["metrics"] != {} or event["artifact_refs"] != []:
        raise ValidationError("run.started contiene datos fuera del contrato del preflight.")


def _validate_gate_lifecycle(
    events: list[dict[str, object]],
    *,
    mode: str,
    model_endpoint: str,
) -> tuple[str, Counter[str], dict[str, tuple[str, dict[str, object]]]]:
    middle = events[1:-1]
    if len(middle) != 2 * len(REQUIRED_GATE_IDS):
        raise ValidationError("La corrida no contiene exactamente los diez pares de gates.")
    outcomes: list[str] = []
    records: dict[str, tuple[str, dict[str, object]]] = {}
    for offset, gate_id in enumerate(REQUIRED_GATE_IDS):
        started = middle[offset * 2]
        finished = middle[offset * 2 + 1]
        expected_node = {"id": gate_id, "kind": "preflight_gate"}
        if started["event_type"] != "node.started" or started["node"] != expected_node:
            raise ValidationError(f"Lifecycle invalido para {gate_id}: falta node.started.")
        if started["payload"] != {"gate_id": gate_id}:
            raise ValidationError(f"Payload de inicio invalido para {gate_id}.")
        if started["metrics"] != {} or started["artifact_refs"] != []:
            raise ValidationError(f"node.started contiene datos inesperados para {gate_id}.")
        if finished["node"] != expected_node:
            raise ValidationError(f"Nodo terminal invalido para {gate_id}.")
        payload = finished["payload"]
        if not isinstance(payload, dict) or set(payload) != {
            "gate_id",
            "outcome",
            "code",
            "blocking",
            "evidence",
        }:
            raise ValidationError(f"Payload terminal invalido para {gate_id}.")
        if payload["gate_id"] != gate_id:
            raise ValidationError(f"gate_id terminal invalido para {gate_id}.")
        outcome = payload["outcome"]
        if outcome not in {"passed", "warning", "blocked", "failed"}:
            raise ValidationError(f"Outcome invalido para {gate_id}.")
        blocking = payload["blocking"]
        expected_blocking = outcome in {"blocked", "failed"}
        if not isinstance(blocking, bool) or blocking is not expected_blocking:
            raise ValidationError(f"Blocking inconsistente para {gate_id}.")
        expected_event = "node.failed" if expected_blocking else "node.completed"
        if finished["event_type"] != expected_event:
            raise ValidationError(f"Evento terminal inconsistente para {gate_id}.")
        code = _non_empty_string(payload["code"], "payload.code", offset * 2 + 3)
        if not re.fullmatch(r"[a-z0-9_]+", code):
            raise ValidationError(f"Codigo terminal invalido para {gate_id}.")
        if not isinstance(payload["evidence"], dict):
            raise ValidationError(f"Evidencia no estructurada para {gate_id}.")
        try:
            sanitize_gate_evidence(payload["evidence"])
        except ValueError as exc:
            raise ValidationError(f"Evidencia no sanitaria para {gate_id}.") from exc
        if finished["metrics"] != {} or finished["artifact_refs"] != []:
            raise ValidationError(f"Nodo terminal contiene datos inesperados para {gate_id}.")
        evidence = payload["evidence"]
        assert isinstance(evidence, dict)
        outcome_text = str(outcome)
        _validate_gate_contract(
            gate_id,
            outcome_text,
            code,
            evidence,
            mode=mode,
            model_endpoint=model_endpoint,
        )
        outcomes.append(outcome_text)
        records[gate_id] = (outcome_text, evidence)
    counts: Counter[str] = Counter(outcomes)
    if counts["failed"]:
        return "failed", counts, records
    if counts["blocked"]:
        return "blocked", counts, records
    return "passed", counts, records


def _validate_started_correlations(
    payload: dict[str, object],
    records: dict[str, tuple[str, dict[str, object]]],
) -> None:
    hermes_outcome, hermes_evidence = records["hermes.available"]
    expected_version = hermes_evidence.get("version") if hermes_outcome == "passed" else None
    if payload["client_version"] != expected_version:
        raise ValidationError("client_version no coincide con el gate de Hermes.")

    git_outcome, git_evidence = records["git.head"]
    expected_head = git_evidence.get("head") if git_outcome == "passed" else None
    if payload["git_head"] != expected_head:
        raise ValidationError("git_head no coincide con el gate Git.")

    firewall_passed = records["network.firewall"][0] == "passed"
    network_ref = payload["network_evidence_ref"]
    if (network_ref is not None) is not firewall_passed:
        raise ValidationError("La referencia de red no coincide con el gate de firewall.")

    server_passed = records["ollama.server_profile"][0] == "passed"
    server_ref = payload["server_profile_evidence_ref"]
    if (server_ref is not None) is not server_passed:
        raise ValidationError("La referencia de perfil no coincide con su gate.")


def _validate_terminal(
    event: dict[str, object], derived_outcome: str, gate_counts: Counter[str]
) -> None:
    expected_event = {
        "passed": "run.completed",
        "blocked": "run.blocked",
        "failed": "run.failed",
    }[derived_outcome]
    if event["event_type"] != expected_event:
        raise ValidationError("El terminal no coincide con los resultados de los gates.")
    payload = event["payload"]
    if not isinstance(payload, dict) or set(payload) != {
        "outcome",
        "scored",
        "comparable",
        "gate_counts",
    }:
        raise ValidationError("Payload terminal incorrecto.")
    if payload["outcome"] != derived_outcome:
        raise ValidationError("El outcome terminal no coincide con los gates.")
    if payload["scored"] is not False or payload["comparable"] is not False:
        raise ValidationError("El preflight no puede ser puntuado o comparable.")
    expected_counts = dict(sorted(gate_counts.items()))
    if payload["gate_counts"] != expected_counts:
        raise ValidationError("gate_counts no coincide con los eventos.")
    if event["node"] is not None or event["artifact_refs"] != []:
        raise ValidationError("El terminal contiene nodo o artefactos inesperados.")
    if event["metrics"] != {"gate_total": len(REQUIRED_GATE_IDS)}:
        raise ValidationError("gate_total terminal incorrecto.")


def validate_events(events: list[dict[str, object]]) -> dict[str, object]:
    if not events:
        raise ValidationError("El JSONL esta vacio.")
    event_ids: set[str] = set()
    run_ids: set[str] = set()
    case_ids: set[str] = set()
    variant_ids: set[str] = set()
    model_values: set[str] = set()
    terminals: list[int] = []
    for index, event in enumerate(events, start=1):
        _validate_event(event, index)
        if event["sequence"] != index:
            raise ValidationError(f"Linea {index}: sequence no es consecutiva desde 1.")
        event_id = str(event["event_id"])
        if event_id in event_ids:
            raise ValidationError(f"Linea {index}: event_id duplicado.")
        event_ids.add(event_id)
        run_ids.add(str(event["run_id"]))
        case_ids.add(str(event["case_id"]))
        variant_ids.add(str(event["variant_id"]))
        model_values.add(json.dumps(event["model"], sort_keys=True, separators=(",", ":")))
        if event["event_type"] in TERMINAL_EVENTS:
            terminals.append(index)
    if len(run_ids) != 1:
        raise ValidationError("El archivo mezcla run_id distintos.")
    if len(case_ids) != 1:
        raise ValidationError("El archivo mezcla case_id distintos.")
    if len(variant_ids) != 1:
        raise ValidationError("El archivo mezcla variant_id distintos.")
    if len(model_values) != 1:
        raise ValidationError("El archivo cambia la identidad del modelo durante la corrida.")
    if events[0]["event_type"] != "run.started":
        raise ValidationError("El primer evento debe ser run.started.")
    if sum(event["event_type"] == "run.started" for event in events) != 1:
        raise ValidationError("Debe existir un unico run.started.")
    if terminals != [len(events)]:
        raise ValidationError("Debe existir un unico evento terminal y ser el ultimo.")
    _validate_started_payload(events[0])
    started_payload = events[0]["payload"]
    model = events[0]["model"]
    assert isinstance(started_payload, dict)
    assert isinstance(model, dict)
    derived_outcome, gate_counts, records = _validate_gate_lifecycle(
        events,
        mode=str(started_payload["mode"]),
        model_endpoint=str(model["endpoint"]),
    )
    _validate_started_correlations(started_payload, records)
    _validate_terminal(events[-1], derived_outcome, gate_counts)
    terminal = str(events[-1]["event_type"])
    return {
        "run_id": next(iter(run_ids)),
        "event_count": len(events),
        "terminal_event": terminal,
    }


def validate_path(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValidationError("La ruta JSONL no existe o no es archivo.")
    try:
        data = path.read_bytes().decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError("El archivo no es UTF-8 valido.") from exc
    if not data:
        raise ValidationError("El JSONL esta vacio.")
    if not data.endswith("\n"):
        raise ValidationError("El JSONL debe terminar con newline.")
    lines = data.splitlines()
    if any(not line.strip() for line in lines):
        raise ValidationError("El JSONL no admite lineas vacias.")
    events = [_parse_line(line, number) for number, line in enumerate(lines, start=1)]
    return validate_events(events)


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida una corrida JSONL del laboratorio.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = validate_path(args.path)
    except ValidationError as exc:
        print(f"JSONL invalido: {exc}")
        return 1
    print(
        "JSONL valido: "
        f"run_id={summary['run_id']} eventos={summary['event_count']} "
        f"terminal={summary['terminal_event']}"
    )
    return 0


def main() -> None:
    raise SystemExit(cli())

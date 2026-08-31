"""Eventos JSONL sanitizados, compatibles con el comparador maestro."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sales_curator.contracts.models import RunEvent
from sales_curator.domain.threats import find_sensitive_hits

REQUIRED_FIELDS = frozenset(
    {
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
    }
)
TERMINAL_EVENTS = frozenset({"run.completed", "run.failed"})


class RunValidationError(ValueError):
    """El JSONL no satisface el contrato mínimo de una corrida."""


def to_jsonl_event(
    event: RunEvent,
    *,
    event_type: str,
    model_ref: str,
    case_id: str = "I-CURATOR-SALES-001@0.1.0",
) -> dict[str, Any]:
    payload = dict(event.result_sanitized)
    blob = json.dumps(payload, ensure_ascii=False)
    if find_sensitive_hits(blob):
        payload = {"redacted": True, "reason": "sensitive_content"}
    return {
        "schema_version": "1.0",
        "event_id": event.event_id,
        "run_id": event.run_id,
        "sequence": event.sequence,
        "timestamp": event.occurred_at.isoformat().replace("+00:00", "Z"),
        "event_type": event_type,
        "lab_id": "13-sales-knowledge-curator",
        "variant_id": "deterministic-local-curator",
        "case_id": case_id,
        "model": {
            "provider": "ollama" if model_ref else "none",
            "chat": model_ref or "deterministic",
        },
        "node": {"id": event.node_id, "state": event.state.value},
        "payload": payload,
        "metrics": {
            "latency_ms": event.latency_ms,
            "tokens": event.tokens,
            "ram_mb": event.ram_mb,
            "vram_mb": event.vram_mb,
        },
        "artifact_refs": event.refs,
    }


def write_run_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp.replace(path)


def validate_run(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RunValidationError(f"No existe el archivo: {path}")
    events: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            raise RunValidationError(f"La línea {line_number} está vacía")
        event = json.loads(raw)
        missing = REQUIRED_FIELDS.difference(event)
        if missing:
            raise RunValidationError(
                f"La línea {line_number} no contiene: {', '.join(sorted(missing))}"
            )
        events.append(event)
    if not events:
        raise RunValidationError("La corrida no contiene eventos")
    if events[0]["event_type"] != "run.started":
        raise RunValidationError("El primer evento debe ser run.started")
    if events[-1]["event_type"] not in TERMINAL_EVENTS:
        raise RunValidationError("Falta un evento terminal")
    run_id = events[0]["run_id"]
    for expected, event in enumerate(events, 1):
        if event["sequence"] != expected:
            raise RunValidationError("La secuencia no es consecutiva")
        if event["run_id"] != run_id:
            raise RunValidationError("Los eventos no comparten run_id")
        if event["lab_id"] != "13-sales-knowledge-curator":
            raise RunValidationError("lab_id incorrecto")
    return {
        "path": str(path),
        "run_id": run_id,
        "events": len(events),
        "terminal_event": events[-1]["event_type"],
    }

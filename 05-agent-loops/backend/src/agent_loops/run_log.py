"""Eventos JSONL sanitizados, sin prompts ni salidas completas."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .prompts import CASE_ID, LAB_ID

SCHEMA_VERSION = "1.0"
EventListener = Callable[[dict[str, Any]], None]


class RunLogger:
    def __init__(
        self,
        runs_dir: Path,
        model: str,
        base_url: str,
        variant_id: str,
        listener: EventListener | None = None,
        run_id: str | None = None,
    ) -> None:
        runs_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or f"run-{uuid4()}"
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = runs_dir / f"{timestamp}-{self.run_id}.jsonl"
        self._sequence = 0
        self._finished = False
        self._listener = listener
        self._model = {
            "provider": "ollama",
            "name": model,
            "digest": None,
            "endpoint": base_url,
            "parameters": {
                "stream": False,
                "think": False,
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }
        self.variant_id = variant_id

    def emit(
        self,
        event_type: str,
        *,
        node_id: str | None = None,
        node_type: str | None = None,
        state: str | None = None,
        payload: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        artifact_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        if self._finished:
            raise RuntimeError("La corrida ya termino; no admite eventos nuevos.")
        self._sequence += 1
        node = None
        if node_id is not None:
            node = {"id": node_id, "type": node_type or "agent", "state": state}
        event = {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"{self.run_id}-evt-{self._sequence:04d}",
            "run_id": self.run_id,
            "sequence": self._sequence,
            "timestamp": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "event_type": event_type,
            "lab_id": LAB_ID,
            "variant_id": self.variant_id,
            "case_id": CASE_ID,
            "model": self._model,
            "node": node,
            "payload": payload or {},
            "metrics": metrics or {},
            "artifact_refs": artifact_refs or [],
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
        if self._listener is not None:
            self._listener(event)
        return event

    def finish(self, *, status: str, reason: str) -> None:
        if self._finished:
            return
        event_type = "run.completed" if status == "completed" else "run.failed"
        self.emit(
            event_type,
            payload={
                "status": status,
                "reason": reason,
                "raw_content_stored": False,
            },
        )
        self._finished = True

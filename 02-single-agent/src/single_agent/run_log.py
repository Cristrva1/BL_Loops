"""Exportacion JSONL pequena, observable y sin contenido conversacional."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

LAB_ID = "02-single-agent"
VARIANT_ID = "base-cli"
CASE_ID = "CHAT-BASIC-001@0.1.0"


class RunLogger:
    """Escribe eventos autocontenidos y ordenados dentro del laboratorio."""

    def __init__(self, runs_dir: Path, model: str, base_url: str) -> None:
        runs_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = f"run-{uuid4()}"
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = runs_dir / f"{timestamp}-{self.run_id}.jsonl"
        self._sequence = 0
        self._finished = False
        self._model = {
            "provider": "ollama",
            "name": model,
            "digest": None,
            "endpoint": base_url,
            "parameters": {
                "stream": False,
                "think": False,
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 64,
            },
        }

    def emit(
        self,
        event_type: str,
        *,
        state: str | None = None,
        payload: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        if self._finished:
            raise RuntimeError("La corrida ya termino; no admite eventos nuevos.")
        self._sequence += 1
        event = {
            "schema_version": "1.0",
            "event_id": f"{self.run_id}-evt-{self._sequence:04d}",
            "run_id": self.run_id,
            "sequence": self._sequence,
            "timestamp": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "event_type": event_type,
            "lab_id": LAB_ID,
            "variant_id": VARIANT_ID,
            "case_id": CASE_ID,
            "model": self._model,
            "node": (
                {"id": "chat", "type": "model", "state": state} if state is not None else None
            ),
            "payload": payload or {},
            "metrics": metrics or {},
            "artifact_refs": [],
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")

    def finish(self, *, status: str, turns: int, reason: str) -> None:
        if self._finished:
            return
        event_type = "run.completed" if status == "completed" else "run.failed"
        self.emit(
            event_type,
            payload={
                "status": status,
                "turns": turns,
                "reason": reason,
                "raw_conversation_stored": False,
            },
        )
        self._finished = True

"""Traza JSONL observable sin guardar pregunta, contexto ni respuesta."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

LAB_ID = "06-naive-rag"
VARIANT_ID = "sqlite-fts5-cli"
CASE_ID = "I-RAG-NAIVE-004@0.1.0"


class RunLogger:
    """Escribe eventos autocontenidos y monotonicamente ordenados."""

    def __init__(
        self,
        runs_dir: Path,
        *,
        model: str,
        base_url: str,
        index_ref: str,
    ) -> None:
        runs_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = f"run-{uuid4()}"
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = runs_dir / f"{timestamp}-{self.run_id}.jsonl"
        self._sequence = 0
        self._finished = False
        self._index_ref = index_ref
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

    def emit(
        self,
        event_type: str,
        *,
        node_id: str | None = None,
        node_type: str | None = None,
        state: str | None = None,
        payload: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        if self._finished:
            raise RuntimeError("La corrida ya termino; no admite eventos nuevos.")
        self._sequence += 1
        node = None
        if node_id is not None:
            node = {"id": node_id, "type": node_type or "step", "state": state}
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
            "node": node,
            "payload": payload or {},
            "metrics": metrics or {},
            "artifact_refs": (
                [{"type": "sqlite-index", "path": self._index_ref}]
                if event_type == "run.started"
                else []
            ),
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")

    def finish(
        self,
        *,
        status: str,
        reason: str,
        sources: int,
        abstained: bool,
    ) -> None:
        if self._finished:
            return
        event_type = "run.completed" if status == "completed" else "run.failed"
        self.emit(
            event_type,
            payload={
                "status": status,
                "reason": reason,
                "sources": sources,
                "abstained": abstained,
                "raw_question_stored": False,
                "raw_context_stored": False,
                "raw_answer_stored": False,
            },
        )
        self._finished = True

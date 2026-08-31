"""Eventos JSONL sin contenido crudo de la conversacion o las fuentes."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class RunLogger:
    def __init__(
        self,
        runs_dir: Path,
        *,
        chat_model: str,
        embedding_model: str,
        dimensions: int,
        index_ref: str,
    ) -> None:
        runs_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = f"run-{uuid4()}"
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = runs_dir / f"{stamp}-{self.run_id}.jsonl"
        self._sequence = 0
        self._finished = False
        self._model = {
            "provider": "ollama",
            "chat": chat_model,
            "embedding": embedding_model,
            "embedding_dimensions": dimensions,
            "retrieval_mode": "hybrid",
        }
        self._index_ref = index_ref

    @property
    def finished(self) -> bool:
        return self._finished

    def emit(
        self,
        event_type: str,
        *,
        node_id: str | None = None,
        state: str | None = None,
        payload: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        if self._finished:
            raise RuntimeError("La corrida ya termino.")
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
            "lab_id": "09-agentic-rag",
            "variant_id": "sales-expert-hybrid",
            "case_id": "I-AGENT-SALES-001@0.1.0",
            "model": self._model,
            "node": {"id": node_id, "state": state} if node_id else None,
            "payload": payload or {},
            "metrics": metrics or {},
            "artifact_refs": (
                [{"type": "sqlite-index", "path": self._index_ref}]
                if event_type == "run.started"
                else []
            ),
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")

    def finish(
        self,
        status: str,
        reason: str,
        *,
        sources: int,
        tool_calls: int,
    ) -> None:
        if self._finished:
            return
        self.emit(
            "run.completed" if status == "completed" else "run.failed",
            payload={
                "status": status,
                "reason": reason,
                "sources": sources,
                "tool_calls": tool_calls,
                "raw_question_stored": False,
                "raw_history_stored": False,
                "raw_sources_stored": False,
                "raw_answer_stored": False,
            },
        )
        self._finished = True

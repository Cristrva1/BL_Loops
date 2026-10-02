"""Corridas en memoria para el dashboard SSE. El JSONL es la evidencia persistente."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Literal

from .contracts import CandidateView, IterationView, LoopDeclaration, NodeView
from .engine import GRAPH_NODES, LoopResult

NodeState = Literal["idle", "queued", "running", "waiting", "retrying", "done", "failed", "blocked"]
VALID_STATES: frozenset[str] = frozenset(
    {"idle", "queued", "running", "waiting", "retrying", "done", "failed", "blocked"}
)

IDLE_DETAIL = {
    "intake": "Espera una tarea y un presupuesto.",
    "generate": "Todavia no hay salida.",
    "score": "El evaluador determinista espera una salida.",
    "decide": "Compara el score con umbral y presupuesto.",
    "improve": "Solo se activa si el umbral no se alcanzo.",
    "best": "Todavia no hay mejor candidato.",
}


@dataclass
class RunSnapshot:
    run_id: str
    status: str
    case_id: str
    model: str
    nodes: list[NodeView]
    events: list[dict[str, Any]] = field(default_factory=list)
    declaration: LoopDeclaration | None = None
    iterations: list[IterationView] = field(default_factory=list)
    best: CandidateView | None = None
    stop_reason: str | None = None
    jsonl_path: str | None = None
    error: str | None = None

    def public_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "case_id": self.case_id,
            "model": self.model,
            "nodes": [node.model_dump(mode="json") for node in self.nodes],
            "event_count": len(self.events),
            "declaration": None
            if self.declaration is None
            else self.declaration.model_dump(mode="json"),
            "iterations": [item.model_dump(mode="json") for item in self.iterations],
            "best": None if self.best is None else self.best.model_dump(mode="json"),
            "stop_reason": self.stop_reason,
            "jsonl_path": self.jsonl_path,
            "error": self.error,
        }


class RunStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runs: dict[str, RunSnapshot] = {}

    def create(self, run_id: str, *, case_id: str, model: str) -> RunSnapshot:
        snapshot = RunSnapshot(
            run_id=run_id,
            status="queued",
            case_id=case_id,
            model=model,
            nodes=[
                NodeView(id=node_id, title=title, state="idle", detail=IDLE_DETAIL[node_id])
                for node_id, title in GRAPH_NODES
            ],
        )
        with self._lock:
            self._runs[run_id] = snapshot
        return snapshot

    def reset(self) -> None:
        with self._lock:
            self._runs.clear()

    def get(self, run_id: str) -> RunSnapshot | None:
        with self._lock:
            return self._runs.get(run_id)

    def apply(self, run_id: str, event: dict[str, Any]) -> RunSnapshot | None:
        with self._lock:
            snapshot = self._runs.get(run_id)
            if snapshot is None:
                return None
            snapshot.events.append(event)
            event_type = event["event_type"]
            if event_type == "run.started":
                snapshot.status = "running"
            elif event_type == "run.completed":
                snapshot.status = "completed"
            elif event_type == "run.failed":
                snapshot.status = "failed"
                reason = event.get("payload", {}).get("reason")
                if isinstance(reason, str):
                    snapshot.error = reason
            node = event.get("node")
            if isinstance(node, dict) and isinstance(node.get("id"), str):
                _set_node(snapshot, node["id"], str(node.get("state") or "running"), event)
            return snapshot

    def finish(
        self,
        run_id: str,
        result: LoopResult,
        jsonl_relative: str,
    ) -> RunSnapshot | None:
        with self._lock:
            snapshot = self._runs.get(run_id)
            if snapshot is None:
                return None
            snapshot.status = result.status
            snapshot.declaration = result.declaration
            snapshot.iterations = list(result.iterations)
            snapshot.best = result.best
            snapshot.stop_reason = result.stop_reason
            snapshot.error = result.error
            snapshot.jsonl_path = jsonl_relative
            return snapshot


def _set_node(snapshot: RunSnapshot, node_id: str, state: str, event: dict[str, Any]) -> None:
    visual: NodeState = state if state in VALID_STATES else "running"
    detail = event.get("payload", {}).get("detail")
    for node in snapshot.nodes:
        if node.id != node_id:
            continue
        node.state = visual
        if isinstance(detail, str) and detail:
            node.detail = detail
        elif visual == "failed":
            node.detail = snapshot.error or "El nodo termino con error."
        return


STORE = RunStore()

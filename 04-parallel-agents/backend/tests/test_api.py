from __future__ import annotations

import json
import time

from fastapi.testclient import TestClient

from helpers import TASK, ScriptedClient
from parallel_agents.main import app
from parallel_agents.prompts import CASE_ID, DEFAULT_TASK

client = TestClient(app)


def test_health_declares_local_llm_phase() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["lab_id"] == "04-parallel-agents"
    assert body["llm_used"] is True
    assert body["phase"] == "a-asyncio-fanout"
    assert body["max_in_flight"] >= 1


def test_example_matches_evaluation_case() -> None:
    response = client.get("/api/v1/examples/i-parallel-002")

    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == CASE_ID
    assert len(body["sources"]) == 3
    assert body["sources"][0]["source_id"] == "source-a"


def test_rejects_experiment_without_variants() -> None:
    response = client.post(
        "/api/v1/experiments",
        json={"task": DEFAULT_TASK, "include_sequential": False, "include_parallel": False},
    )

    assert response.status_code == 422


def test_experiment_round_trip_with_scripted_model(lab_settings, monkeypatch) -> None:
    scripted = ScriptedClient()
    monkeypatch.setattr("parallel_agents.main.get_settings", lambda: lab_settings)
    monkeypatch.setattr("parallel_agents.main.get_client", lambda _settings: scripted)

    started = client.post(
        "/api/v1/experiments",
        json={"task": TASK, "include_sequential": True, "include_parallel": True},
    )
    assert started.status_code == 200
    run_id = started.json()["run_id"]

    snapshot = None
    for _ in range(80):
        snapshot = client.get(f"/api/v1/runs/{run_id}").json()
        if snapshot["status"] in {"completed", "failed"}:
            break
        time.sleep(0.05)

    assert snapshot is not None
    assert snapshot["status"] == "completed"
    assert snapshot["sequential"]["passed"] is True
    assert snapshot["parallel"]["passed"] is True
    states = {node["id"]: node["state"] for node in snapshot["nodes"]}
    assert states["intake"] == "done"
    assert states["par-a"] == "done"
    assert states["par-join"] == "done"
    assert states["compare"] == "done"
    assert snapshot["jsonl_path"] is not None
    assert snapshot["jsonl_path"].endswith(".jsonl")
    assert "http://" not in snapshot["jsonl_path"]


def test_terminal_event_is_published_together_with_the_final_result(
    lab_settings, monkeypatch
) -> None:
    """Regresión: run.completed no puede marcar `completed` antes de guardar las variantes."""

    from parallel_agents.main import _execute_run
    from parallel_agents.orchestrator import ExperimentRequest
    from parallel_agents.store import STORE

    scripted = ScriptedClient()
    monkeypatch.setattr("parallel_agents.main.get_client", lambda _settings: scripted)
    run_id = "run-regression-terminal"
    STORE.create(
        run_id,
        case_id=CASE_ID,
        model=lab_settings.model,
        include_sequential=True,
        include_parallel=True,
    )
    statuses_seen: list[str] = []
    real_apply = STORE.apply

    def spy(target_run: str, event: dict) -> object:
        snapshot = real_apply(target_run, event)
        statuses_seen.append(snapshot.status)
        return snapshot

    monkeypatch.setattr(STORE, "apply", spy)

    _execute_run(run_id, ExperimentRequest(task=TASK), lab_settings)

    snapshot = STORE.get(run_id)
    assert "completed" not in statuses_seen
    assert snapshot is not None
    assert snapshot.status == "completed"
    assert snapshot.parallel is not None
    assert snapshot.comparison is not None
    assert snapshot.events[-1]["event_type"] == "run.completed"

    with client.stream("GET", f"/api/v1/runs/{run_id}/events") as response:
        envelopes = [
            json.loads(line.removeprefix("data: "))
            for line in response.iter_lines()
            if line.startswith("data: ")
        ]
    assert envelopes[-1]["event"]["event_type"] == "run.completed"
    assert envelopes[-1]["snapshot"]["status"] == "completed"
    assert envelopes[-1]["snapshot"]["parallel"] is not None
    assert envelopes[-1]["snapshot"]["comparison"] is not None

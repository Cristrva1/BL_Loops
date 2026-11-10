from __future__ import annotations

import json
import time

from fastapi.testclient import TestClient

from agent_loops.main import app
from agent_loops.prompts import CASE_ID, DEFAULT_TASK, INITIAL_PROMPT
from helpers import PASSING_OUTPUT, ScriptedClient

client = TestClient(app)


def test_health_declares_local_llm_phase() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["lab_id"] == "05-agent-loops"
    assert body["llm_used"] is True
    assert body["phase"] == "a0-typed-python-loop"


def test_example_matches_evaluation_case() -> None:
    response = client.get("/api/v1/examples/i-loop-003")

    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == CASE_ID
    assert body["initial_prompt"] == INITIAL_PROMPT
    assert body["budget"]["max_iterations"] == 5
    assert "JSON" in body["task"]


def test_rejects_short_task() -> None:
    response = client.post(
        "/api/v1/experiments",
        json={"task": "muy corto", "initial_prompt": INITIAL_PROMPT},
    )

    assert response.status_code == 422


def test_experiment_round_trip_with_scripted_model(lab_settings, monkeypatch) -> None:
    scripted = ScriptedClient([PASSING_OUTPUT])
    monkeypatch.setattr("agent_loops.main.get_settings", lambda: lab_settings)
    monkeypatch.setattr("agent_loops.main.get_client", lambda _settings: scripted)

    started = client.post(
        "/api/v1/experiments",
        json={"task": DEFAULT_TASK, "initial_prompt": INITIAL_PROMPT},
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
    assert snapshot["stop_reason"] == "threshold_reached"
    assert snapshot["best"]["passed"] is True
    states = {node["id"]: node["state"] for node in snapshot["nodes"]}
    assert states["intake"] == "done"
    assert states["generate"] == "done"
    assert states["score"] == "done"
    assert states["decide"] == "done"
    assert states["best"] == "done"
    assert snapshot["jsonl_path"] is not None
    assert snapshot["jsonl_path"].endswith(".jsonl")
    assert "http://" not in snapshot["jsonl_path"]


def test_terminal_event_is_published_together_with_the_final_result(
    lab_settings, monkeypatch
) -> None:
    """Regresión: run.completed no puede marcar `completed` antes de guardar el mejor candidato."""

    from agent_loops.engine import LoopRequest
    from agent_loops.main import _execute_run
    from agent_loops.store import STORE

    scripted = ScriptedClient([PASSING_OUTPUT])
    monkeypatch.setattr("agent_loops.main.get_client", lambda _settings: scripted)
    run_id = "run-regression-terminal"
    STORE.create(run_id, case_id=CASE_ID, model=lab_settings.model)
    statuses_seen: list[str] = []
    real_apply = STORE.apply

    def spy(target_run: str, event: dict) -> object:
        snapshot = real_apply(target_run, event)
        statuses_seen.append(snapshot.status)
        return snapshot

    monkeypatch.setattr(STORE, "apply", spy)

    request = LoopRequest(task=DEFAULT_TASK, initial_prompt=INITIAL_PROMPT)
    _execute_run(run_id, request, lab_settings)

    snapshot = STORE.get(run_id)
    assert "completed" not in statuses_seen
    assert snapshot is not None
    assert snapshot.status == "completed"
    assert snapshot.best is not None
    assert snapshot.stop_reason is not None
    assert snapshot.events[-1]["event_type"] == "run.completed"

    with client.stream("GET", f"/api/v1/runs/{run_id}/events") as response:
        envelopes = [
            json.loads(line.removeprefix("data: "))
            for line in response.iter_lines()
            if line.startswith("data: ")
        ]
    assert envelopes[-1]["event"]["event_type"] == "run.completed"
    assert envelopes[-1]["snapshot"]["status"] == "completed"
    assert envelopes[-1]["snapshot"]["best"] is not None
    assert envelopes[-1]["snapshot"]["stop_reason"] is not None

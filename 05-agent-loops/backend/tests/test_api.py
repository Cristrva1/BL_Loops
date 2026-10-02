from __future__ import annotations

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

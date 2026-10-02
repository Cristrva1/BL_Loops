from __future__ import annotations

import time

from fastapi.testclient import TestClient

from helpers import PASSING_GUIDE, PLAN_JSON, REVIEW_PASS_JSON, ScriptedClient
from orchestration.main import app
from orchestration.prompts import CASE_ID, DEFAULT_TASK

client = TestClient(app)


def test_health_declares_local_llm_phase() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["lab_id"] == "03-orchestration"
    assert body["llm_used"] is True
    assert body["phase"] == "a0-own-orchestrator"


def test_example_matches_evaluation_case() -> None:
    response = client.get("/api/v1/examples/i-orch-001")

    assert response.status_code == 200
    assert response.json()["case_id"] == CASE_ID
    assert "Ollama" in response.json()["task"]


def test_rejects_experiment_without_variants() -> None:
    response = client.post(
        "/api/v1/experiments",
        json={"task": DEFAULT_TASK, "include_baseline": False, "include_orchestrated": False},
    )

    assert response.status_code == 422


def test_experiment_round_trip_with_scripted_model(lab_settings, monkeypatch) -> None:
    scripted = ScriptedClient([PASSING_GUIDE, PLAN_JSON, PASSING_GUIDE, REVIEW_PASS_JSON])
    monkeypatch.setattr("orchestration.main.get_settings", lambda: lab_settings)
    monkeypatch.setattr("orchestration.main.get_client", lambda _settings: scripted)

    started = client.post(
        "/api/v1/experiments",
        json={"task": DEFAULT_TASK, "include_baseline": True, "include_orchestrated": True},
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
    assert snapshot["baseline"]["passed"] is True
    assert snapshot["orchestrated"]["passed"] is True
    states = {node["id"]: node["state"] for node in snapshot["nodes"]}
    assert states["intake"] == "done"
    assert states["baseline"] == "done"
    assert states["planner"] == "done"
    assert states["score"] == "done"
    assert snapshot["jsonl_path"] is not None
    assert snapshot["jsonl_path"].endswith(".jsonl")
    assert "http://" not in snapshot["jsonl_path"]

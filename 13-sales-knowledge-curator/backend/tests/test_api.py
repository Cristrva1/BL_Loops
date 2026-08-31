from __future__ import annotations

from fastapi.testclient import TestClient

from sales_curator.api.main import create_app
from sales_curator.orchestration.service import CuratorService


def test_health_is_local_and_offline(service: CuratorService) -> None:
    client = TestClient(create_app(service))
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["network_enabled"] is False
    assert body["telemetry"] is False
    assert body["phase"] == "phase-1-local-vertical-slice"


def test_audit_and_sse_round_trip(service: CuratorService) -> None:
    client = TestClient(create_app(service))
    response = client.post("/api/runs/audit", json={"source_dir": "fixtures/corpus"})
    assert response.status_code == 200, response.text
    run_id = response.json()["run_id"]
    assert response.json()["state"] == "review_pending"
    assert response.json()["conflicts"]
    events = client.get(f"/api/runs/{run_id}/events")
    assert events.status_code == 200
    assert "event: run.event" in events.text
    assert "event: run.terminal" in events.text
    claims = client.get("/api/claims", params={"run_id": run_id, "status": "disputed"})
    assert claims.status_code == 200
    assert claims.json()

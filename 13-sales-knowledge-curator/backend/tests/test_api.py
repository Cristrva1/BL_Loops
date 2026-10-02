from __future__ import annotations

from fastapi.testclient import TestClient

from sales_curator.api.main import create_app
from sales_curator.orchestration.service import CuratorService, RunSnapshot


def _stage_via_service(service: CuratorService, corpus) -> RunSnapshot:
    snapshot = service.start_audit(corpus)
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    return service.build_release(snapshot.workflow.run_id)


def test_library_index_is_empty_without_local_artifacts(service: CuratorService) -> None:
    client = TestClient(create_app(service))
    response = client.get("/api/library")
    assert response.status_code == 200
    body = response.json()
    assert body["loop_id"] is None
    assert body["works"] == []


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


def test_build_exposes_candidate_diff_and_publish_requires_exact_hash(
    service: CuratorService, corpus
) -> None:
    client = TestClient(create_app(service))
    staged = _stage_via_service(service, corpus)
    body = client.get(f"/api/runs/{staged.workflow.run_id}").json()
    assert body["state"] == "staging"
    assert body["candidate_id"] == staged.candidate_id
    assert body["candidate_hash"] == staged.candidate_hash
    assert body["candidate_diff"]["included_claim_ids"]
    assert "canonical_text" not in str(body["candidate_diff"])

    rejected = client.post(
        "/api/releases/publish",
        json={
            "run_id": staged.workflow.run_id,
            "candidate_id": staged.candidate_id,
            "expected_hash": "0" * 64,
            "reviewer": "operador-local",
            "reason": "Aprobacion posterior del hash exacto",
        },
    )
    assert rejected.status_code == 400
    assert client.get(f"/api/runs/{staged.workflow.run_id}").json()["state"] == "staging"


def test_publish_round_trip_moves_graph_to_published(service: CuratorService, corpus) -> None:
    client = TestClient(create_app(service))
    staged = _stage_via_service(service, corpus)
    published = client.post(
        "/api/releases/publish",
        json={
            "run_id": staged.workflow.run_id,
            "candidate_id": staged.candidate_id,
            "expected_hash": staged.candidate_hash,
            "reviewer": "operador-local",
            "reason": "Aprobacion posterior del hash exacto",
        },
    )
    assert published.status_code == 200, published.text
    body = published.json()
    assert body["state"] == "published"
    assert body["release_id"]
    current = client.get("/api/releases/current")
    assert current.status_code == 200
    assert current.json()["release_id"] == body["release_id"]

from fastapi.testclient import TestClient

from meeting_summarizer.main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["lab"] == "25-meeting-summarizer"


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "ollama_available" in data


def test_models_endpoint():
    resp = client.get("/api/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data


def test_parse_preview_endpoint():
    payload = {
        "transcript_text": "[00:01] Carlos: Hola a todos\n[00:03] Ana: Hola Carlos",
        "title": "Reunión de prueba",
    }
    resp = client.post("/api/v1/parse", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_turns"] == 2
    assert "Carlos" in data["metadata"]["participants"]
    assert "Ana" in data["metadata"]["participants"]


def test_list_meetings_endpoint():
    resp = client.get("/api/v1/meetings")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_fixtures_endpoint():
    resp = client.get("/api/v1/fixtures")
    assert resp.status_code == 200
    data = resp.json()
    assert "fixtures" in data
    assert len(data["fixtures"]) >= 1

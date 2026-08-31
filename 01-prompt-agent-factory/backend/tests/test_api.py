from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from prompt_agent_factory.api_models import FactoryIntake
from prompt_agent_factory.main import app

client = TestClient(app)


def test_health_is_explicit_about_no_llm() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["llm_used"] is False
    assert response.json()["phase"] == "part-1-contracts"


def test_questions_and_draft_round_trip(prompt_intake: FactoryIntake) -> None:
    intake = prompt_intake.model_dump(mode="json")

    guidance = client.post("/api/v1/factory/questions", json=intake)
    draft = client.post("/api/v1/factory/draft", json=intake)

    assert guidance.status_code == 200
    assert guidance.json()["ready"] is True
    assert draft.status_code == 200
    assert draft.json()["artifact"]["artifact_type"] == "prompt"
    assert draft.json()["events"][-1]["status"] == "queued"


def test_incomplete_draft_has_actionable_error(prompt_intake: FactoryIntake) -> None:
    intake = prompt_intake.model_dump(mode="json")
    intake["title"] = None

    response = client.post("/api/v1/factory/draft", json=intake)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "incomplete_intake"
    assert detail["guidance"]["questions"][0]["field"] == "title"


def test_schema_endpoint_uses_public_schema_key() -> None:
    response = client.get("/api/v1/contracts/agent")

    assert response.status_code == 200
    assert "schema" in response.json()
    assert "schema_" not in response.json()


def test_export_endpoint_reports_relative_result(
    prompt_intake: FactoryIntake,
    monkeypatch,
    tmp_path: Path,
) -> None:
    draft = client.post(
        "/api/v1/factory/draft",
        json=prompt_intake.model_dump(mode="json"),
    ).json()
    fake_path = tmp_path / f"{draft['artifact']['artifact_id']}.json"
    monkeypatch.setattr(
        "prompt_agent_factory.main.export_artifact",
        lambda artifact: fake_path,
    )

    response = client.post(
        "/api/v1/artifacts/export",
        json={"artifact": draft["artifact"]},
    )

    assert response.status_code == 200
    relative_path = response.json()["relative_path"]
    assert relative_path.endswith(fake_path.name)
    assert Path(relative_path).is_absolute() is False
    assert response.json()["events"][-1]["status"] == "done"


def test_export_endpoint_rejects_changed_content(prompt_intake: FactoryIntake) -> None:
    artifact = client.post(
        "/api/v1/factory/draft",
        json=prompt_intake.model_dump(mode="json"),
    ).json()["artifact"]
    artifact["title"] = "Cambio no firmado"

    response = client.post(
        "/api/v1/artifacts/export",
        json={"artifact": artifact},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "content_hash_mismatch"

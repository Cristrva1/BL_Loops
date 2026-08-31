from __future__ import annotations

from pathlib import Path

import pytest
from prompt_agent_factory.api_models import FactoryIntake
from prompt_agent_factory.exporter import export_artifact
from prompt_agent_factory.factory import IncompleteIntakeError, analyze_intake, build_artifact


def test_guidance_explains_missing_context(prompt_intake: FactoryIntake) -> None:
    incomplete = prompt_intake.model_copy(update={"context": None, "constraints": []})
    guidance = analyze_intake(incomplete)

    assert guidance.ready is False
    assert {question.field for question in guidance.questions} == {"context", "constraints"}
    assert guidance.events[1].status == "waiting"
    assert guidance.events[2].status == "idle"


def test_build_refuses_incomplete_intake(prompt_intake: FactoryIntake) -> None:
    incomplete = prompt_intake.model_copy(update={"title": None})

    with pytest.raises(IncompleteIntakeError) as error:
        build_artifact(incomplete)

    assert error.value.guidance.questions[0].field == "title"


def test_agent_requires_explicit_tool_confirmation(agent_intake: FactoryIntake) -> None:
    unconfirmed = agent_intake.model_copy(update={"tools_confirmed": False})
    guidance = analyze_intake(unconfirmed)

    assert guidance.ready is False
    assert guidance.questions[0].field == "tools_confirmed"


def test_export_stays_in_selected_directory(
    prompt_intake: FactoryIntake,
    tmp_path: Path,
) -> None:
    artifact = build_artifact(prompt_intake).artifact
    path = export_artifact(artifact, export_dir=tmp_path)

    assert path.parent == tmp_path
    assert path.name == f"{artifact.artifact_id}.json"
    assert artifact.content_hash in path.read_text(encoding="utf-8")


def test_export_rejects_tampered_artifact(
    prompt_intake: FactoryIntake,
    tmp_path: Path,
) -> None:
    artifact = build_artifact(prompt_intake).artifact
    artifact.purpose = "Contenido alterado después de calcular la huella para probar el control."

    with pytest.raises(ValueError, match="content_hash"):
        export_artifact(artifact, export_dir=tmp_path)

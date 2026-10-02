import pytest

from orchestration.contracts import Plan
from orchestration.json_parse import JsonParseError, extract_json_object


def test_extracts_object_from_fenced_json() -> None:
    payload = extract_json_object("```json\n{\"title\": \"Guia\", \"ok\": true}\n```")

    assert payload["title"] == "Guia"
    assert payload["ok"] is True


def test_plan_defaults_section_id_from_heading() -> None:
    plan = Plan.model_validate(
        {
            "title": "Guia local",
            "audience": "Estudiante de laboratorio",
            "outline": [
                {"heading": "Objetivo", "must_include": ["Ollama"]},
                {"heading": "Pasos", "must_include": ["PowerShell"]},
                {"heading": "Limites", "must_include": ["solo local"]},
            ],
            "success_checks": ["Tiene Objetivo", "Tiene Pasos", "Tiene Limites"],
        }
    )

    assert [section.section_id for section in plan.outline] == [
        "objetivo",
        "pasos",
        "limites",
    ]


def test_rejects_array_or_empty_text() -> None:
    with pytest.raises(JsonParseError, match="objeto"):
        extract_json_object("[1, 2]")
    with pytest.raises(JsonParseError, match="vacia"):
        extract_json_object("   ")

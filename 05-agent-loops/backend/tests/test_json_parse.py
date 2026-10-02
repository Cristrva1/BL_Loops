import pytest

from agent_loops.contracts import PromptRewrite
from agent_loops.json_parse import JsonParseError, extract_json_object


def test_extracts_object_from_fenced_json() -> None:
    payload = extract_json_object('```json\n{"prompt": "Nuevo prompt", "ok": true}\n```')

    assert payload["prompt"] == "Nuevo prompt"
    assert payload["ok"] is True


def test_prompt_rewrite_requires_prompt() -> None:
    rewrite = PromptRewrite.model_validate({"prompt": "Devuelve JSON con title y steps."})

    assert rewrite.prompt.startswith("Devuelve JSON")
    assert rewrite.rationale == ""


def test_rejects_array_or_empty_text() -> None:
    with pytest.raises(JsonParseError, match="objeto"):
        extract_json_object("[1, 2]")
    with pytest.raises(JsonParseError, match="vacia"):
        extract_json_object("   ")

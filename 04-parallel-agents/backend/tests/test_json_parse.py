import pytest

from parallel_agents.contracts import FactBundle
from parallel_agents.json_parse import JsonParseError, extract_json_object


def test_extracts_object_from_fenced_json() -> None:
    payload = extract_json_object('```json\n{"source_id": "source-a", "ok": true}\n```')

    assert payload["source_id"] == "source-a"
    assert payload["ok"] is True


def test_fact_bundle_rejects_unknown_source() -> None:
    with pytest.raises(ValueError):
        FactBundle.model_validate({"source_id": "source-z", "facts": []})


def test_rejects_array_or_empty_text() -> None:
    with pytest.raises(JsonParseError, match="objeto"):
        extract_json_object("[1, 2]")
    with pytest.raises(JsonParseError, match="vacia"):
        extract_json_object("   ")

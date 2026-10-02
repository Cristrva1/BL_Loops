import json
from pathlib import Path

import pytest

from agent_loops.validation import RunValidationError, validate_run


def _event(sequence: int, event_type: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "event_id": f"run-x-evt-{sequence:04d}",
        "run_id": "run-x",
        "sequence": sequence,
        "timestamp": "2026-09-02T12:00:00.000Z",
        "event_type": event_type,
        "lab_id": "05-agent-loops",
        "variant_id": "bounded-loop",
        "case_id": "I-LOOP-003@0.1.0",
        "model": {"provider": "ollama", "name": "qwen3.5:4b"},
        "node": {"id": "generate", "type": "agent", "state": "running"}
        if event_type.startswith("node.")
        else None,
        "payload": {},
        "metrics": {},
        "artifact_refs": [],
    }


def test_valid_run_is_accepted(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    events = [
        _event(1, "run.started"),
        _event(2, "node.started"),
        _event(3, "run.completed"),
    ]
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")

    summary = validate_run(path)

    assert summary.events == 3
    assert summary.terminal_event == "run.completed"


def test_wrong_lab_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    event = _event(1, "run.started")
    event["lab_id"] = "03-orchestration"
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")

    with pytest.raises(RunValidationError, match="05-agent-loops"):
        validate_run(path)


def test_secret_marker_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    event = _event(1, "run.started")
    event["payload"] = {"api_key": "secret"}
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")

    with pytest.raises(RunValidationError, match="marcador"):
        validate_run(path)

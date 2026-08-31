import json
from pathlib import Path

import pytest

from sales_agent.run_log import RunLogger
from sales_agent.validation import RunValidationError, validate_run


def test_completed_agent_run_is_valid(tmp_path: Path) -> None:
    logger = RunLogger(
        tmp_path,
        chat_model="chat",
        embedding_model="embed",
        dimensions=3,
        index_ref=".local/data/index.sqlite3",
    )
    logger.emit("run.started")
    logger.emit("tool.completed", node_id="search_sales_library", state="done")
    logger.finish("completed", "answered", sources=1, tool_calls=1)

    summary = validate_run(logger.path)

    assert summary.events == 3
    assert summary.terminal_event == "run.completed"


def test_non_consecutive_sequence_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    base = {
        "schema_version": "1.0",
        "event_id": "event",
        "run_id": "run",
        "sequence": 2,
        "timestamp": "2026-08-30T00:00:00.000Z",
        "event_type": "run.started",
        "lab_id": "09-agentic-rag",
        "variant_id": "sales-expert-hybrid",
        "case_id": "I-AGENT-SALES-001@0.1.0",
        "model": {},
        "node": None,
        "payload": {},
        "metrics": {},
        "artifact_refs": [],
    }
    path.write_text(json.dumps(base) + "\n", encoding="utf-8")

    with pytest.raises(RunValidationError, match="secuencia"):
        validate_run(path)

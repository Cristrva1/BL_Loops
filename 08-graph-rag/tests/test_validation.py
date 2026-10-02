import json
from pathlib import Path

import pytest

from graph_rag.run_log import RunLogger
from graph_rag.validation import RunValidationError, validate_run


def test_logger_round_trip_and_sequence_validation(tmp_path: Path) -> None:
    logger = RunLogger(
        tmp_path,
        chat_model="qwen3.5:4b",
        mode="graph",
        max_hops=3,
        index_ref=".local/data/graph.sqlite3",
    )
    logger.emit("run.started")
    logger.finish("completed", "test", sources=1, paths=1)
    assert validate_run(logger.path).events == 2

    events = [json.loads(line) for line in logger.path.read_text(encoding="utf-8").splitlines()]
    assert events[0]["lab_id"] == "08-graph-rag"
    assert events[0]["variant_id"] == "sqlite-multihop"
    assert events[0]["case_id"] == "A-RAG-GRAPH-001@0.1.0"
    events[1]["sequence"] = 8
    logger.path.write_text("\n".join(json.dumps(item) for item in events) + "\n", encoding="utf-8")
    with pytest.raises(RunValidationError, match="secuencia"):
        validate_run(logger.path)

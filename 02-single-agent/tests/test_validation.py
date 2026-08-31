import json
from pathlib import Path

import pytest

from single_agent.run_log import RunLogger
from single_agent.validation import RunValidationError, validate_run


def test_logger_output_can_be_imported(tmp_path: Path) -> None:
    logger = RunLogger(tmp_path, "gemma4:e4b", "http://127.0.0.1:11434")
    logger.emit("run.started")
    logger.finish(status="completed", turns=0, reason="test")

    summary = validate_run(logger.path)

    assert summary.events == 2
    assert summary.terminal_event == "run.completed"


def test_import_rejects_non_monotonic_sequence(tmp_path: Path) -> None:
    logger = RunLogger(tmp_path, "gemma4:e4b", "http://127.0.0.1:11434")
    logger.emit("run.started")
    logger.finish(status="completed", turns=0, reason="test")
    events = [json.loads(line) for line in logger.path.read_text(encoding="utf-8").splitlines()]
    events[1]["sequence"] = 99
    logger.path.write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RunValidationError, match="secuencia"):
        validate_run(logger.path)

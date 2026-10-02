from agent_loops.engine import Budget, LoopRequest, run_loop
from agent_loops.ollama_client import OllamaError
from agent_loops.prompts import DEFAULT_TASK, INITIAL_PROMPT
from agent_loops.run_log import RunLogger
from agent_loops.validation import validate_run
from helpers import (
    FAILING_OUTPUT,
    IMPROVED_PROMPT_JSON,
    INVALID_REWRITE,
    MID_OUTPUT,
    PASSING_OUTPUT,
    WORSE_OUTPUT,
    ScriptedClient,
)


def _logger(settings) -> RunLogger:
    return RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        "bounded-loop",
        run_id="run-test-001",
    )


def _request(**kwargs) -> LoopRequest:
    payload = {"task": DEFAULT_TASK, "initial_prompt": INITIAL_PROMPT}
    payload.update(kwargs)
    return LoopRequest(**payload)


def test_first_generation_can_stop_at_threshold(lab_settings) -> None:
    client = ScriptedClient([PASSING_OUTPUT])
    logger = _logger(lab_settings)

    result = run_loop(_request(), lab_settings, client, logger)
    summary = validate_run(result.jsonl_path)

    assert result.status == "completed"
    assert result.stop_reason == "threshold_reached"
    assert result.declaration.initial_score == 5
    assert result.declaration.best_known_score == 5
    assert result.best is not None and result.best.passed is True
    assert len(result.iterations) == 1
    assert len(client.calls) == 1
    assert summary.terminal_event == "run.completed"
    assert (lab_settings.artifacts_dir / "run-test-001" / "best-prompt.txt").is_file()


def test_loop_improves_until_threshold(lab_settings) -> None:
    client = ScriptedClient([FAILING_OUTPUT, IMPROVED_PROMPT_JSON, PASSING_OUTPUT])
    logger = _logger(lab_settings)

    result = run_loop(_request(), lab_settings, client, logger)

    assert result.stop_reason == "threshold_reached"
    assert result.declaration.initial_score == 0
    assert result.declaration.best_known_score == 5
    assert [item.checks_passed for item in result.iterations] == [0, 5]
    assert result.iterations[1].is_best is True
    assert len(client.calls) == 3


def test_keeps_best_candidate_not_the_last(lab_settings) -> None:
    client = ScriptedClient(
        [
            FAILING_OUTPUT,
            IMPROVED_PROMPT_JSON,
            MID_OUTPUT,
            IMPROVED_PROMPT_JSON,
            WORSE_OUTPUT,
        ]
    )
    logger = _logger(lab_settings)
    request = _request(
        budget=Budget(max_iterations=3, max_errors=2, timeout_seconds=180, threshold=5)
    )

    result = run_loop(request, lab_settings, client, logger)

    assert result.stop_reason == "max_iterations"
    assert result.declaration.initial_score == 0
    assert result.declaration.best_known_score == 4
    assert result.best is not None
    assert result.best.iteration == 2
    assert result.best.checks_passed == 4
    assert result.iterations[-1].checks_passed == 2
    assert result.iterations[-1].is_best is False


def test_stops_at_max_errors(lab_settings) -> None:
    client = ScriptedClient(
        [
            OllamaError("fallo uno"),
            IMPROVED_PROMPT_JSON,
            OllamaError("fallo dos"),
        ]
    )
    logger = _logger(lab_settings)

    result = run_loop(_request(), lab_settings, client, logger)

    assert result.stop_reason == "max_errors"
    assert result.declaration.best_known_score == 0
    assert len(result.iterations) == 2


def test_stops_at_timeout(lab_settings) -> None:
    readings = [0.0, 0.0, 10.0]

    def clock() -> float:
        return readings.pop(0) if readings else 10.0

    client = ScriptedClient([FAILING_OUTPUT, IMPROVED_PROMPT_JSON, PASSING_OUTPUT])
    logger = _logger(lab_settings)
    request = _request(
        budget=Budget(max_iterations=5, max_errors=2, timeout_seconds=1.0, threshold=5)
    )

    result = run_loop(request, lab_settings, client, logger, now=clock)

    assert result.stop_reason == "timeout"
    assert result.declaration.initial_score == 0
    assert len(result.iterations) == 1
    assert len(client.calls) == 1


def test_invalid_rewrite_counts_as_error_and_jsonl_is_sanitized(lab_settings) -> None:
    client = ScriptedClient([FAILING_OUTPUT, INVALID_REWRITE, FAILING_OUTPUT, INVALID_REWRITE])
    logger = _logger(lab_settings)

    result = run_loop(_request(), lab_settings, client, logger)
    raw = result.jsonl_path.read_text(encoding="utf-8")

    assert result.stop_reason == "max_errors"
    assert INITIAL_PROMPT not in raw
    assert "ChatGPT" not in raw
    assert "raw_content_stored" in raw
    assert result.declaration.objective
    assert result.declaration.improvement_condition
    assert result.declaration.stop_condition

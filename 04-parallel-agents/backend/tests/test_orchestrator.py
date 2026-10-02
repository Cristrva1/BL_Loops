from dataclasses import replace

from helpers import TASK, ScriptedClient, fixture_sources
from parallel_agents.orchestrator import ExperimentRequest, run_experiment, variant_id_for
from parallel_agents.run_log import RunLogger
from parallel_agents.validation import validate_run


def _logger(settings) -> RunLogger:
    return RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        "sequential-and-parallel",
        run_id="run-test-001",
    )


def test_both_lanes_pass_with_scripted_models(lab_settings) -> None:
    client = ScriptedClient(delay=0.12)
    logger = _logger(lab_settings)
    request = ExperimentRequest(task=TASK)

    result = run_experiment(request, lab_settings, client, logger, sources=fixture_sources())
    summary = validate_run(result.jsonl_path)

    assert result.status == "completed"
    assert result.sequential is not None and result.sequential.passed is True
    assert result.parallel is not None and result.parallel.passed is True
    assert result.parallel.overlap_observed is True
    assert result.parallel.wall_ms is not None
    assert result.sequential.wall_ms is not None
    assert result.parallel.wall_ms < result.sequential.wall_ms
    assert client.peak_in_flight >= 2
    assert result.comparison is not None
    assert result.comparison.winner == "parallel"
    assert summary.terminal_event == "run.completed"
    assert (lab_settings.artifacts_dir / "run-test-001" / "parallel-table.md").is_file()
    raw = result.jsonl_path.read_text(encoding="utf-8")
    assert "plan basico cuesta 29" not in raw.casefold()
    assert "raw_content_stored" in raw


def test_failed_branch_is_not_presented_as_complete(lab_settings) -> None:
    client = ScriptedClient(invalid_source="source-b")
    logger = _logger(lab_settings)
    request = ExperimentRequest(task=TASK, include_sequential=False, include_parallel=True)

    result = run_experiment(request, lab_settings, client, logger, sources=fixture_sources())

    assert result.parallel is not None
    assert "source-b" in result.parallel.failed_sources
    assert "source-b" not in result.parallel.completed_sources
    table_rows = result.parallel.table.rows if result.parallel.table else []
    assert all(row.source_id != "source-b" for row in table_rows)
    assert result.parallel.passed is False


def test_timeout_marks_branch_failed_and_keeps_the_others(lab_settings) -> None:
    tight = replace(lab_settings, branch_timeout_seconds=0.2)
    client = ScriptedClient(delay=0.05, hang_source="source-c")
    logger = _logger(tight)
    request = ExperimentRequest(task=TASK, include_sequential=False, include_parallel=True)

    result = run_experiment(request, tight, client, logger, sources=fixture_sources())

    assert result.parallel is not None
    timed = next(branch for branch in result.parallel.branches if branch.source_id == "source-c")
    assert timed.status == "timeout"
    assert "source-a" in result.parallel.completed_sources
    assert "source-c" not in result.parallel.completed_sources


def test_max_in_flight_one_prevents_overlap(lab_settings) -> None:
    serial = replace(lab_settings, max_in_flight=1)
    client = ScriptedClient(delay=0.08)
    logger = _logger(serial)
    request = ExperimentRequest(task=TASK, include_sequential=False, include_parallel=True)

    result = run_experiment(request, serial, client, logger, sources=fixture_sources())

    assert result.parallel is not None
    assert result.parallel.overlap_observed is False
    assert client.peak_in_flight == 1


def test_variant_id_names_the_selected_lanes() -> None:
    assert variant_id_for(ExperimentRequest("x" * 20, True, True)) == "sequential-and-parallel"
    assert variant_id_for(ExperimentRequest("x" * 20, False, True)) == "parallel"
    assert variant_id_for(ExperimentRequest("x" * 20, True, False)) == "sequential"

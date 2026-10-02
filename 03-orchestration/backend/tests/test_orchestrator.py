from helpers import FAILING_GUIDE, PASSING_GUIDE, PLAN_JSON, REVIEW_PASS_JSON, ScriptedClient
from orchestration.orchestrator import ExperimentRequest, run_experiment, variant_id_for
from orchestration.run_log import RunLogger
from orchestration.validation import validate_run


def _logger(settings) -> RunLogger:
    return RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        "baseline-and-orchestrated",
        run_id="run-test-001",
    )


def test_both_variants_pass_with_scripted_models(lab_settings) -> None:
    client = ScriptedClient([PASSING_GUIDE, PLAN_JSON, PASSING_GUIDE, REVIEW_PASS_JSON])
    logger = _logger(lab_settings)
    request = ExperimentRequest(
        task="Produce una guia breve para ejecutar un agente local con Ollama."
    )

    result = run_experiment(request, lab_settings, client, logger)
    summary = validate_run(result.jsonl_path)

    assert result.status == "completed"
    assert result.baseline is not None and result.baseline.passed is True
    assert result.orchestrated is not None and result.orchestrated.passed is True
    assert result.orchestrated.revision_used is False
    assert result.comparison is not None
    assert result.comparison.winner in {"tie", "orchestrated", "baseline"}
    assert summary.terminal_event == "run.completed"
    assert len(client.calls) == 4
    assert (lab_settings.artifacts_dir / "run-test-001" / "baseline.md").is_file()
    raw = result.jsonl_path.read_text(encoding="utf-8")
    assert "El historial vive en RAM" not in raw
    assert "raw_content_stored" in raw


def test_failed_review_triggers_one_revision(lab_settings) -> None:
    client = ScriptedClient(
        [PASSING_GUIDE, PLAN_JSON, FAILING_GUIDE, REVIEW_PASS_JSON, PASSING_GUIDE]
    )
    logger = _logger(lab_settings)
    request = ExperimentRequest(
        task="Produce una guia breve para ejecutar un agente local con Ollama."
    )

    result = run_experiment(request, lab_settings, client, logger)

    assert result.orchestrated is not None
    assert result.orchestrated.revision_used is True
    assert result.orchestrated.passed is True
    assert len(client.calls) == 5
    roles = [call[0]["content"][:40] for call in client.calls]
    folded = [item.casefold() for item in roles]
    assert any("corrección única" in item or "correccion unica" in item for item in folded)


def test_invalid_plan_fails_only_the_orchestrated_variant(lab_settings) -> None:
    client = ScriptedClient([PASSING_GUIDE, "esto no es un plan"])
    logger = _logger(lab_settings)
    request = ExperimentRequest(
        task="Produce una guia breve para ejecutar un agente local con Ollama."
    )

    result = run_experiment(request, lab_settings, client, logger)

    assert result.baseline is not None and result.baseline.passed is True
    assert result.orchestrated is not None and result.orchestrated.status == "failed"
    assert result.comparison is not None
    assert result.comparison.winner == "baseline"
    assert result.status == "completed"


def test_variant_id_names_the_selected_branches() -> None:
    assert variant_id_for(ExperimentRequest("x" * 20, True, True)) == "baseline-and-orchestrated"
    assert variant_id_for(ExperimentRequest("x" * 20, False, True)) == "orchestrated"
    assert variant_id_for(ExperimentRequest("x" * 20, True, False)) == "baseline"

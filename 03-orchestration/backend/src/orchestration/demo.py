"""Demostracion CLI del caso I-ORCH-001 contra Ollama local."""

from __future__ import annotations

from .config import ConfigurationError, Settings
from .ollama_client import OllamaClient, OllamaError
from .orchestrator import ExperimentRequest, OrchestrationError, run_experiment, variant_id_for
from .prompts import CASE_ID, DEFAULT_TASK
from .run_log import RunLogger
from .validation import validate_run


def main() -> None:
    try:
        settings = Settings.load()
        client = OllamaClient(settings.base_url, settings.model, settings.timeout_seconds)
        request = ExperimentRequest(task=DEFAULT_TASK)
        logger = RunLogger(
            settings.runs_dir,
            settings.model,
            settings.base_url,
            variant_id_for(request),
        )
        print(f"Caso {CASE_ID}")
        print(f"Modelo {settings.model} en {settings.base_url}")
        print("Ejecutando linea base y pipeline orquestado…")
        result = run_experiment(request, settings, client, logger)
    except (ConfigurationError, OllamaError, OrchestrationError) as exc:
        print(f"Demostracion fallida: {exc}")
        raise SystemExit(1) from exc

    summary = validate_run(result.jsonl_path)
    print(f"Estado: {result.status}")
    print(f"JSONL: {summary.path}")
    print(f"Eventos: {summary.events}  terminal={summary.terminal_event}")
    if result.baseline is not None:
        print(
            "Agente unico: "
            f"{result.baseline.checks_passed}/{result.baseline.checks_total} "
            f"passed={result.baseline.passed}  {result.baseline.latency_ms} ms"
        )
    if result.orchestrated is not None:
        print(
            "Orquestada: "
            f"{result.orchestrated.checks_passed}/{result.orchestrated.checks_total} "
            f"passed={result.orchestrated.passed}  correccion={result.orchestrated.revision_used}  "
            f"{result.orchestrated.latency_ms} ms"
        )
    if result.comparison is not None:
        print(f"Comparacion: winner={result.comparison.winner}")
        for line in result.comparison.explanation:
            print(f"- {line}")
    if result.status != "completed":
        raise SystemExit(1)

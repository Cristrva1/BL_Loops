"""Demostracion CLI del caso I-PARALLEL-002 contra Ollama local."""

from __future__ import annotations

from .config import ConfigurationError, Settings
from .ollama_client import OllamaClient, OllamaError
from .orchestrator import ExperimentRequest, ParallelError, run_experiment, variant_id_for
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
        print(f"max_in_flight={settings.max_in_flight}")
        print("Ejecutando variante secuencial y fan-out paralelo…")
        result = run_experiment(request, settings, client, logger)
    except (ConfigurationError, OllamaError, ParallelError) as exc:
        print(f"Demostracion fallida: {exc}")
        raise SystemExit(1) from exc

    summary = validate_run(result.jsonl_path)
    print(f"Estado: {result.status}")
    print(f"JSONL: {summary.path}")
    print(f"Eventos: {summary.events}  terminal={summary.terminal_event}")
    if result.sequential is not None:
        print(
            "Secuencial: "
            f"{len(result.sequential.completed_sources)} fuentes, "
            f"passed={result.sequential.passed}  {result.sequential.wall_ms} ms"
        )
    if result.parallel is not None:
        print(
            "Paralelo: "
            f"{len(result.parallel.completed_sources)} fuentes, "
            f"passed={result.parallel.passed}  overlap={result.parallel.overlap_observed}  "
            f"{result.parallel.wall_ms} ms"
        )
    if result.comparison is not None:
        print(f"Comparacion: winner={result.comparison.winner} speedup={result.comparison.speedup}")
        for line in result.comparison.explanation:
            print(f"- {line}")
    if result.status != "completed":
        raise SystemExit(1)

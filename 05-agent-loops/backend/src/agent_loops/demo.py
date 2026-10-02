"""Demostracion CLI del caso I-LOOP-003 contra Ollama local."""

from __future__ import annotations

from .config import ConfigurationError, Settings
from .engine import LoopError, LoopRequest, run_loop
from .ollama_client import OllamaClient, OllamaError
from .prompts import CASE_ID, DEFAULT_TASK
from .run_log import RunLogger
from .validation import validate_run


def main() -> None:
    try:
        settings = Settings.load()
        client = OllamaClient(settings.base_url, settings.model, settings.timeout_seconds)
        request = LoopRequest(task=DEFAULT_TASK)
        logger = RunLogger(settings.runs_dir, settings.model, settings.base_url, "bounded-loop")
        print(f"Caso {CASE_ID}")
        print(f"Modelo {settings.model} en {settings.base_url}")
        print("Ejecutando loop acotado…")
        result = run_loop(request, settings, client, logger)
    except (ConfigurationError, OllamaError, LoopError) as exc:
        print(f"Demostracion fallida: {exc}")
        raise SystemExit(1) from exc

    summary = validate_run(result.jsonl_path)
    print(f"Estado: {result.status}")
    print(f"JSONL: {summary.path}")
    print(f"Eventos: {summary.events}  terminal={summary.terminal_event}")
    print(f"Motivo de salida: {result.stop_reason}")
    if result.declaration.initial_score is not None:
        print(f"Score inicial: {result.declaration.initial_score}/5")
    if result.declaration.best_known_score is not None:
        print(f"Mejor score: {result.declaration.best_known_score}/5")
    for item in result.iterations:
        marker = " mejor" if item.is_best else ""
        print(
            f"- iter {item.iteration}: {item.checks_passed}/{item.checks_total}"
            f"{marker}"
        )
    if result.status != "completed":
        raise SystemExit(1)

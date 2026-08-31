"""Interfaz conversacional para Windows 11 y PowerShell."""

from __future__ import annotations

import sys
from collections.abc import Callable
from time import perf_counter
from typing import TextIO

from single_agent.config import ConfigurationError, Settings
from single_agent.ollama_client import OllamaClient, OllamaError
from single_agent.run_log import RunLogger

EXIT_COMMANDS = frozenset({"/salir", "salir", "/exit", "exit", "/quit", "quit"})


def run_chat(
    settings: Settings,
    *,
    client: OllamaClient | None = None,
    input_fn: Callable[[str], str] = input,
    output: TextIO = sys.stdout,
) -> int:
    actual_client = client or OllamaClient(
        base_url=settings.base_url,
        model=settings.model,
        timeout_seconds=settings.timeout_seconds,
    )
    logger = RunLogger(settings.runs_dir, settings.model, settings.base_url)
    history = [{"role": "system", "content": settings.system_prompt}]
    turns = 0
    final_status = "completed"
    final_reason = "user_exit"

    logger.emit(
        "run.started",
        payload={
            "interface": "windows-cli",
            "conversation_memory": "session_only",
            "raw_conversation_stored": False,
        },
    )
    _write(output, f"Agente local | modelo: {settings.model}")
    _write(output, "Flujo: humano -> Ollama local -> agente")
    _write(output, "Escribe /salir para terminar.\n")

    try:
        while True:
            try:
                user_text = input_fn("Tu > ").strip()
            except EOFError:
                final_reason = "end_of_input"
                break
            except KeyboardInterrupt:
                _write(output, "\nSalida solicitada.")
                final_reason = "keyboard_interrupt"
                break

            if user_text.casefold() in EXIT_COMMANDS:
                break
            if not user_text:
                continue

            turn_number = turns + 1
            logger.emit(
                "node.queued",
                state="queued",
                payload={"turn": turn_number, "input_chars": len(user_text)},
            )
            logger.emit("node.started", state="running", payload={"turn": turn_number})
            logger.emit(
                "model.requested",
                state="waiting",
                payload={"turn": turn_number, "history_messages": len(history) + 1},
            )
            _write(output, "[procesando] humano -> Ollama -> agente")
            started = perf_counter()

            pending_history = [*history, {"role": "user", "content": user_text}]
            try:
                result = actual_client.chat(pending_history)
            except KeyboardInterrupt:
                elapsed_ms = round((perf_counter() - started) * 1000, 3)
                logger.emit(
                    "error.raised",
                    state="failed",
                    payload={"turn": turn_number, "error_type": "KeyboardInterrupt"},
                    metrics={"wall_duration_ms": elapsed_ms},
                )
                logger.emit("node.failed", state="failed", payload={"turn": turn_number})
                _write(output, "\nSolicitud cancelada por el humano.")
                final_reason = "keyboard_interrupt"
                break
            except OllamaError as exc:
                elapsed_ms = round((perf_counter() - started) * 1000, 3)
                logger.emit(
                    "error.raised",
                    state="failed",
                    payload={"turn": turn_number, "error_type": type(exc).__name__},
                    metrics={"wall_duration_ms": elapsed_ms},
                )
                logger.emit("node.failed", state="failed", payload={"turn": turn_number})
                _write(output, f"Error > {exc}\n")
                continue

            elapsed_ms = round((perf_counter() - started) * 1000, 3)
            history.extend(
                [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": result.content},
                ]
            )
            turns += 1
            metrics = {
                "wall_duration_ms": elapsed_ms,
                "ollama_duration_ms": result.total_duration_ms,
                "prompt_tokens": result.prompt_tokens,
                "output_tokens": result.output_tokens,
            }
            logger.emit(
                "model.completed",
                state="done",
                payload={
                    "turn": turn_number,
                    "response_chars": len(result.content),
                    "response_model": result.model,
                },
                metrics=metrics,
            )
            logger.emit("node.completed", state="done", payload={"turn": turn_number})
            logger.emit("metric.recorded", metrics=metrics)
            _write(output, f"Agente > {result.content}\n")
    except Exception:
        final_status = "failed"
        final_reason = "unexpected_error"
        raise
    finally:
        logger.finish(status=final_status, turns=turns, reason=final_reason)
        try:
            relative_path = logger.path.relative_to(settings.root)
        except ValueError:
            relative_path = logger.path
        _write(output, f"Conversacion terminada. Traza: {relative_path}")

    return 0


def _write(output: TextIO, text: str) -> None:
    print(text, file=output, flush=True)


def _configure_output_encoding(output: TextIO) -> None:
    """Evita fallos de CP-1252 cuando el modelo responde con Unicode en Windows."""

    reconfigure = getattr(output, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


def cli() -> int:
    _configure_output_encoding(sys.stdout)
    try:
        settings = Settings.load()
    except ConfigurationError as exc:
        print(f"Configuracion invalida: {exc}", file=sys.stderr)
        return 2
    return run_chat(settings)


def main() -> None:
    raise SystemExit(cli())

"""Importador minimo para comprobar una corrida JSONL exportada."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from single_agent.config import Settings

REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "event_id",
        "run_id",
        "sequence",
        "timestamp",
        "event_type",
        "lab_id",
        "variant_id",
        "case_id",
        "model",
        "node",
        "payload",
        "metrics",
        "artifact_refs",
    }
)
TERMINAL_EVENTS = frozenset({"run.completed", "run.failed"})


class RunValidationError(ValueError):
    """El JSONL no satisface el contrato minimo de una corrida."""


@dataclass(frozen=True, slots=True)
class RunSummary:
    path: Path
    run_id: str
    events: int
    terminal_event: str


def validate_run(path: Path) -> RunSummary:
    if not path.is_file():
        raise RunValidationError(f"No existe el archivo: {path}")

    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            raise RunValidationError(f"La linea {line_number} esta vacia.")
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise RunValidationError(f"La linea {line_number} no contiene JSON valido.") from exc
        if not isinstance(event, dict):
            raise RunValidationError(f"La linea {line_number} no contiene un objeto JSON.")
        missing = REQUIRED_FIELDS.difference(event)
        if missing:
            names = ", ".join(sorted(missing))
            raise RunValidationError(f"La linea {line_number} no contiene: {names}.")
        events.append(event)

    if not events:
        raise RunValidationError("La corrida no contiene eventos.")
    if events[0]["event_type"] != "run.started":
        raise RunValidationError("El primer evento debe ser run.started.")

    run_id = events[0]["run_id"]
    for expected_sequence, event in enumerate(events, 1):
        if event["sequence"] != expected_sequence:
            raise RunValidationError("La secuencia de eventos no es monotónica y consecutiva.")
        if event["run_id"] != run_id:
            raise RunValidationError("Todos los eventos deben compartir el mismo run_id.")
        if event["lab_id"] != "02-single-agent":
            raise RunValidationError("La corrida no pertenece a 02-single-agent.")

    terminal_event = events[-1]["event_type"]
    if terminal_event not in TERMINAL_EVENTS:
        raise RunValidationError("La corrida no termina en run.completed o run.failed.")
    if any(event["event_type"] in TERMINAL_EVENTS for event in events[:-1]):
        raise RunValidationError("Solo el ultimo evento puede ser terminal.")

    return RunSummary(
        path=path.resolve(),
        run_id=str(run_id),
        events=len(events),
        terminal_event=str(terminal_event),
    )


def _latest_run(runs_dir: Path) -> Path:
    candidates = sorted(runs_dir.glob("*.jsonl"), key=lambda path: path.stat().st_mtime)
    if not candidates:
        raise RunValidationError("Todavia no hay corridas JSONL para validar.")
    return candidates[-1]


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Importa y valida una corrida de 02-single-agent.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Ruta del JSONL; omitir usa el mas reciente.",
    )
    args = parser.parse_args(argv)

    try:
        path = args.path or _latest_run(Settings.load().runs_dir)
        summary = validate_run(path)
    except (RunValidationError, ValueError) as exc:
        print(f"JSONL invalido: {exc}")
        return 1

    print(
        f"JSONL valido: {summary.events} eventos, "
        f"terminal={summary.terminal_event}, run_id={summary.run_id}"
    )
    return 0


def main() -> None:
    raise SystemExit(cli())

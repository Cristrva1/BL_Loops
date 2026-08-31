"""Validador importable de las corridas JSONL del laboratorio."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from vector_rag.config import Settings

FIELDS = frozenset(
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
TERMINAL = frozenset({"run.completed", "run.failed"})


class RunValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RunSummary:
    path: Path
    run_id: str
    events: int
    terminal_event: str


def validate_run(path: Path) -> RunSummary:
    if not path.is_file():
        raise RunValidationError(f"No existe: {path}")
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RunValidationError(f"La linea {number} no es JSON valido.") from exc
        if not isinstance(event, dict) or not FIELDS.issubset(event):
            raise RunValidationError(f"La linea {number} no cumple el contrato.")
        events.append(event)
    if not events or events[0]["event_type"] != "run.started":
        raise RunValidationError("La corrida debe iniciar con run.started.")
    run_id = events[0]["run_id"]
    for expected, event in enumerate(events, 1):
        if event["sequence"] != expected:
            raise RunValidationError("La secuencia no es consecutiva.")
        if event["run_id"] != run_id or event["lab_id"] != "07-vector-rag":
            raise RunValidationError("La identidad de la corrida es inconsistente.")
    terminal = events[-1]["event_type"]
    if terminal not in TERMINAL or any(item["event_type"] in TERMINAL for item in events[:-1]):
        raise RunValidationError("La corrida no tiene un unico evento terminal al final.")
    return RunSummary(path.resolve(), str(run_id), len(events), str(terminal))


def _latest(directory: Path) -> Path:
    candidates = sorted(directory.glob("*.jsonl"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise RunValidationError("Todavia no hay corridas.")
    return candidates[-1]


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida una corrida de 07-vector-rag.")
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = validate_run(args.path or _latest(Settings.load().runs_dir))
    except (RunValidationError, ValueError) as exc:
        print(f"JSONL invalido: {exc}")
        return 1
    print(
        f"JSONL valido: {summary.events} eventos, terminal={summary.terminal_event}, "
        f"run_id={summary.run_id}"
    )
    return 0


def main() -> None:
    raise SystemExit(cli())

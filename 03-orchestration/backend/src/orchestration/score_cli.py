"""Puntúa guías Markdown con el gate determinista de I-ORCH-001, sin llamar a Ollama.

Sirve para practicar con `examples/guides/` y para volver a puntuar los borradores que el modelo
dejó en `.local/artifacts/<run_id>/`. PowerShell no expande comodines para programas nativos, así
que el propio comando expande patrones como `*.md`.
"""

from __future__ import annotations

import argparse
import glob
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from .scoring import score_guide


def _expand(raw_paths: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in raw_paths:
        if any(marker in raw for marker in "*?["):
            matches = sorted(glob.glob(raw))
            paths.extend(Path(match) for match in matches)
            if not matches:
                paths.append(Path(raw))
        else:
            paths.append(Path(raw))
    return paths


def cli(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    error_output: TextIO = sys.stderr,
) -> int:
    """Devuelve 0 si todo aprueba, 1 si alguna guía falla el gate y 2 si falta un archivo."""

    parser = argparse.ArgumentParser(
        prog="orchestration-score",
        description="Aplica el gate determinista de I-ORCH-001 a guías Markdown.",
    )
    parser.add_argument("paths", nargs="+", help="Archivos Markdown o patrones como *.md")
    args = parser.parse_args(argv)

    exit_code = 0
    for path in _expand(args.paths):
        if not path.is_file():
            print(f"No existe el archivo: {path}", file=error_output)
            exit_code = 2
            continue
        result = score_guide(path.read_text(encoding="utf-8"))
        print(
            f"{path.name}: passed={result.passed} "
            f"checks={result.checks_passed}/{result.checks_total} palabras={result.word_count}",
            file=output,
        )
        for check in result.checks:
            mark = "OK" if check.passed else "NO"
            print(f"  {mark}  {check.check_id:<20} {check.evidence}", file=output)
        if not result.passed and exit_code == 0:
            exit_code = 1
    return exit_code


def main() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(cli())

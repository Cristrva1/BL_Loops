"""Puntúa salidas con las cinco assertions de I-LOOP-003, sin llamar a Ollama.

Sirve para practicar con `examples/outputs/` y para volver a puntuar el mejor candidato que el loop
dejó en `.local/artifacts/<run_id>/best-output.txt`. PowerShell no expande comodines para programas
nativos, así que el propio comando expande patrones como `*.txt`.
"""

from __future__ import annotations

import argparse
import glob
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from .scoring import score_output


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
    """Devuelve 0 si todo alcanza 5/5, 1 si alguna salida falla y 2 si falta un archivo."""

    parser = argparse.ArgumentParser(
        prog="agent-loops-score",
        description="Aplica las cinco assertions de I-LOOP-003 a salidas guardadas en archivos.",
    )
    parser.add_argument("paths", nargs="+", help="Archivos de texto o patrones como *.txt")
    args = parser.parse_args(argv)

    exit_code = 0
    for path in _expand(args.paths):
        if not path.is_file():
            print(f"No existe el archivo: {path}", file=error_output)
            exit_code = 2
            continue
        result = score_output(path.read_text(encoding="utf-8"))
        print(
            f"{path.name}: passed={result.passed} "
            f"checks={result.checks_passed}/{result.checks_total}",
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

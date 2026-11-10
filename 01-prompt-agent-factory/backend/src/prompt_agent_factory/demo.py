"""Demostración reproducible: briefing local -> artefacto validado -> archivo JSON.

Sin argumentos conserva el recorrido original (`prompt_duplicate_finder.json`).
Con `--list`, `--intake` o `--all` permite practicar con todos los briefings de
`examples/intakes/`, incluido uno incompleto que muestra las preguntas guiadas.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from .api_models import FactoryIntake
from .config import lab_root
from .exporter import display_path, export_artifact
from .factory import analyze_intake, build_artifact

DEFAULT_INTAKE = "prompt_duplicate_finder.json"


def examples_dir() -> Path:
    return lab_root() / "examples" / "intakes"


def resolve_intake_path(raw: str) -> Path:
    """Acepta rutas relativas al directorio actual o a la raíz del laboratorio."""

    candidate = Path(raw)
    if candidate.is_file() or candidate.is_absolute():
        return candidate
    from_lab = lab_root() / candidate
    if from_lab.is_file():
        return from_lab
    from_examples = examples_dir() / candidate
    if from_examples.is_file():
        return from_examples
    return candidate


def load_intake(path: Path) -> FactoryIntake:
    return FactoryIntake.model_validate_json(path.read_text(encoding="utf-8"))


def _print(output: TextIO, text: str = "") -> None:
    print(text, file=output, flush=True)


def list_examples(output: TextIO) -> int:
    paths = sorted(examples_dir().glob("*.json"))
    _print(output, f"Briefings de ejemplo en {display_path(examples_dir())}:")
    for path in paths:
        try:
            intake = load_intake(path)
        except ValidationError as exc:
            _print(output, f"- {path.name}: inválido ({exc.error_count()} errores)")
            continue
        guidance = analyze_intake(intake)
        state = (
            "listo para construir"
            if guidance.ready
            else f"incompleto: {len(guidance.questions)} preguntas pendientes"
        )
        title = intake.title or "(sin título)"
        _print(output, f"- {path.name} · {intake.artifact_type.value} · {title} · {state}")
    _print(output)
    _print(output, "Construye uno con: uv run factory-demo --intake <archivo.json>")
    return 0


def run_intake(path: Path, output: TextIO) -> int:
    """Devuelve 0 si exporta, 1 si el briefing está incompleto y 2 si es inválido."""

    if not path.is_file():
        _print(output, f"No existe el briefing: {path}")
        return 2
    try:
        intake = load_intake(path)
    except ValidationError as exc:
        _print(output, f"Briefing inválido: {path.name}")
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"]) or "(raíz)"
            _print(output, f"  - {location}: {error['msg']}")
        return 2

    guidance = analyze_intake(intake)
    if not guidance.ready:
        _print(output, f"Briefing incompleto: {path.name} ({guidance.readiness:.0%} listo)")
        _print(output, "La fábrica no inventa los huecos; antes necesita estas decisiones:")
        for question in guidance.questions:
            _print(output, f"  ? [{question.field}] {question.prompt}")
            _print(output, f"    Por qué importa: {question.why}")
            _print(output, f"    Ejemplo: {question.example}")
        _print(output, "No se construyó ni exportó ningún artefacto.")
        return 1

    result = build_artifact(intake)
    exported = export_artifact(result.artifact)
    _print(output, f"Briefing: {path.name}")
    _print(output, f"Artefacto: {result.artifact.artifact_id}")
    _print(output, f"Tipo: {result.artifact.artifact_type.value}")
    _print(output, f"Huella: {result.artifact.content_hash}")
    _print(output, f"Exportado: {display_path(exported)}")
    _print(output, "IA utilizada: no; plantilla determinista de la Parte 1")
    return 0


def run_all(output: TextIO) -> int:
    exported = incomplete = invalid = 0
    for path in sorted(examples_dir().glob("*.json")):
        code = run_intake(path, output)
        _print(output)
        if code == 0:
            exported += 1
        elif code == 1:
            incomplete += 1
        else:
            invalid += 1
    _print(
        output,
        "Resumen: "
        f"{_count(exported, 'exportado', 'exportados')}, "
        f"{_count(incomplete, 'incompleto', 'incompletos')}, "
        f"{_count(invalid, 'inválido', 'inválidos')}.",
    )
    return 0 if invalid == 0 else 2


def _count(value: int, singular: str, plural: str) -> str:
    return f"{value} {singular if value == 1 else plural}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="factory-demo",
        description="Construye artefactos deterministas desde briefings de ejemplo.",
    )
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--list", action="store_true", help="Listar los briefings disponibles.")
    choice.add_argument("--intake", help="Ruta o nombre de un briefing JSON.")
    choice.add_argument("--all", action="store_true", help="Procesar todos los briefings.")
    return parser


def cli(argv: Sequence[str] | None = None, *, output: TextIO = sys.stdout) -> int:
    args = _parser().parse_args(argv)
    if args.list:
        return list_examples(output)
    if args.all:
        return run_all(output)
    raw = args.intake or DEFAULT_INTAKE
    return run_intake(resolve_intake_path(raw), output)


def main() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(cli())


if __name__ == "__main__":
    main()

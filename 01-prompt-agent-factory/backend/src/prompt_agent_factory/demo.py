"""Demostración reproducible: fixture local -> PromptSpec -> archivo JSON."""

from __future__ import annotations

from .api_models import FactoryIntake
from .config import lab_root
from .exporter import display_path, export_artifact
from .factory import build_artifact


def main() -> None:
    fixture = lab_root() / "examples" / "intakes" / "prompt_duplicate_finder.json"
    intake = FactoryIntake.model_validate_json(fixture.read_text(encoding="utf-8"))
    result = build_artifact(intake)
    path = export_artifact(result.artifact)
    print(f"Artefacto: {result.artifact.artifact_id}")
    print(f"Tipo: {result.artifact.artifact_type.value}")
    print(f"Huella: {result.artifact.content_hash}")
    print(f"Exportado: {display_path(path)}")
    print("IA utilizada: no; plantilla determinista de la Parte 1")


if __name__ == "__main__":
    main()

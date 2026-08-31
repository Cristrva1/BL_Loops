"""Exportación local y acotada de artefactos validados."""

from __future__ import annotations

import json
from pathlib import Path

from .config import lab_root
from .contracts import Artifact
from .hashing import has_valid_content_hash


def export_artifact(artifact: Artifact, export_dir: Path | None = None) -> Path:
    if not has_valid_content_hash(artifact):
        raise ValueError("El content_hash no coincide con el contenido del artefacto")

    destination = export_dir or (lab_root() / ".local" / "exports")
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / f"{artifact.artifact_id}.json"
    temporary_path = output_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(artifact.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return output_path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(lab_root().resolve()).as_posix()
    except ValueError:
        return path.name

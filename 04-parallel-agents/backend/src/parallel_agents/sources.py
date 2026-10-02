"""Tres documentos independientes del caso I-PARALLEL-002."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import lab_root


@dataclass(frozen=True, slots=True)
class RequiredFact:
    fact_id: str
    topic: str
    expected_contains: str


@dataclass(frozen=True, slots=True)
class SourceDoc:
    source_id: str
    key: str
    title: str
    filename: str
    text: str
    required_facts: tuple[RequiredFact, ...]

    @property
    def required_ids(self) -> tuple[str, ...]:
        return tuple(item.fact_id for item in self.required_facts)


SOURCE_SPECS: tuple[tuple[str, str, str, tuple[RequiredFact, ...]], ...] = (
    (
        "a",
        "Precios del Taller Norte",
        "source-a-precios.md",
        (
            RequiredFact("precio_basico", "precio", "29"),
            RequiredFact("plan_taller", "precio", "49"),
        ),
    ),
    (
        "b",
        "Horario del Taller Norte",
        "source-b-horario.md",
        (
            RequiredFact("apertura_semana", "horario", "09"),
            RequiredFact("cierre_semana", "horario", "18"),
        ),
    ),
    (
        "c",
        "Garantia del Taller Norte",
        "source-c-garantia.md",
        (
            RequiredFact("garantia_meses", "garantia", "24"),
            RequiredFact("recambios", "garantia", "locales"),
        ),
    ),
)


def sources_dir(root: Path | None = None) -> Path:
    return (root or lab_root()) / "examples" / "sources"


def load_sources(root: Path | None = None) -> tuple[SourceDoc, ...]:
    folder = sources_dir(root)
    documents: list[SourceDoc] = []
    for key, title, filename, required in SOURCE_SPECS:
        path = folder / filename
        if not path.is_file():
            raise FileNotFoundError(f"Falta el fixture {filename}.")
        documents.append(
            SourceDoc(
                source_id=f"source-{key}",
                key=key,
                title=title,
                filename=filename,
                text=path.read_text(encoding="utf-8").strip(),
                required_facts=required,
            )
        )
    return tuple(documents)


def source_summaries(root: Path | None = None) -> list[dict[str, object]]:
    return [
        {
            "source_id": source.source_id,
            "title": source.title,
            "filename": source.filename,
            "chars": len(source.text),
            "required_fact_ids": list(source.required_ids),
        }
        for source in load_sources(root)
    ]

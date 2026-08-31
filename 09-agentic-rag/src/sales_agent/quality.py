"""Filtro explicito de secciones contaminadas o no sustantivas."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
EXCLUDED_HEADINGS = frozenset(
    {
        "contexto (wikipedia)",
        "fuentes y adquisicion",
        "metadatos",
        "temas (open library)",
    }
)


@dataclass(frozen=True, slots=True)
class PreparedBlock:
    text: str
    heading: str
    start_line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class PreparedDocument:
    source_path: Path
    title: str
    source_status: str
    excluded_sections: int
    blocks: tuple[PreparedBlock, ...]


def _normalized(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def _source_status(text: str) -> str:
    normalized = _normalized(text)
    if "candidato no revisado" in normalized:
        return "unreviewed"
    if "documento generado por anima research pipeline" in normalized:
        return "generated"
    return "received"


def prepare_markdown(path: Path, text: str) -> PreparedDocument:
    lines = text.splitlines()
    title = path.stem.replace("_", " ").strip()
    status = _source_status(text)
    heading = title
    excluded = 0
    skip_section = False
    blocks: list[PreparedBlock] = []
    paragraph: list[str] = []
    paragraph_start = 0

    def flush(end_line: int) -> None:
        nonlocal paragraph, paragraph_start
        content = " ".join(value.strip() for value in paragraph).strip()
        if content:
            blocks.append(PreparedBlock(content, heading, paragraph_start, end_line))
        paragraph = []
        paragraph_start = 0

    for line_number, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        match = HEADING.match(stripped)
        if match:
            flush(line_number - 1)
            heading_text = match.group(2).strip()
            if len(match.group(1)) == 1 and heading_text:
                title = heading_text
            heading = heading_text or title
            skip_section = _normalized(heading) in EXCLUDED_HEADINGS
            if skip_section:
                excluded += 1
            continue
        normalized_line = _normalized(stripped)
        if (
            skip_section
            or not stripped
            or stripped == "---"
            or "documento generado por anima research pipeline" in normalized_line
            or "candidato no revisado" in normalized_line
            or normalized_line.startswith("**autor:**")
        ):
            flush(line_number - 1)
            continue
        if not paragraph:
            paragraph_start = line_number
        paragraph.append(stripped)
    flush(len(lines))
    return PreparedDocument(path, title, status, excluded, tuple(blocks))

"""Extraccion determinista de triples visibles y emparejado de entidades."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

TRIPLE_PATTERN = re.compile(
    r"^(?:[-*]\s+)?`([^`]+)`\s+--([A-Za-z][A-Za-z0-9_]*)-->\s+`([^`]+)`\s*$"
)


class ExtractError(ValueError):
    """Una linea parece un triple pero no es una arista valida."""


@dataclass(frozen=True, slots=True)
class ExtractedTriple:
    subject: str
    predicate: str
    object: str
    start_line: int
    end_line: int
    origin: str = "extracted"


def _label(raw: str) -> str:
    return " ".join(raw.split())


def extract_triples(text: str) -> tuple[ExtractedTriple, ...]:
    triples: list[ExtractedTriple] = []
    for number, raw_line in enumerate(text.splitlines(), 1):
        match = TRIPLE_PATTERN.match(raw_line.strip())
        if match is None:
            continue
        subject = _label(match.group(1))
        predicate = match.group(2)
        obj = _label(match.group(3))
        if not subject or not obj:
            raise ExtractError(f"La linea {number} declara una entidad vacia.")
        if subject.casefold() == obj.casefold():
            raise ExtractError(
                f"La linea {number} declara un bucle {subject} --{predicate}--> {obj}."
            )
        triples.append(
            ExtractedTriple(
                subject=subject,
                predicate=predicate,
                object=obj,
                start_line=number,
                end_line=number,
            )
        )
    return tuple(triples)


def match_entities(question: str, labels: Sequence[str]) -> tuple[str, ...]:
    haystack = question.casefold()
    occupied = [False] * len(haystack)
    found: list[str] = []
    unique_labels = {label for label in labels if label.strip()}
    ordered = sorted(unique_labels, key=lambda item: (-len(item), item))
    for label in ordered:
        needle = label.casefold()
        if len(needle) < 2:
            continue
        start = 0
        while True:
            index = haystack.find(needle, start)
            if index < 0:
                break
            end = index + len(needle)
            before = haystack[index - 1] if index > 0 else " "
            after = haystack[end] if end < len(haystack) else " "
            if before.isalnum() or after.isalnum() or any(occupied[index:end]):
                start = index + 1
                continue
            occupied[index:end] = [True] * (end - index)
            found.append(label)
            break
    return tuple(found)

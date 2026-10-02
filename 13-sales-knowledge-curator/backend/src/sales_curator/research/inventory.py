"""Inventario de fichas Markdown de obras, sin leer la guía didáctica."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from sales_curator.contracts.research import LibraryCard

SKIP_NAMES = {"libros.md", "readme.md"}
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
AUTHOR_RE = re.compile(r"\*\*Autor:\*\*\s*(.+)", re.IGNORECASE)
YEAR_RE = re.compile(r"\*\*Año:\*\*\s*(.+)", re.IGNORECASE)
ISBN_RE = re.compile(r"ISBN[:\s]+([0-9Xx-]{10,17})")
LINK_RE = re.compile(r"\*\*([^*]+):\*\*\s*\[[^\]]*\]\((https?://[^)]+)\)")
EXCERPT_HEADING_RE = re.compile(
    r"^##\s+(Descripción Editorial|Contexto \(Wikipedia\)|Contexto)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def work_id_for(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:16]
    return f"wrk_{digest}"


def inventory_library_cards(source: Path) -> list[LibraryCard]:
    root = source.resolve()
    if not root.is_dir():
        raise ValueError("el inventario requiere un directorio de fichas")
    cards: list[LibraryCard] = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file() or path.name.casefold() in SKIP_NAMES:
            continue
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        card = parse_library_card(text, relative_path=relative)
        if card is not None:
            cards.append(card)
    return cards


def parse_library_card(text: str, *, relative_path: str) -> LibraryCard | None:
    title_match = TITLE_RE.search(text)
    author_match = AUTHOR_RE.search(text)
    if title_match is None or author_match is None:
        return None
    title = title_match.group(1).strip()
    author = author_match.group(1).strip()
    if not title or not author:
        return None
    year_match = YEAR_RE.search(text)
    isbn_match = ISBN_RE.search(text)
    links: dict[str, str] = {}
    for label, url in LINK_RE.findall(text):
        key = label.strip().casefold()
        if key in {"amazon", "buscar"}:
            continue
        links[label.strip()] = url.strip()
    excerpt = _excerpt(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return LibraryCard(
        work_id=work_id_for(relative_path),
        title=title[:400],
        author=author[:200],
        year=year_match.group(1).strip()[:20] if year_match else None,
        isbn=isbn_match.group(1).strip() if isbn_match else None,
        relative_path=relative_path,
        source_sha256=digest,
        existing_links=links,
        excerpt=excerpt,
    )


def _excerpt(text: str) -> str:
    heading = EXCERPT_HEADING_RE.search(text)
    if heading is None:
        return ""
    start = heading.end()
    rest = text[start:]
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    body = rest[: next_heading.start() if next_heading else len(rest)]
    collapsed = " ".join(body.split())
    return collapsed[:1200]

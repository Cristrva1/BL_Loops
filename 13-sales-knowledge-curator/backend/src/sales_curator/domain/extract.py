"""Extracción determinista de bloques CLAIM. El LLM opcional no repara JSON inválido."""

from __future__ import annotations

import re
from datetime import date

from sales_curator.contracts.models import ClaimCandidate, ClaimType
from sales_curator.domain.ingest import IngestedSource

CLAIM_BLOCK = re.compile(
    r"^CLAIM:(?P<header>[^\n]+)\n(?P<body>.*?)^ENDCLAIM\s*$",
    re.MULTILINE | re.DOTALL,
)


class ExtractError(ValueError):
    """Un bloque CLAIM no cumple el contrato."""


def _parse_header(header: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in header.split(";"):
        if not part.strip():
            continue
        if "=" not in part:
            raise ExtractError(f"cabecera CLAIM inválida: {header}")
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def _optional_date(fields: dict[str, str], name: str) -> date | None:
    raw = fields.get(name)
    if not raw:
        return None
    return date.fromisoformat(raw)


def _claim_references(fields: dict[str, str], name: str) -> list[str]:
    raw = fields.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def locator_for(text: str, start: int, end: int) -> str:
    before = text[:start]
    start_line = before.count("\n") + 1
    end_line = start_line + text[start:end].count("\n")
    if start_line == end_line:
        return f"L{start_line}"
    return f"L{start_line}-L{end_line}"


def fragment_at_locator(text: str, locator: str) -> str | None:
    lines = text.replace("\r\n", "\n").split("\n")
    match = re.fullmatch(r"L(\d+)(?:-L(\d+))?", locator)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    if start < 1 or end < start or end > len(lines):
        return None
    return "\n".join(lines[start - 1 : end])


def extract_from_source(item: IngestedSource) -> list[ClaimCandidate]:
    claims: list[ClaimCandidate] = []
    for match in CLAIM_BLOCK.finditer(item.full_text):
        fields = _parse_header(match.group("header"))
        body = match.group("body").strip()
        if not body:
            raise ExtractError(f"CLAIM {fields.get('id', '?')} sin texto")
        locator = locator_for(item.full_text, match.start("body"), match.end("body"))
        try:
            claim_type = ClaimType(fields["type"])
        except (KeyError, ValueError) as exc:
            raise ExtractError(f"tipo de afirmación inválido: {fields.get('type')}") from exc
        claims.append(
            ClaimCandidate(
                claim_id=fields["id"],
                text=body,
                claim_type=claim_type,
                topic=fields["topic"],
                population=fields.get("population") or None,
                context=fields.get("context") or None,
                jurisdiction=fields.get("jurisdiction") or item.source.jurisdiction,
                valid_from=_optional_date(fields, "valid_from"),
                valid_until=_optional_date(fields, "valid_until"),
                method=fields.get("method") or None,
                sample=fields.get("sample") or None,
                conflicts_with=_claim_references(fields, "conflicts_with"),
                supersedes=fields.get("supersedes") or None,
                locator=locator,
                source_id=item.source.source_id,
            )
        )
    return claims

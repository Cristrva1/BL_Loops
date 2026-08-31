"""Ingesta de solo lectura: hash, cuarentena, metadatos y sin mutar la fuente."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from sales_curator.config import lab_root
from sales_curator.connectors.local_fs import (
    IngestError,
    discover_sources,
    mime_for,
    read_bytes,
    resolve_inside,
)
from sales_curator.contracts.models import (
    DocumentArtifact,
    Independence,
    QuarantineStatus,
    SourceKind,
    SourceRecord,
)
from sales_curator.domain.threats import find_injection_hits
from sales_curator.hashing import sha256_bytes, sha256_text, with_content_hash


def _parse_bool(value: str) -> bool:
    lowered = value.strip().casefold()
    if lowered in {"true", "yes", "1"}:
        return True
    if lowered in {"false", "no", "0"}:
        return False
    raise IngestError(f"booleano inválido: {value}")


def _parse_date(value: str) -> date | None:
    text = value.strip()
    if not text or text.lower() in {"none", "n/a", "na"}:
        return None
    return date.fromisoformat(text)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, int]:
    if not text.startswith("---"):
        raise IngestError("El archivo debe comenzar con frontmatter ---")
    rest = text[3:].lstrip("\r\n")
    end = rest.find("\n---")
    if end < 0:
        raise IngestError("Frontmatter sin cierre")
    raw_meta = rest[:end]
    body = rest[end + 4 :].lstrip("\r\n")
    meta: dict[str, str] = {}
    for line in raw_meta.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise IngestError(f"Línea de metadatos inválida: {line}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    header_lines = 3 + raw_meta.count("\n") + (0 if raw_meta.endswith("\n") else 1)
    body_start = header_lines + 1
    return meta, body, body_start


def sanitize_uri(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split()).casefold()


def _kind_for_mime(mime: str) -> SourceKind:
    if mime == "text/markdown":
        return SourceKind.LOCAL_MARKDOWN
    return SourceKind.LOCAL_TXT


def _quarantine(
    meta: dict[str, str],
    body: str,
    size: int,
    max_bytes: int,
    injection_hits: list[str],
) -> tuple[QuarantineStatus, list[str]]:
    warnings: list[str] = []
    if size > max_bytes:
        return QuarantineStatus.OVERSIZE, ["exceeds_max_bytes"]
    if injection_hits:
        warnings.append("injection_patterns")
        return QuarantineStatus.INJECTION, warnings
    license_value = meta.get("license", "").strip().casefold()
    rights = int(meta.get("rights_clarity", "0") or "0")
    allowed = _parse_bool(meta.get("redistribution_allowed", "false"))
    if license_value in {"", "unknown", "unclear"} or rights <= 1 or not allowed:
        warnings.append("uncertain_rights")
        return QuarantineStatus.UNCERTAIN_RIGHTS, warnings
    if not body.strip():
        warnings.append("empty_projection")
        return QuarantineStatus.EMPTY, warnings
    return QuarantineStatus.CLEAR, warnings


@dataclass(frozen=True, slots=True)
class IngestedSource:
    source: SourceRecord
    artifact: DocumentArtifact
    body: str
    full_text: str
    body_start_line: int
    original_bytes: bytes


def ingest_file(
    path: Path,
    *,
    allowed_root: Path,
    max_bytes: int,
    retrieved_at: datetime,
    lab: Path | None = None,
) -> IngestedSource:
    root = lab or lab_root()
    target = resolve_inside(allowed_root, path)
    original_mtime = target.stat().st_mtime
    original_bytes = read_bytes(target, max_bytes)
    if target.stat().st_mtime != original_mtime:
        raise IngestError("La fuente cambió durante la lectura")
    mime = mime_for(target)
    text = original_bytes.decode("utf-8-sig")
    meta, body, body_start = parse_frontmatter(text)
    injection_hits = find_injection_hits(text)
    status, warnings = _quarantine(meta, body, len(original_bytes), max_bytes, injection_hits)
    independence_raw = meta.get("independence", "unknown")
    try:
        independence = Independence(independence_raw)
    except ValueError as exc:
        raise IngestError(f"independence inválida: {independence_raw}") from exc
    topics = [part.strip() for part in meta.get("topics", "").split(",") if part.strip()]
    source = with_content_hash(
        SourceRecord(
            source_id=meta["source_id"],
            kind=_kind_for_mime(mime),
            title=meta["title"],
            author=meta["author"],
            editor=meta.get("editor") or None,
            uri=sanitize_uri(target, root),
            published_at=_parse_date(meta.get("published_at", "")),
            updated_at=_parse_date(meta.get("updated_at", "")),
            retrieved_at=retrieved_at,
            license=meta.get("license", "unknown"),
            usage_basis=meta.get("usage_basis", "unspecified"),
            redistribution_allowed=_parse_bool(meta.get("redistribution_allowed", "false")),
            content_sha256=sha256_bytes(original_bytes),
            language=meta.get("language", "es"),
            jurisdiction=meta.get("jurisdiction", "unspecified"),
            origin_source_id=meta.get("origin_source_id", meta["source_id"]),
            independence=independence,
            topics=topics,
            quarantine_status=status,
            rights_clarity=int(meta.get("rights_clarity", "0") or "0"),
            warnings=warnings,
            content_hash="0" * 64,
        )
    )
    locators = [f"L{index}" for index, line in enumerate(text.splitlines(), 1) if line.strip()]
    artifact = with_content_hash(
        DocumentArtifact(
            artifact_id=f"art-{source.source_id}",
            source_id=source.source_id,
            mime="text/markdown" if mime == "text/markdown" else "text/plain",
            extractor="frontmatter-v1",
            extractor_version="1.0.0",
            original_hash=source.content_sha256,
            normalized_hash=sha256_text(normalize_text(body)),
            size_bytes=len(original_bytes),
            quarantine_status=status,
            warnings=warnings,
            locators=locators[:200],
            content_hash="0" * 64,
        )
    )
    if target.stat().st_mtime != original_mtime:
        raise IngestError("La fuente fue modificada; la ingesta es de solo lectura")
    return IngestedSource(
        source=source,
        artifact=artifact,
        body=body,
        full_text=text,
        body_start_line=body_start,
        original_bytes=original_bytes,
    )


def ingest_directory(
    source_dir: Path,
    *,
    allowed_root: Path,
    max_bytes: int,
    retrieved_at: datetime,
) -> list[IngestedSource]:
    files = discover_sources(allowed_root, source_dir)
    ingested = [
        ingest_file(
            path,
            allowed_root=allowed_root,
            max_bytes=max_bytes,
            retrieved_at=retrieved_at,
        )
        for path in files
    ]
    source_uris: dict[str, str] = {}
    for item in ingested:
        source_id = item.source.source_id
        if source_id in source_uris:
            raise IngestError(
                f"source_id duplicado en la corrida: {source_id}; "
                f"{source_uris[source_id]} y {item.source.uri}; "
                "cada archivo debe declarar una identidad única"
            )
        source_uris[source_id] = item.source.uri
    by_hash: dict[str, str] = {}
    result: list[IngestedSource] = []
    for item in ingested:
        origin = item.source.origin_source_id
        digest = item.source.content_sha256
        independence = item.source.independence
        warnings = list(item.source.warnings)
        if digest in by_hash:
            independence = Independence.SYNDICATED
            warnings.append(f"exact_duplicate_of:{by_hash[digest]}")
        elif origin != item.source.source_id:
            independence = Independence.SYNDICATED
            warnings.append(f"origin_chain:{origin}")
        else:
            by_hash[digest] = item.source.source_id
        source = with_content_hash(
            item.source.model_copy(update={"independence": independence, "warnings": warnings})
        )
        result.append(
            IngestedSource(
                source=source,
                artifact=item.artifact,
                body=item.body,
                full_text=item.full_text,
                body_start_line=item.body_start_line,
                original_bytes=item.original_bytes,
            )
        )
    return result

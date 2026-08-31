"""Importación local y estrecha de PDF/DOCX autorizados mediante MarkItDown."""

from __future__ import annotations

import io
import json
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from sales_curator.config import resolve_lab_output_root
from sales_curator.connectors.local_fs import IngestError, read_bytes, resolve_inside
from sales_curator.contracts.research import (
    DocumentImportRecord,
    DocumentRights,
    RightsStatus,
)
from sales_curator.hashing import sha256_bytes, sha256_text, with_content_hash

Converter = Callable[[bytes, str], str]

MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class DocumentImportError(ValueError):
    """El documento no cumple alcance, derechos o extracción mínima."""


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _value(text: str) -> str:
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())


def _markitdown_convert(data: bytes, suffix: str) -> str:
    try:
        from markitdown import MarkItDown, StreamInfo
    except ImportError as exc:  # pragma: no cover - se prueba con el spike real
        raise DocumentImportError(
            "MarkItDown no está instalado; ejecute uv sync y el preflight documental"
        ) from exc
    try:
        result = MarkItDown(enable_plugins=False).convert_stream(
            io.BytesIO(data),
            stream_info=StreamInfo(extension=suffix),
        )
    except Exception as exc:  # el detalle del parser no debe filtrar contenido
        raise DocumentImportError(f"MarkItDown no pudo convertir {suffix}") from exc
    return result.markdown


def markitdown_version() -> str:
    try:
        return version("markitdown")
    except PackageNotFoundError as exc:
        raise DocumentImportError("MarkItDown no está instalado") from exc


def import_document(
    path: Path,
    *,
    allowed_root: Path,
    output_root: Path,
    title: str,
    author: str,
    language: str,
    rights: DocumentRights,
    topics: tuple[str, ...] = (),
    max_bytes: int = 20_000_000,
    converter: Converter | None = None,
    extractor_version: str | None = None,
    clock: Callable[[], datetime] | None = None,
) -> DocumentImportRecord:
    if language not in {"en", "es"}:
        raise DocumentImportError("solo se permiten idiomas en o es")
    try:
        output_root = resolve_lab_output_root(output_root)
    except ValueError as exc:
        raise DocumentImportError(str(exc)) from exc
    if not rights.retention_allowed or not rights.extraction_allowed:
        raise DocumentImportError("los derechos no permiten retener y extraer el documento")
    try:
        target = resolve_inside(allowed_root, path)
    except IngestError as exc:
        raise DocumentImportError("el archivo sale del directorio permitido") from exc
    if not target.is_file():
        raise DocumentImportError("el documento no existe")
    suffix = target.suffix.casefold()
    media_type = MEDIA_TYPES.get(suffix)
    if media_type is None:
        raise DocumentImportError("solo se permiten PDF y DOCX")
    original_mtime = target.stat().st_mtime_ns
    try:
        original = read_bytes(target, max_bytes)
    except IngestError as exc:
        raise DocumentImportError(str(exc)) from exc
    if target.stat().st_mtime_ns != original_mtime:
        raise DocumentImportError("el documento cambió durante la lectura")
    original_hash = sha256_bytes(original)
    convert = converter or _markitdown_convert
    converted = convert(original, suffix).replace("\r\n", "\n").replace("\r", "\n").strip()
    if not converted:
        raise DocumentImportError("la proyección Markdown está vacía")
    try:
        current = read_bytes(target, max_bytes)
    except IngestError as exc:
        raise DocumentImportError("la importación perdió consistencia con el original") from exc
    if target.stat().st_mtime_ns != original_mtime or current != original:
        raise DocumentImportError("la importación alteró o perdió consistencia con el original")
    source_id = f"src-doc-{original_hash[:16]}"
    document_id = f"doc_{original_hash[:16]}"
    resolved_extractor_version = extractor_version or markitdown_version()
    rights_clarity = (
        4
        if rights.rights_status
        in {
            RightsStatus.PUBLIC_DOMAIN,
            RightsStatus.OPEN_LICENSE,
            RightsStatus.EXPLICIT_PERMISSION,
        }
        else 1
    )
    frontmatter = [
        "---",
        f"source_id: {source_id}",
        f"title: {_value(title)}",
        f"author: {_value(author)}",
        f"license: {_value(rights.license)}",
        f"usage_basis: {_value(rights.usage_basis)}",
        f"redistribution_allowed: {str(rights.redistribution_allowed).lower()}",
        f"language: {language}",
        f"jurisdiction: {_value(rights.jurisdiction)}",
        f"origin_source_id: {source_id}",
        "independence: original",
        f"rights_clarity: {rights_clarity}",
        f"topics: {','.join(_value(item) for item in topics)}",
        f"original_sha256: {original_hash}",
        f"original_media_type: {media_type}",
        "extractor: markitdown",
        f"extractor_version: {resolved_extractor_version}",
        "---",
        "",
    ]
    markdown = "\n".join(frontmatter) + converted + "\n"
    markdown_relative = Path(document_id) / "content.md"
    manifest_relative = Path(document_id) / "manifest.json"
    when = (clock or (lambda: datetime.now(UTC)))()
    warnings = [
        "MarkItDown optimiza para análisis; no garantiza fidelidad editorial ni página original."
    ]
    if not rights.redistribution_allowed:
        warnings.append("Contenido privado: no incluir texto en paquetes redistribuibles.")
    if not rights.notebooklm_upload_allowed:
        warnings.append("No autorizado para transferencia a NotebookLM u otra nube.")
    record = with_content_hash(
        DocumentImportRecord(
            document_id=document_id,
            source_file_name=target.name,
            source_media_type=media_type,
            title=_value(title),
            author=_value(author),
            language=language,  # type: ignore[arg-type]
            topics=[_value(item) for item in topics],
            original_sha256=original_hash,
            markdown_sha256=sha256_text(markdown),
            extractor_version=resolved_extractor_version,
            locator_strategy=(
                "líneas del Markdown derivado; página original requiere revisión humana"
            ),
            markdown_path=markdown_relative.as_posix(),
            manifest_path=manifest_relative.as_posix(),
            rights=rights,
            warnings=warnings,
            created_at=when,
            content_hash="0" * 64,
        )
    )
    _atomic_write(output_root / markdown_relative, markdown)
    _atomic_write(
        output_root / manifest_relative,
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
    )
    return record

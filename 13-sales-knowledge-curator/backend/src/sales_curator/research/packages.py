"""Exportaciones manuales: NotebookLM y corpus portable para otro RAG."""

from __future__ import annotations

import json
from pathlib import Path

from sales_curator.config import resolve_lab_output_root
from sales_curator.contracts.research import (
    BookAccessOffer,
    BookResearchReport,
    NotebookPacket,
    NotebookSourceSet,
    RagPacket,
)
from sales_curator.hashing import sha256_text, with_content_hash


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _offer_markdown(offer: BookAccessOffer) -> str:
    authors = ", ".join(offer.authors) or "Sin autor verificado"
    identifiers = (
        ", ".join(
            f"{kind}: {', '.join(values)}" for kind, values in sorted(offer.identifiers.items())
        )
        or "Sin identificadores verificados"
    )
    download = offer.download_url or "No habilitada"
    return (
        f"# {offer.title}\n\n"
        f"- Proveedor: `{offer.provider}`\n"
        f"- Autores: {authors}\n"
        f"- Identificadores: {identifiers}\n"
        f"- Idioma: {offer.language or 'sin verificar'}\n"
        f"- Publicación: {offer.published_date or 'sin verificar'}\n"
        f"- Acceso: `{offer.access_mode.value}`\n"
        f"- Derechos: `{offer.rights_status.value}`\n"
        f"- Jurisdicción evaluada: {offer.jurisdiction}\n"
        f"- Registro: {offer.record_url}\n"
        f"- Evidencia de derechos: {offer.rights_evidence_url or 'ausente'}\n"
        f"- Descarga automática: {download}\n\n"
        f"> {offer.rights_statement}\n\n"
        "Esta ficha contiene metadatos y enlaces; no reproduce el libro.\n"
    )


def build_notebooklm_packet(
    report: BookResearchReport,
    output_root: Path,
    *,
    max_sources: int = 50,
) -> NotebookPacket:
    output_root = resolve_lab_output_root(output_root)
    if not 1 <= max_sources <= 50:
        raise ValueError("NotebookLM admite como máximo 50 fuentes por notebook estándar")
    source_paths: list[str] = []
    lines = [
        "# Fuentes de investigación",
        "",
        "Paquete manual: no se inició sesión ni se subió contenido a NotebookLM.",
        "Cada ficha conserva el modo de acceso y los derechos por separado.",
        "",
    ]
    for index, offer in enumerate(report.offers, 1):
        relative = Path("sources") / f"{index:03d}-{offer.offer_id}.md"
        _atomic_write(output_root / relative, _offer_markdown(offer))
        source_paths.append(relative.as_posix())
        lines.append(
            f"- **{offer.title}** — {offer.provider}; `{offer.access_mode.value}`; "
            f"`{offer.rights_status.value}`; {offer.record_url}"
        )
    _atomic_write(output_root / "SOURCES.md", "\n".join(lines) + "\n")
    _atomic_write(
        output_root / "STUDY_GUIDE.md",
        "# Guía de estudio\n\n"
        "1. Distingue obra, edición y copia digital.\n"
        "2. Compara metadatos entre proveedores antes de aceptar una coincidencia.\n"
        "3. Trata preview y préstamo como acceso, no como permiso de copia.\n"
        "4. Verifica jurisdicción y licencia antes de cualquier descarga.\n"
        "5. Toda síntesis debe citar la ficha y, después, la fuente primaria autorizada.\n",
    )
    _atomic_write(
        output_root / "RESEARCH_QUESTIONS.md",
        "# Preguntas para NotebookLM\n\n"
        "- ¿Qué proveedores describen la misma obra y qué edición concreta ofrece cada uno?\n"
        "- ¿Qué campos bibliográficos se contradicen o siguen sin verificar?\n"
        "- ¿Qué accesos son descarga abierta, lectura, preview o préstamo?\n"
        "- ¿Qué afirmaciones requerirían revisar el texto completo autorizado?\n"
        "- ¿Qué límites impiden generalizar una práctica de ventas?\n",
    )
    notebooks = [
        NotebookSourceSet(
            notebook_number=(start // max_sources) + 1,
            source_paths=source_paths[start : start + max_sources],
        )
        for start in range(0, len(source_paths), max_sources)
    ]
    if not notebooks:
        notebooks = [NotebookSourceSet(notebook_number=1, source_paths=[])]
    packet = with_content_hash(
        NotebookPacket(
            packet_id=f"nbk_{report.content_hash[:16]}",
            notebooks=notebooks,
            manifest_path="manifest.json",
            content_hash="0" * 64,
        )
    )
    manifest = {
        **packet.model_dump(mode="json"),
        "research_id": report.research_id,
        "query": report.query,
        "jurisdiction": report.jurisdiction,
        "report_hash": report.content_hash,
        "rights_note": (
            "El uso educativo no autoriza copiar. El operador importa manualmente solo fuentes "
            "que pueda transferir legalmente."
        ),
    }
    _atomic_write(
        output_root / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return packet


def build_rag_packet(report: BookResearchReport, output_root: Path) -> RagPacket:
    output_root = resolve_lab_output_root(output_root)
    records: list[dict] = []
    for offer in report.offers:
        records.append(
            {
                "record_type": "book_access_offer",
                "offer_id": offer.offer_id,
                "title": offer.title,
                "authors": offer.authors,
                "identifiers": offer.identifiers,
                "provider": offer.provider,
                "provider_record_id": offer.provider_record_id,
                "record_url": offer.record_url,
                "access_mode": offer.access_mode.value,
                "rights_status": offer.rights_status.value,
                "rights_evidence_url": offer.rights_evidence_url,
                "rights_statement": offer.rights_statement,
                "download_url": offer.download_url,
                "jurisdiction": offer.jurisdiction,
                "language": offer.language,
                "published_date": offer.published_date,
                "retrieved_at": offer.retrieved_at.isoformat(),
                "content_hash": offer.content_hash,
            }
        )
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in records
    )
    records_path = "book-access-offers.jsonl"
    _atomic_write(output_root / records_path, text)
    packet = with_content_hash(
        RagPacket(
            packet_id=f"rag_{report.content_hash[:16]}",
            records_path=records_path,
            manifest_path="manifest.json",
            record_count=len(records),
            content_hash="0" * 64,
        )
    )
    manifest = {
        **packet.model_dump(mode="json"),
        "research_id": report.research_id,
        "report_hash": report.content_hash,
        "records_sha256": sha256_text(text),
        "import_mode": "manual_copy_only",
        "target_profile": "portable-rag-metadata; no live dependency",
    }
    _atomic_write(
        output_root / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return packet

"""Loop acotado de biblioteca: catálogos, descarga legal y dossier local."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from sales_curator.config import resolve_lab_output_root
from sales_curator.connectors.book_catalogs import apply_internet_archive_files
from sales_curator.connectors.network import NetworkDisabled, NetworkPolicyError, SafeHttpClient
from sales_curator.contracts.research import (
    AccessMode,
    BookAccessOffer,
    BookResearchReport,
    LegalCopyRecord,
    LibraryLoopReport,
    LibraryWorkRecord,
    LibraryWorkStatus,
    can_download_automatically,
)
from sales_curator.research.books import BookResearcher, internet_archive_metadata_url
from sales_curator.research.inventory import inventory_library_cards

CURATOR_SECTION_START = "## Investigación del curador"
CURATOR_SECTION_END = "<!-- curator:end -->"
DEFAULT_LIBRARY_PROVIDERS = (
    "open_library",
    "google_books",
    "project_gutenberg",
    "internet_archive",
)
COMPLETE_STATUSES = {LibraryWorkStatus.DOSSIER_READY, LibraryWorkStatus.COPY_ACQUIRED}


def download_legal_copy(
    http: SafeHttpClient,
    offer: BookAccessOffer,
    *,
    work_id: str,
    output_dir: Path,
    jurisdiction_approved: bool,
    clock: Callable[[], datetime],
) -> LegalCopyRecord:
    if not can_download_automatically(offer, jurisdiction_approved=jurisdiction_approved):
        raise ValueError("la oferta no es descargable automáticamente")
    assert offer.download_url is not None
    body = http.get_bytes(offer.download_url, allowed_types={"application/pdf"})
    if not body.startswith(b"%PDF"):
        raise NetworkPolicyError("el cuerpo no es un PDF")
    filename = _safe_pdf_name(offer)
    copies = output_dir / "copies"
    copies.mkdir(parents=True, exist_ok=True)
    path = copies / filename
    temporary = path.with_suffix(".pdf.tmp")
    temporary.write_bytes(body)
    temporary.replace(path)
    digest = hashlib.sha256(body).hexdigest()
    host = (urlsplit(offer.download_url).hostname or "").casefold()
    copy_id = f"cpy_{hashlib.sha256(f'{work_id}:{digest}'.encode()).hexdigest()[:16]}"
    return LegalCopyRecord(
        copy_id=copy_id,
        work_id=work_id,
        offer_id=offer.offer_id,
        provider=offer.provider,
        filename=f"copies/{filename}",
        sha256=digest,
        size_bytes=len(body),
        source_host=host,
        rights_status=offer.rights_status,
        downloaded_at=clock(),
        content_hash="0" * 64,
    )


def run_library_loop(
    *,
    source: Path,
    output_root: Path,
    http: SafeHttpClient,
    jurisdiction: str,
    languages: tuple[str, ...],
    max_rounds: int,
    jurisdiction_approved: bool,
    providers: tuple[str, ...] = DEFAULT_LIBRARY_PROVIDERS,
    max_books: int | None = None,
    clock: Callable[[], datetime] | None = None,
) -> LibraryLoopReport:
    if not jurisdiction.strip():
        raise ValueError("jurisdiction es obligatoria")
    if not 1 <= max_rounds <= 8:
        raise ValueError("max_rounds debe estar entre 1 y 8")
    now_fn = clock or (lambda: datetime.now(UTC))
    output_root = resolve_lab_output_root(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    cards = inventory_library_cards(source)
    if max_books is not None:
        cards = cards[: max(0, max_books)]
    researcher = BookResearcher(http, clock=now_fn)
    works: list[LibraryWorkRecord] = []
    warnings: list[str] = []
    for card in cards:
        existing = _load_work(output_root / card.work_id / "work.json")
        if existing is not None and existing.status in COMPLETE_STATUSES:
            works.append(existing)
            continue
        work_dir = output_root / card.work_id
        work_dir.mkdir(parents=True, exist_ok=True)
        rounds_used = 0
        work_warnings: list[str] = []
        report: BookResearchReport | None = None
        offers: list[BookAccessOffer] = []
        copy: LegalCopyRecord | None = existing.legal_copy if existing else None
        status = LibraryWorkStatus.RESEARCHING
        gaps = ["investigación no iniciada"]
        try:
            while rounds_used < max_rounds:
                rounds_used += 1
                if report is None:
                    report = researcher.research(
                        title=card.title,
                        author=card.author,
                        isbn=card.isbn,
                        jurisdiction=jurisdiction,
                        languages=languages,
                        providers=providers,
                        max_results=8,
                    )
                    offers = list(report.offers)
                    work_warnings.extend(report.warnings)
                offers, enrich_warnings = _enrich_archive_offers(http, offers)
                work_warnings.extend(enrich_warnings)
                if copy is None:
                    copy, download_warnings = _acquire_first_copy(
                        http,
                        offers,
                        work_id=card.work_id,
                        work_dir=work_dir,
                        jurisdiction_approved=jurisdiction_approved,
                        clock=now_fn,
                    )
                    work_warnings.extend(download_warnings)
                gaps = _gaps(card, offers, copy, jurisdiction_approved)
                if _is_complete(card, offers, copy, jurisdiction_approved):
                    status = (
                        LibraryWorkStatus.COPY_ACQUIRED
                        if copy is not None
                        else LibraryWorkStatus.DOSSIER_READY
                    )
                    break
                if not _has_pending_archive_metadata(offers) or rounds_used >= max_rounds:
                    status = LibraryWorkStatus.INCONCLUSIVE
                    break
        except (NetworkDisabled, NetworkPolicyError, ValueError) as exc:
            status = LibraryWorkStatus.FAILED
            gaps = [f"la corrida falló: {exc}"]
            work_warnings.append(str(exc))
            warnings.append(f"{card.title}: {exc}")
        report_path = None
        if report is not None:
            report_path = "report.json"
            _write_json(work_dir / report_path, report.model_dump(mode="json"))
        dossier = render_dossier(
            card,
            offers=offers,
            copy=copy,
            gaps=_gaps(card, offers, copy, jurisdiction_approved)
            if status != LibraryWorkStatus.FAILED
            else gaps,
            warnings=work_warnings,
            status=status,
        )
        (work_dir / "dossier.md").write_text(dossier, encoding="utf-8", newline="\n")
        work = LibraryWorkRecord(
            work_id=card.work_id,
            status=status,
            card=card,
            rounds_used=rounds_used,
            offers_count=len(offers),
            downloadable_offers=sum(
                1
                for offer in offers
                if can_download_automatically(offer, jurisdiction_approved=jurisdiction_approved)
            ),
            legal_copy=copy,
            gaps=_gaps(card, offers, copy, jurisdiction_approved)
            if status != LibraryWorkStatus.FAILED
            else gaps,
            warnings=work_warnings[:40],
            dossier_path="dossier.md",
            report_path=report_path,
            updated_at=now_fn(),
            content_hash="0" * 64,
        )
        _write_json(work_dir / "work.json", work.model_dump(mode="json"))
        works.append(work)
    report = LibraryLoopReport.create(
        jurisdiction=jurisdiction,
        languages=list(languages),
        inventory_count=len(cards),
        works=works,
        warnings=warnings,
        created_at=now_fn(),
    )
    _write_json(output_root / "index.json", report.model_dump(mode="json"))
    return report


def render_dossier(
    card,
    *,
    offers: list[BookAccessOffer],
    copy: LegalCopyRecord | None,
    gaps: list[str],
    warnings: list[str],
    status: LibraryWorkStatus,
) -> str:
    lines = [
        f"# {card.title}",
        f"**Autor:** {card.author or 'desconocido'}",
        "",
        "## Identidad",
        f"- **work_id:** `{card.work_id}`",
        f"- **Año:** {card.year or 'no declarado en la ficha'}",
        f"- **ISBN:** {card.isbn or 'no declarado en la ficha'}",
        f"- **Estado del loop:** `{status.value}`",
        "",
        "## Ofertas de acceso",
    ]
    if not offers:
        lines.append("Ningún catálogo devolvió una coincidencia utilizable.")
    else:
        lines.append("| Proveedor | Modo | Derechos | Descarga |")
        lines.append("|---|---|---|---|")
        for offer in offers:
            download = "sí" if offer.download_url else "no"
            lines.append(
                f"| {offer.provider} | {offer.access_mode.value} | "
                f"{offer.rights_status.value} | {download} |"
            )
    lines.extend(["", "## Copia local"])
    if copy is None:
        lines.append(
            "No hay copia local. Solo se descarga PDF con `full_download` y derechos "
            "elegibles con evidencia."
        )
    else:
        lines.append(f"- **Archivo:** `{copy.filename}`")
        lines.append(f"- **SHA-256:** `{copy.sha256}`")
        lines.append(f"- **Proveedor:** {copy.provider}")
        lines.append(f"- **Host:** {copy.source_host}")
    lines.extend(["", "## Hechos públicos ya presentes"])
    if card.excerpt:
        lines.append(card.excerpt)
    else:
        lines.append("La ficha de origen no traía descripción pública reutilizable.")
    if card.existing_links:
        lines.extend(["", "## Enlaces de la ficha original"])
        for label, url in card.existing_links.items():
            lines.append(f"- **{label}:** {url}")
    lines.extend(["", "## Huecos"])
    for gap in gaps:
        lines.append(f"- {gap}")
    if warnings:
        lines.extend(["", "## Advertencias"])
        for item in warnings[:20]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "---",
            "*Dossier generado por el loop de biblioteca del curador. "
            "No reconstruye el texto de una obra protegida.*",
            "",
        ]
    )
    return "\n".join(lines)


def export_library_markdown(
    library_root: Path,
    destination: Path,
    *,
    authorize_export: bool,
) -> list[Path]:
    if not authorize_export:
        raise ValueError("library export exige --authorize-export")
    index_path = library_root / "index.json"
    if not index_path.is_file():
        raise ValueError("no hay index.json de biblioteca para exportar")
    dest = destination.resolve()
    if not dest.is_dir():
        raise ValueError("el destino de exportación debe ser un directorio existente")
    report = LibraryLoopReport.model_validate_json(index_path.read_text(encoding="utf-8"))
    written: list[Path] = []
    for work in report.works:
        target = dest / work.card.relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        dossier = (library_root / work.work_id / "dossier.md").read_text(encoding="utf-8")
        section = f"{CURATOR_SECTION_START}\n\n{dossier.strip()}\n\n{CURATOR_SECTION_END}\n"
        if target.is_file():
            current = target.read_text(encoding="utf-8")
            merged = _merge_curator_section(current, section)
        else:
            merged = section
        target.write_text(merged, encoding="utf-8", newline="\n")
        written.append(target)
    return written


def _merge_curator_section(current: str, section: str) -> str:
    pattern = re.compile(
        re.escape(CURATOR_SECTION_START) + r".*?" + re.escape(CURATOR_SECTION_END),
        re.DOTALL,
    )
    if pattern.search(current):
        return pattern.sub(section.strip(), current).rstrip() + "\n"
    return current.rstrip() + "\n\n" + section


def _enrich_archive_offers(
    http: SafeHttpClient,
    offers: list[BookAccessOffer],
) -> tuple[list[BookAccessOffer], list[str]]:
    warnings: list[str] = []
    updated: list[BookAccessOffer] = []
    remaining = 3
    for offer in offers:
        eligible = (
            offer.provider == "internet_archive"
            and offer.download_url is None
            and offer.access_mode != AccessMode.BORROW
            and offer.rights_status.value in {"public_domain", "open_license"}
            and remaining > 0
        )
        if not eligible:
            updated.append(offer)
            continue
        remaining -= 1
        try:
            metadata = http.get_json(internet_archive_metadata_url(offer.provider_record_id))
            updated.append(apply_internet_archive_files(offer, metadata))
        except (NetworkDisabled, NetworkPolicyError, ValueError) as exc:
            warnings.append(f"internet_archive metadata: {exc}")
            updated.append(offer)
    return updated, warnings


def _acquire_first_copy(
    http: SafeHttpClient,
    offers: list[BookAccessOffer],
    *,
    work_id: str,
    work_dir: Path,
    jurisdiction_approved: bool,
    clock: Callable[[], datetime],
) -> tuple[LegalCopyRecord | None, list[str]]:
    warnings: list[str] = []
    for offer in offers:
        if not can_download_automatically(offer, jurisdiction_approved=jurisdiction_approved):
            continue
        try:
            copy = download_legal_copy(
                http,
                offer,
                work_id=work_id,
                output_dir=work_dir,
                jurisdiction_approved=jurisdiction_approved,
                clock=clock,
            )
            _write_json(work_dir / "copy.json", copy.model_dump(mode="json"))
            return copy, warnings
        except (NetworkDisabled, NetworkPolicyError, ValueError) as exc:
            warnings.append(f"{offer.provider}: descarga legal fallida: {exc}")
    return None, warnings


def _has_pending_archive_metadata(offers: list[BookAccessOffer]) -> bool:
    return any(
        offer.provider == "internet_archive"
        and offer.download_url is None
        and offer.access_mode != AccessMode.BORROW
        and offer.rights_status.value in {"public_domain", "open_license"}
        for offer in offers
    )


def _is_complete(card, offers: list[BookAccessOffer], copy, jurisdiction_approved: bool) -> bool:
    if not card.title or not card.author:
        return False
    if not offers:
        return False
    eligible = [
        offer
        for offer in offers
        if can_download_automatically(offer, jurisdiction_approved=jurisdiction_approved)
    ]
    return not (eligible and copy is None)


def _gaps(card, offers: list[BookAccessOffer], copy, jurisdiction_approved: bool) -> list[str]:
    gaps: list[str] = []
    if not card.year:
        gaps.append("la ficha no declara año")
    if not card.isbn:
        gaps.append("la ficha no declara ISBN; se usó título/autor en los catálogos")
    if not offers:
        gaps.append("ningún catálogo devolvió una oferta utilizable")
    eligible = [
        offer
        for offer in offers
        if can_download_automatically(offer, jurisdiction_approved=jurisdiction_approved)
    ]
    if eligible and copy is None:
        gaps.append("hay PDF legal anunciado, pero la copia local aún no se conservó")
    if offers and not eligible:
        gaps.append(
            "no hay descarga automática: préstamo, preview o derechos restringidos no se copian"
        )
    if not gaps:
        gaps.append("sin huecos materiales de catálogo en este corte")
    return gaps[:40]


def _safe_pdf_name(offer: BookAccessOffer) -> str:
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", offer.provider_record_id).strip("-") or "copy"
    return f"{offer.provider}-{stem}.pdf"[:180]


def _load_work(path: Path) -> LibraryWorkRecord | None:
    if not path.is_file():
        return None
    try:
        return LibraryWorkRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)

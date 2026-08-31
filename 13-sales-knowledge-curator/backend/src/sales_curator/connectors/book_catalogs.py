"""Normalización estricta de catálogos bibliográficos oficiales."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlencode, urlsplit

from sales_curator.contracts.research import AccessMode, BookAccessOffer, RightsStatus

OPEN_LIBRARY_RIGHTS = "https://openlibrary.org/help/faq/reading"
GOOGLE_BOOKS_RIGHTS = "https://developers.google.com/books/docs/v1/reference/volumes"


def _offer_id(provider: str, record_id: str) -> str:
    digest = hashlib.sha256(f"{provider}:{record_id}".encode()).hexdigest()[:16]
    return f"ofr_{digest}"


def _language(value: str | None) -> str | None:
    mapping = {"eng": "en", "spa": "es"}
    if not value:
        return None
    return mapping.get(value.casefold(), value.casefold())


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _trusted_https_url(value: str, *, hosts: set[str]) -> bool:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme.casefold() == "https"
        and parsed.hostname
        and parsed.hostname.casefold() in hosts
        and parsed.username is None
        and parsed.password is None
        and port in {None, 443}
    )


def parse_open_library(
    payload: dict[str, Any],
    *,
    retrieved_at: datetime,
    jurisdiction: str,
) -> list[BookAccessOffer]:
    offers: list[BookAccessOffer] = []
    for raw in payload.get("docs") or []:
        if not isinstance(raw, dict) or not raw.get("title") or not raw.get("key"):
            continue
        record_id = str(raw["key"]).strip("/").replace("/", "-")
        access_raw = str(raw.get("ebook_access") or "no_ebook").casefold()
        if access_raw == "borrowable" or raw.get("lending_edition_s"):
            access = AccessMode.BORROW
            statement = "Open Library anuncia préstamo controlado; no es una copia descargable."
        elif access_raw == "public":
            access = AccessMode.READ_ONLINE
            statement = (
                "Open Library anuncia lectura pública, pero ese dato no demuestra por sí solo "
                "dominio público en la jurisdicción configurada."
            )
        elif access_raw == "printdisabled_only":
            access = AccessMode.READ_ONLINE
            statement = "Acceso de lectura condicionado por el proveedor; no descargable."
        elif raw.get("ia"):
            access = AccessMode.PREVIEW
            statement = "Existe un registro digital asociado; derechos y descarga no verificados."
        else:
            access = AccessMode.CATALOG_ONLY
            statement = "Registro bibliográfico sin copia digital verificada."
        isbns = _strings(raw.get("isbn"))
        identifiers = {"isbn": isbns} if isbns else {}
        language_values = _strings(raw.get("language"))
        offers.append(
            BookAccessOffer(
                offer_id=_offer_id("open_library", record_id),
                provider="open_library",
                provider_record_id=record_id,
                title=str(raw["title"]),
                authors=_strings(raw.get("author_name")),
                identifiers=identifiers,
                language=_language(language_values[0]) if language_values else None,
                published_date=str(raw.get("first_publish_year"))
                if raw.get("first_publish_year")
                else None,
                record_url=f"https://openlibrary.org/{str(raw['key']).lstrip('/')}",
                access_mode=access,
                rights_status=RightsStatus.UNKNOWN,
                rights_evidence_url=OPEN_LIBRARY_RIGHTS,
                rights_statement=statement,
                download_url=None,
                jurisdiction=jurisdiction,
                retrieved_at=retrieved_at,
            )
        )
    return offers


def parse_google_books(
    payload: dict[str, Any],
    *,
    retrieved_at: datetime,
    jurisdiction: str,
) -> list[BookAccessOffer]:
    offers: list[BookAccessOffer] = []
    for raw in payload.get("items") or []:
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        info = raw.get("volumeInfo") if isinstance(raw.get("volumeInfo"), dict) else {}
        access_info = raw.get("accessInfo") if isinstance(raw.get("accessInfo"), dict) else {}
        title = str(info.get("title") or "").strip()
        if not title:
            continue
        record_id = str(raw["id"])
        public_domain = access_info.get("publicDomain") is True
        access_status = str(access_info.get("accessViewStatus") or "").upper()
        viewability = str(access_info.get("viewability") or "NO_PAGES").upper()
        pdf = access_info.get("pdf") if isinstance(access_info.get("pdf"), dict) else {}
        raw_download = str(pdf.get("downloadLink") or "").strip()
        complete_public = bool(
            public_domain
            and access_status == "FULL_PUBLIC_DOMAIN"
            and pdf.get("isAvailable") is True
            and _trusted_https_url(raw_download, hosts={"books.google.com"})
        )
        if complete_public:
            mode = AccessMode.FULL_DOWNLOAD
            rights = RightsStatus.PUBLIC_DOMAIN
            download_url = raw_download
            statement = (
                "Google Books declara publicDomain=true y FULL_PUBLIC_DOMAIN, con enlace PDF; "
                "la jurisdicción aún debe estar aprobada."
            )
        elif viewability in {"PARTIAL", "ALL_PAGES"} or access_status == "SAMPLE":
            mode = AccessMode.PREVIEW if viewability == "PARTIAL" else AccessMode.READ_ONLINE
            rights = RightsStatus.RESTRICTED
            download_url = None
            statement = "Vista previa o lectura del proveedor; no autoriza conservar una copia."
        else:
            mode = AccessMode.CATALOG_ONLY
            rights = RightsStatus.UNKNOWN
            download_url = None
            statement = "Registro bibliográfico sin descarga pública verificada."
        identifiers: dict[str, list[str]] = {}
        for row in info.get("industryIdentifiers") or []:
            if not isinstance(row, dict) or not row.get("identifier"):
                continue
            key = str(row.get("type") or "other").casefold()
            identifiers.setdefault(key, []).append(str(row["identifier"]))
        raw_record_url = str(info.get("infoLink") or "").strip()
        record_url = (
            raw_record_url
            if _trusted_https_url(raw_record_url, hosts={"books.google.com"})
            else f"https://books.google.com/books?{urlencode({'id': record_id})}"
        )
        offers.append(
            BookAccessOffer(
                offer_id=_offer_id("google_books", record_id),
                provider="google_books",
                provider_record_id=record_id,
                title=title,
                authors=_strings(info.get("authors")),
                identifiers=identifiers,
                language=_language(str(info.get("language") or "") or None),
                published_date=str(info.get("publishedDate"))
                if info.get("publishedDate")
                else None,
                record_url=record_url,
                access_mode=mode,
                rights_status=rights,
                rights_evidence_url=GOOGLE_BOOKS_RIGHTS,
                rights_statement=statement,
                download_url=download_url,
                jurisdiction=jurisdiction,
                retrieved_at=retrieved_at,
            )
        )
    return offers

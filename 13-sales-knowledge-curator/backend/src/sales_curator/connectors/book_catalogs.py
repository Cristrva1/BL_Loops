"""Normalización estricta de catálogos bibliográficos oficiales."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import quote, urlencode, urlsplit

from sales_curator.contracts.research import AccessMode, BookAccessOffer, RightsStatus

OPEN_LIBRARY_RIGHTS = "https://openlibrary.org/help/faq/reading"
GOOGLE_BOOKS_RIGHTS = "https://developers.google.com/books/docs/v1/reference/volumes"
GUTENBERG_RIGHTS = "https://www.gutenberg.org/policy/license.html"
INTERNET_ARCHIVE_RIGHTS = "https://archive.org/about/terms.php"
GUTENBERG_DOWNLOAD_HOSTS = {"gutenberg.org", "www.gutenberg.org"}
INTERNET_ARCHIVE_HOSTS = {"archive.org"}
CREATIVE_COMMONS_HOSTS = {"creativecommons.org", "www.creativecommons.org"}
RESTRICTED_LICENSE_MARKERS = (
    "/by-nc",
    "/by-nd",
    "/by-nc-nd",
    "/by-nc-sa",
)


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


def _https_url(value: str, *, hosts: set[str]) -> str | None:
    raw = value.strip()
    if raw.startswith("http://"):
        raw = "https://" + raw[len("http://") :]
    if _trusted_https_url(raw, hosts=hosts):
        return raw
    return None


def _license_status(license_url: str | None) -> RightsStatus:
    if not license_url:
        return RightsStatus.UNKNOWN
    lowered = license_url.casefold()
    if any(marker in lowered for marker in RESTRICTED_LICENSE_MARKERS):
        return RightsStatus.RESTRICTED
    if "publicdomain" in lowered or "/licenses/cc0" in lowered or "/zero/" in lowered:
        return RightsStatus.PUBLIC_DOMAIN
    if "/licenses/by-sa/" in lowered or "/licenses/by/" in lowered:
        return RightsStatus.OPEN_LICENSE
    return RightsStatus.UNKNOWN


def parse_gutenberg(
    payload: dict[str, Any],
    *,
    retrieved_at: datetime,
    jurisdiction: str,
) -> list[BookAccessOffer]:
    offers: list[BookAccessOffer] = []
    for raw in payload.get("results") or []:
        if not isinstance(raw, dict) or not raw.get("id") or not raw.get("title"):
            continue
        record_id = str(raw["id"])
        formats = raw.get("formats") if isinstance(raw.get("formats"), dict) else {}
        pdf_url = None
        for mime, candidate in formats.items():
            if "application/pdf" not in str(mime).casefold():
                continue
            trusted = _https_url(str(candidate or ""), hosts=GUTENBERG_DOWNLOAD_HOSTS)
            if trusted:
                pdf_url = trusted
                break
        copyrighted = raw.get("copyright") is True
        if copyrighted:
            access = AccessMode.CATALOG_ONLY
            rights = RightsStatus.RESTRICTED
            download_url = None
            statement = (
                "Project Gutenberg marca la obra como protegida; no se expone descarga automática."
            )
        elif pdf_url:
            access = AccessMode.FULL_DOWNLOAD
            rights = RightsStatus.PUBLIC_DOMAIN
            download_url = pdf_url
            statement = (
                "Gutendex/Gutenberg declara copyright=false y PDF en un host de Gutenberg; "
                "la jurisdicción configurada aún debe estar aprobada."
            )
        else:
            access = AccessMode.READ_ONLINE
            rights = RightsStatus.PUBLIC_DOMAIN
            download_url = None
            statement = (
                "Gutenberg anuncia texto sin copyright, pero no hay PDF verificable en este corte."
            )
        authors = []
        for row in raw.get("authors") or []:
            if isinstance(row, dict) and row.get("name"):
                authors.append(str(row["name"]))
        language_values = _strings(raw.get("languages"))
        offers.append(
            BookAccessOffer(
                offer_id=_offer_id("project_gutenberg", record_id),
                provider="project_gutenberg",
                provider_record_id=record_id,
                title=str(raw["title"]),
                authors=authors,
                identifiers={"gutenberg": [record_id]},
                language=_language(language_values[0]) if language_values else None,
                published_date=None,
                record_url=f"https://www.gutenberg.org/ebooks/{record_id}",
                access_mode=access,
                rights_status=rights,
                rights_evidence_url=GUTENBERG_RIGHTS,
                rights_statement=statement,
                download_url=download_url,
                jurisdiction=jurisdiction,
                retrieved_at=retrieved_at,
            )
        )
    return offers


def parse_internet_archive(
    payload: dict[str, Any],
    *,
    retrieved_at: datetime,
    jurisdiction: str,
) -> list[BookAccessOffer]:
    offers: list[BookAccessOffer] = []
    response = payload.get("response") if isinstance(payload.get("response"), dict) else payload
    docs = response.get("docs") if isinstance(response, dict) else None
    for raw in docs or []:
        if not isinstance(raw, dict) or not raw.get("identifier") or not raw.get("title"):
            continue
        record_id = str(raw["identifier"]).strip()
        if not record_id or "/" in record_id or ".." in record_id:
            continue
        restricted = raw.get("access-restricted-item") in {True, "true", "1"}
        license_url = None
        raw_license = raw.get("licenseurl")
        if isinstance(raw_license, list) and raw_license:
            raw_license = raw_license[0]
        if isinstance(raw_license, str):
            license_url = _https_url(
                raw_license,
                hosts=CREATIVE_COMMONS_HOSTS | INTERNET_ARCHIVE_HOSTS,
            )
        rights = RightsStatus.UNKNOWN if restricted else _license_status(license_url)
        if restricted:
            access = AccessMode.BORROW
            statement = (
                "Internet Archive marca acceso restringido o préstamo; no es una copia descargable."
            )
        elif rights in {RightsStatus.PUBLIC_DOMAIN, RightsStatus.OPEN_LICENSE}:
            access = AccessMode.CATALOG_ONLY
            statement = (
                "La búsqueda indica licencia abierta, pero el PDF solo se confirma con metadatos."
            )
        else:
            access = AccessMode.CATALOG_ONLY
            statement = "Registro de Internet Archive sin licencia abierta verificable."
        creators = raw.get("creator")
        authors = [creators] if isinstance(creators, str) else _strings(creators)
        language_raw = raw.get("language")
        if isinstance(language_raw, list) and language_raw:
            language_raw = language_raw[0]
        offers.append(
            BookAccessOffer(
                offer_id=_offer_id("internet_archive", record_id),
                provider="internet_archive",
                provider_record_id=record_id,
                title=str(raw["title"]),
                authors=authors,
                identifiers={"archive": [record_id]},
                language=_language(str(language_raw) if language_raw else None),
                published_date=str(raw.get("year")) if raw.get("year") else None,
                record_url=f"https://archive.org/details/{record_id}",
                access_mode=access,
                rights_status=rights,
                rights_evidence_url=license_url or INTERNET_ARCHIVE_RIGHTS,
                rights_statement=statement,
                download_url=None,
                jurisdiction=jurisdiction,
                retrieved_at=retrieved_at,
            )
        )
    return offers


def apply_internet_archive_files(
    offer: BookAccessOffer,
    metadata: dict[str, Any],
) -> BookAccessOffer:
    if offer.provider != "internet_archive":
        raise ValueError("solo se enriquecen ofertas de Internet Archive")
    if offer.access_mode == AccessMode.BORROW:
        return offer
    if offer.rights_status not in {RightsStatus.PUBLIC_DOMAIN, RightsStatus.OPEN_LICENSE}:
        return offer
    files = metadata.get("files") if isinstance(metadata.get("files"), list) else []
    pdf_name = None
    for item in files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip().lstrip("/")
        fmt = str(item.get("format") or "").casefold()
        parts = [part for part in name.replace("\\", "/").split("/") if part]
        if not parts or any(part == ".." for part in parts):
            continue
        joined = "/".join(parts)
        if not joined.casefold().endswith(".pdf"):
            continue
        if "pdf" in fmt or joined.casefold().endswith(".pdf"):
            pdf_name = joined
            break
    if not pdf_name:
        return offer
    download_url = (
        f"https://archive.org/download/{offer.provider_record_id}/{quote(pdf_name, safe='/')}"
    )
    if not _trusted_https_url(download_url, hosts=INTERNET_ARCHIVE_HOSTS):
        return offer
    return offer.model_copy(
        update={
            "access_mode": AccessMode.FULL_DOWNLOAD,
            "download_url": download_url,
            "rights_statement": (
                "Metadatos de Internet Archive confirman PDF y licencia abierta o dominio público."
            ),
            "content_hash": "0" * 64,
        }
    )

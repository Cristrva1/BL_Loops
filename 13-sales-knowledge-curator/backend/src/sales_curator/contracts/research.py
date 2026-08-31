"""Contratos para investigación bibliográfica, derechos y paquetes portables."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from sales_curator.contracts.models import HASH_PATTERN, ID_PATTERN, StrictModel


def _hash_payload(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class RightsStatus(StrEnum):
    PUBLIC_DOMAIN = "public_domain"
    OPEN_LICENSE = "open_license"
    EXPLICIT_PERMISSION = "explicit_permission"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class AccessMode(StrEnum):
    FULL_DOWNLOAD = "full_download"
    READ_ONLINE = "read_online"
    PREVIEW = "preview"
    BORROW = "borrow"
    CATALOG_ONLY = "catalog_only"


class DocumentRights(StrictModel):
    rights_status: RightsStatus
    license: str = Field(min_length=2, max_length=160)
    usage_basis: str = Field(min_length=8, max_length=300)
    jurisdiction: str = Field(min_length=2, max_length=40)
    retention_allowed: bool
    extraction_allowed: bool
    quotation_allowed: bool
    redistribution_allowed: bool
    notebooklm_upload_allowed: bool
    evidence: str = Field(min_length=8, max_length=500)

    @model_validator(mode="after")
    def require_permission_for_processing(self) -> DocumentRights:
        if not self.retention_allowed or not self.extraction_allowed:
            raise ValueError("la importación requiere permiso de retención y extracción")
        if self.rights_status in {
            RightsStatus.RESTRICTED,
            RightsStatus.UNKNOWN,
        } and (self.redistribution_allowed or self.notebooklm_upload_allowed):
            raise ValueError("derechos restringidos/desconocidos no permiten redistribuir ni subir")
        return self


class BookAccessOffer(StrictModel):
    offer_id: str = Field(pattern=ID_PATTERN)
    provider: Literal[
        "open_library",
        "google_books",
        "project_gutenberg",
        "doab_oapen",
        "library_of_congress",
        "internet_archive",
        "hathitrust",
        "bne",
        "europeana",
    ]
    provider_record_id: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=400)
    authors: list[str] = Field(default_factory=list, max_length=30)
    identifiers: dict[str, list[str]] = Field(default_factory=dict)
    language: str | None = Field(default=None, max_length=20)
    published_date: str | None = Field(default=None, max_length=40)
    record_url: str = Field(min_length=8, max_length=1000)
    access_mode: AccessMode
    rights_status: RightsStatus
    rights_evidence_url: str | None = Field(default=None, max_length=1000)
    rights_statement: str = Field(min_length=8, max_length=600)
    download_url: str | None = Field(default=None, max_length=1000)
    jurisdiction: str = Field(min_length=2, max_length=40)
    retrieved_at: datetime
    content_hash: str = Field(default="0" * 64, pattern=HASH_PATTERN)

    @model_validator(mode="after")
    def protect_download_link(self) -> BookAccessOffer:
        eligible_rights = {
            RightsStatus.PUBLIC_DOMAIN,
            RightsStatus.OPEN_LICENSE,
            RightsStatus.EXPLICIT_PERMISSION,
        }
        if self.download_url and (
            self.access_mode != AccessMode.FULL_DOWNLOAD
            or self.rights_status not in eligible_rights
            or not self.rights_evidence_url
        ):
            raise ValueError(
                "download_url exige descarga completa y evidencia de derechos suficiente"
            )
        if self.retrieved_at.tzinfo is None or self.retrieved_at.utcoffset() is None:
            raise ValueError("retrieved_at debe incluir zona horaria")
        if self.content_hash == "0" * 64:
            payload = self.model_dump(mode="json", exclude={"content_hash"})
            object.__setattr__(self, "content_hash", _hash_payload(payload))
        return self


def can_download_automatically(
    offer: BookAccessOffer,
    *,
    jurisdiction_approved: bool,
) -> bool:
    return bool(
        jurisdiction_approved
        and offer.access_mode == AccessMode.FULL_DOWNLOAD
        and offer.rights_status
        in {
            RightsStatus.PUBLIC_DOMAIN,
            RightsStatus.OPEN_LICENSE,
            RightsStatus.EXPLICIT_PERMISSION,
        }
        and offer.download_url
        and offer.rights_evidence_url
        and offer.jurisdiction.strip()
    )


class BookResearchReport(StrictModel):
    research_id: str = Field(pattern=ID_PATTERN)
    query: str = Field(min_length=2, max_length=400)
    jurisdiction: str = Field(min_length=2, max_length=40)
    languages: list[str] = Field(min_length=1, max_length=10)
    offers: list[BookAccessOffer] = Field(default_factory=list, max_length=1000)
    warnings: list[str] = Field(default_factory=list, max_length=100)
    created_at: datetime
    content_hash: str = Field(pattern=HASH_PATTERN)

    @classmethod
    def create(
        cls,
        *,
        query: str,
        jurisdiction: str,
        languages: list[str],
        offers: list[BookAccessOffer],
        warnings: list[str],
        created_at: datetime | None = None,
    ) -> BookResearchReport:
        when = created_at or datetime.now(UTC)
        identity = _hash_payload(
            {
                "query": query,
                "jurisdiction": jurisdiction,
                "languages": languages,
                "offers": [item.content_hash for item in offers],
            }
        )
        payload = {
            "research_id": f"res_{identity[:16]}",
            "query": query,
            "jurisdiction": jurisdiction,
            "languages": languages,
            "offers": offers,
            "warnings": warnings,
            "created_at": when,
        }
        return cls(**payload, content_hash=_hash_payload(_jsonable(payload)))


def _jsonable(payload: dict) -> dict:
    return json.loads(
        json.dumps(
            payload,
            ensure_ascii=False,
            default=lambda value: (
                value.model_dump(mode="json") if hasattr(value, "model_dump") else value.isoformat()
            ),
        )
    )


class DocumentImportRecord(StrictModel):
    document_id: str = Field(pattern=ID_PATTERN)
    source_file_name: str = Field(min_length=1, max_length=260)
    source_media_type: Literal[
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    title: str = Field(min_length=3, max_length=300)
    author: str = Field(min_length=1, max_length=200)
    language: Literal["en", "es"]
    topics: list[str] = Field(default_factory=list, max_length=20)
    original_sha256: str = Field(pattern=HASH_PATTERN)
    markdown_sha256: str = Field(pattern=HASH_PATTERN)
    extractor: Literal["markitdown"] = "markitdown"
    extractor_version: str = Field(min_length=1, max_length=40)
    locator_strategy: str = Field(min_length=8, max_length=200)
    markdown_path: str = Field(min_length=1, max_length=500)
    manifest_path: str = Field(min_length=1, max_length=500)
    rights: DocumentRights
    warnings: list[str] = Field(default_factory=list, max_length=30)
    created_at: datetime
    content_hash: str = Field(pattern=HASH_PATTERN)


class WebCaptureRecord(StrictModel):
    capture_id: str = Field(pattern=ID_PATTERN)
    source_id: str = Field(pattern=ID_PATTERN)
    requested_url: str = Field(min_length=8, max_length=1000)
    final_url: str = Field(min_length=8, max_length=1000)
    title: str = Field(min_length=1, max_length=400)
    language: Literal["en", "es"]
    status_code: int = Field(ge=200, lt=300)
    extractor: Literal["crawl4ai"] = "crawl4ai"
    extractor_version: str = Field(min_length=1, max_length=40)
    robots_allowed: Literal[True] = True
    markdown_sha256: str = Field(pattern=HASH_PATTERN)
    size_bytes: int = Field(gt=0, le=20_000_000)
    markdown_path: str = Field(min_length=1, max_length=500)
    manifest_path: str = Field(min_length=1, max_length=500)
    rights: DocumentRights
    retrieved_at: datetime
    warnings: list[str] = Field(default_factory=list, max_length=30)
    content_hash: str = Field(pattern=HASH_PATTERN)


class NotebookSourceSet(StrictModel):
    notebook_number: int = Field(ge=1)
    source_paths: list[str] = Field(max_length=50)


class NotebookPacket(StrictModel):
    packet_id: str = Field(pattern=ID_PATTERN)
    mode: Literal["manual_notebooklm_import"] = "manual_notebooklm_import"
    upload_performed: Literal[False] = False
    notebooks: list[NotebookSourceSet]
    manifest_path: str
    content_hash: str = Field(pattern=HASH_PATTERN)


class RagPacket(StrictModel):
    packet_id: str = Field(pattern=ID_PATTERN)
    records_path: str
    manifest_path: str
    record_count: int = Field(ge=0)
    content_hash: str = Field(pattern=HASH_PATTERN)

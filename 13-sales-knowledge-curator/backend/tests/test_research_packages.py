from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from sales_curator.config import lab_root
from sales_curator.contracts.research import (
    AccessMode,
    BookAccessOffer,
    BookResearchReport,
    RightsStatus,
)
from sales_curator.research.packages import build_notebooklm_packet, build_rag_packet


def _offer(index: int, *, restricted: bool = False) -> BookAccessOffer:
    return BookAccessOffer(
        offer_id=f"ofr_{index:03d}",
        provider="google_books",
        provider_record_id=f"book-{index}",
        title=f"Book {index}",
        authors=["A. Author"],
        identifiers={"isbn13": [f"978000000{index:04d}"]},
        language="en",
        published_date="1890" if not restricted else "2024",
        record_url=f"https://books.google.com/books?id={index}",
        access_mode=AccessMode.PREVIEW if restricted else AccessMode.FULL_DOWNLOAD,
        rights_status=RightsStatus.RESTRICTED if restricted else RightsStatus.PUBLIC_DOMAIN,
        rights_evidence_url="https://developers.google.com/books/docs/v1/reference/volumes",
        rights_statement="Provider metadata classification; operator must verify jurisdiction.",
        download_url=None if restricted else f"https://books.google.com/download?id={index}",
        jurisdiction="MX",
        retrieved_at=datetime(2026, 8, 30, tzinfo=UTC),
    )


def test_notebooklm_packet_is_manual_and_splits_at_fifty_sources(tmp_path: Path) -> None:
    report = BookResearchReport.create(
        query="sales education",
        jurisdiction="MX",
        languages=["en", "es"],
        offers=[_offer(index) for index in range(52)] + [_offer(99, restricted=True)],
        warnings=[],
    )
    packet = build_notebooklm_packet(report, tmp_path / "notebooklm", max_sources=50)
    assert packet.upload_performed is False
    assert len(packet.notebooks) == 2
    assert all(len(item.source_paths) <= 50 for item in packet.notebooks)
    manifest = json.loads((tmp_path / "notebooklm" / "manifest.json").read_text("utf-8"))
    assert manifest["upload_performed"] is False
    assert "manual" in manifest["mode"]
    assert "Book 99" in (tmp_path / "notebooklm" / "SOURCES.md").read_text("utf-8")


def test_rag_packet_exports_metadata_not_restricted_book_text(tmp_path: Path) -> None:
    report = BookResearchReport.create(
        query="consultative selling",
        jurisdiction="MX",
        languages=["en"],
        offers=[_offer(1), _offer(2, restricted=True)],
        warnings=[],
    )
    packet = build_rag_packet(report, tmp_path / "rag")
    rows = [
        json.loads(line)
        for line in (tmp_path / "rag" / packet.records_path).read_text("utf-8").splitlines()
    ]
    assert len(rows) == 2
    restricted = next(item for item in rows if item["rights_status"] == "restricted")
    assert restricted["download_url"] is None
    assert "content" not in restricted


def test_package_output_cannot_escape_lab() -> None:
    report = BookResearchReport.create(
        query="safe output",
        jurisdiction="MX",
        languages=["en"],
        offers=[],
        warnings=[],
    )
    with pytest.raises(ValueError, match="laboratorio"):
        build_rag_packet(report, lab_root().parent / "forbidden-research-output")

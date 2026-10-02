from __future__ import annotations

from datetime import UTC, datetime

from sales_curator.connectors.book_catalogs import (
    apply_internet_archive_files,
    parse_google_books,
    parse_gutenberg,
    parse_internet_archive,
    parse_open_library,
)
from sales_curator.contracts.research import AccessMode, RightsStatus, can_download_automatically

NOW = datetime(2026, 8, 30, tzinfo=UTC)


def test_open_library_borrow_is_never_treated_as_a_copy() -> None:
    rows = parse_open_library(
        {
            "docs": [
                {
                    "key": "/works/OL3902892W",
                    "title": "Influence",
                    "author_name": ["Robert Cialdini"],
                    "isbn": ["9780061241895"],
                    "language": ["eng"],
                    "first_publish_year": 1984,
                    "ebook_access": "borrowable",
                    "lending_edition_s": "OL123M",
                    "ia": ["influence0000cial"],
                }
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    assert len(rows) == 1
    offer = rows[0]
    assert offer.access_mode == AccessMode.BORROW
    assert offer.rights_status == RightsStatus.UNKNOWN
    assert offer.download_url is None
    assert can_download_automatically(offer, jurisdiction_approved=True) is False


def test_google_books_full_public_domain_needs_all_download_signals() -> None:
    rows = parse_google_books(
        {
            "items": [
                {
                    "id": "public-id",
                    "volumeInfo": {
                        "title": "A Public Book",
                        "authors": ["A. Author"],
                        "language": "en",
                        "publishedDate": "1890",
                        "industryIdentifiers": [{"type": "ISBN_13", "identifier": "9780000000002"}],
                        "infoLink": "https://books.google.com/books?id=public-id",
                    },
                    "accessInfo": {
                        "viewability": "ALL_PAGES",
                        "publicDomain": True,
                        "accessViewStatus": "FULL_PUBLIC_DOMAIN",
                        "pdf": {
                            "isAvailable": True,
                            "downloadLink": "https://books.google.com/books/download?id=public-id",
                        },
                    },
                }
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    offer = rows[0]
    assert offer.rights_status == RightsStatus.PUBLIC_DOMAIN
    assert offer.access_mode == AccessMode.FULL_DOWNLOAD
    assert can_download_automatically(offer, jurisdiction_approved=True) is True
    assert can_download_automatically(offer, jurisdiction_approved=False) is False


def test_google_books_preview_never_exposes_download_url() -> None:
    rows = parse_google_books(
        {
            "items": [
                {
                    "id": "preview-id",
                    "volumeInfo": {"title": "A Current Book", "authors": ["A. Writer"]},
                    "accessInfo": {
                        "viewability": "PARTIAL",
                        "publicDomain": False,
                        "accessViewStatus": "SAMPLE",
                        "pdf": {"isAvailable": True, "downloadLink": "https://example.test/no"},
                    },
                }
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    offer = rows[0]
    assert offer.access_mode == AccessMode.PREVIEW
    assert offer.rights_status == RightsStatus.RESTRICTED
    assert offer.download_url is None


def test_google_books_does_not_trust_external_links_from_catalog_payload() -> None:
    rows = parse_google_books(
        {
            "items": [
                {
                    "id": "tampered-id",
                    "volumeInfo": {
                        "title": "Tampered catalog row",
                        "infoLink": "https://evil.example/phishing",
                    },
                    "accessInfo": {
                        "viewability": "ALL_PAGES",
                        "publicDomain": True,
                        "accessViewStatus": "FULL_PUBLIC_DOMAIN",
                        "pdf": {
                            "isAvailable": True,
                            "downloadLink": "https://evil.example/payload.pdf",
                        },
                    },
                }
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    offer = rows[0]
    assert offer.record_url == "https://books.google.com/books?id=tampered-id"
    assert offer.access_mode == AccessMode.READ_ONLINE
    assert offer.rights_status == RightsStatus.RESTRICTED
    assert offer.download_url is None


def test_gutenberg_pdf_on_official_host_is_downloadable() -> None:
    rows = parse_gutenberg(
        {
            "results": [
                {
                    "id": 1342,
                    "title": "Pride and Prejudice",
                    "authors": [{"name": "Austen, Jane"}],
                    "languages": ["en"],
                    "copyright": False,
                    "formats": {
                        "application/pdf": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
                        "text/html": "https://www.gutenberg.org/ebooks/1342.html.images",
                    },
                }
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    offer = rows[0]
    assert offer.provider == "project_gutenberg"
    assert offer.access_mode == AccessMode.FULL_DOWNLOAD
    assert offer.rights_status == RightsStatus.PUBLIC_DOMAIN
    assert can_download_automatically(offer, jurisdiction_approved=True) is True


def test_gutenberg_ignores_off_host_pdf_and_copyrighted_rows() -> None:
    rows = parse_gutenberg(
        {
            "results": [
                {
                    "id": 1,
                    "title": "Tampered",
                    "copyright": False,
                    "formats": {"application/pdf": "https://evil.example/book.pdf"},
                },
                {
                    "id": 2,
                    "title": "Still Restricted",
                    "copyright": True,
                    "formats": {
                        "application/pdf": "https://www.gutenberg.org/files/2/2-pdf.pdf",
                    },
                },
            ]
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    assert rows[0].download_url is None
    assert can_download_automatically(rows[0], jurisdiction_approved=True) is False
    assert rows[1].rights_status == RightsStatus.RESTRICTED
    assert rows[1].download_url is None


def test_internet_archive_borrow_and_unlicensed_rows_are_not_copies() -> None:
    rows = parse_internet_archive(
        {
            "response": {
                "docs": [
                    {
                        "identifier": "influence0000cial",
                        "title": "Influence",
                        "creator": "Cialdini",
                        "access-restricted-item": True,
                    },
                    {
                        "identifier": "unknown-scan",
                        "title": "Unknown Scan",
                    },
                ]
            }
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    assert rows[0].access_mode == AccessMode.BORROW
    assert rows[0].download_url is None
    assert can_download_automatically(rows[0], jurisdiction_approved=True) is False
    assert rows[1].rights_status == RightsStatus.UNKNOWN
    assert rows[1].download_url is None


def test_internet_archive_metadata_can_expose_legal_pdf() -> None:
    [offer] = parse_internet_archive(
        {
            "response": {
                "docs": [
                    {
                        "identifier": "prideandprejudice",
                        "title": "Pride and Prejudice",
                        "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/",
                    }
                ]
            }
        },
        retrieved_at=NOW,
        jurisdiction="MX",
    )
    assert offer.download_url is None
    enriched = apply_internet_archive_files(
        offer,
        {
            "files": [
                {"name": "../escape.pdf", "format": "Text PDF"},
                {"name": "pride-and-prejudice.pdf", "format": "Text PDF"},
            ]
        },
    )
    assert enriched.access_mode == AccessMode.FULL_DOWNLOAD
    assert enriched.download_url == (
        "https://archive.org/download/prideandprejudice/pride-and-prejudice.pdf"
    )
    assert can_download_automatically(enriched, jurisdiction_approved=True) is True

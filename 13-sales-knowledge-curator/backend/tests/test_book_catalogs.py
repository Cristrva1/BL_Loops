from __future__ import annotations

from datetime import UTC, datetime

from sales_curator.connectors.book_catalogs import parse_google_books, parse_open_library
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

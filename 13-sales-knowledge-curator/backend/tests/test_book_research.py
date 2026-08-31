from __future__ import annotations

import json
from datetime import UTC, datetime

import httpx

from sales_curator.connectors.network import NetworkPolicy, SafeHttpClient
from sales_curator.research.books import BookResearcher


def _resolver(_host: str) -> tuple[str, ...]:
    return ("142.250.72.14",)


def test_cross_catalog_research_keeps_partial_failures_visible() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "openlibrary.org":
            return httpx.Response(503, headers={"content-type": "application/json"}, json={})
        assert request.url.host == "www.googleapis.com"
        payload = {
            "items": [
                {
                    "id": "gb-1",
                    "volumeInfo": {
                        "title": "SPIN Selling",
                        "authors": ["Neil Rackham"],
                        "language": "en",
                        "infoLink": "https://books.google.com/books?id=gb-1",
                    },
                    "accessInfo": {
                        "viewability": "PARTIAL",
                        "publicDomain": False,
                        "accessViewStatus": "SAMPLE",
                        "pdf": {"isAvailable": False},
                    },
                }
            ]
        }
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=json.dumps(payload).encode(),
        )

    policy = NetworkPolicy(
        network_enabled=True,
        runtime_network=True,
        real_connectors_enabled=True,
        allowed_domains=("openlibrary.org", "googleapis.com"),
        max_bytes=100_000,
        max_url_budget=4,
        user_agent="BL-Loops-SalesCurator/0.2 educational-research",
    ).authorize(run_authorized=True, url_budget=4)
    http = SafeHttpClient(
        policy,
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
    )
    report = BookResearcher(http, clock=lambda: datetime(2026, 8, 30, tzinfo=UTC)).research(
        title="SPIN Selling",
        author="Neil Rackham",
        isbn=None,
        jurisdiction="MX",
        languages=("en", "es"),
        providers=("open_library", "google_books"),
        max_results=5,
    )
    http.close()
    assert [item.provider for item in report.offers] == ["google_books"]
    assert any("open_library" in warning and "503" in warning for warning in report.warnings)
    assert report.query == "SPIN Selling — Neil Rackham"


def test_url_budget_exhaustion_is_a_visible_partial_failure() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=b'{"docs": []}',
        )

    policy = NetworkPolicy(
        network_enabled=True,
        runtime_network=True,
        real_connectors_enabled=True,
        allowed_domains=("openlibrary.org", "googleapis.com"),
        max_bytes=100_000,
        max_url_budget=1,
        user_agent="BL-Loops-SalesCurator/0.2 educational-research",
    ).authorize(run_authorized=True, url_budget=1)
    with SafeHttpClient(
        policy,
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
    ) as http:
        report = BookResearcher(http).research(
            title="Libro escolar",
            author=None,
            isbn=None,
            jurisdiction="MX",
            languages=("es",),
        )
    assert report.offers == []
    assert any(
        "google_books" in warning and "presupuesto" in warning for warning in report.warnings
    )

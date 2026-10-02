from __future__ import annotations

from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

import httpx
import pytest

from sales_curator.cli import cli
from sales_curator.config import Settings, lab_root
from sales_curator.connectors.network import NetworkPolicy, SafeHttpClient
from sales_curator.contracts.research import LibraryWorkStatus
from sales_curator.research.inventory import inventory_library_cards
from sales_curator.research.library import export_library_markdown, run_library_loop

NOW = datetime(2026, 9, 14, tzinfo=UTC)
FIXTURE_LIBRARY = lab_root() / "fixtures" / "library"
PDF_BYTES = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


def _resolver(_host: str) -> tuple[str, ...]:
    return ("142.250.72.14",)


def _policy(**overrides) -> NetworkPolicy:
    values = {
        "network_enabled": True,
        "runtime_network": True,
        "real_connectors_enabled": True,
        "allowed_domains": (
            "openlibrary.org",
            "googleapis.com",
            "gutendex.com",
            "gutenberg.org",
            "archive.org",
        ),
        "max_bytes": 100_000,
        "max_url_budget": 40,
        "user_agent": "BL-Loops-SalesCurator/0.2 educational-research",
    }
    values.update(overrides)
    return NetworkPolicy(**values).authorize(
        run_authorized=True, url_budget=values["max_url_budget"]
    )


def _empty_ol() -> dict:
    return {"docs": []}


def _empty_gb() -> dict:
    return {"items": []}


def _empty_ia() -> dict:
    return {"response": {"docs": []}}


def test_inventory_reads_book_cards_and_skips_bibliography() -> None:
    cards = inventory_library_cards(FIXTURE_LIBRARY)
    titles = {card.title for card in cards}
    assert titles == {"Influence: The Psychology of Persuasion", "Pride and Prejudice"}
    assert all(card.author for card in cards)
    assert all(not card.relative_path.lower().endswith("libros.md") for card in cards)


def _library_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    lowered = url.casefold()
    if request.url.host == "www.gutenberg.org" and request.url.path.endswith(".pdf"):
        return httpx.Response(
            200,
            headers={"content-type": "application/pdf"},
            content=PDF_BYTES,
        )
    if "evil.example" in lowered:
        raise AssertionError("el loop no debe solicitar un host pirateado")
    pride = "pride" in lowered
    if request.url.host == "openlibrary.org":
        payload = _empty_ol()
        if not pride:
            payload = {
                "docs": [
                    {
                        "key": "/works/OL3902892W",
                        "title": "Influence",
                        "author_name": ["Robert Cialdini"],
                        "ebook_access": "borrowable",
                        "lending_edition_s": "OL123M",
                    }
                ]
            }
        return httpx.Response(200, headers={"content-type": "application/json"}, json=payload)
    if request.url.host == "www.googleapis.com":
        payload = _empty_gb()
        if not pride:
            payload = {
                "items": [
                    {
                        "id": "gb-influence",
                        "volumeInfo": {"title": "Influence", "authors": ["Robert Cialdini"]},
                        "accessInfo": {
                            "viewability": "PARTIAL",
                            "publicDomain": False,
                            "accessViewStatus": "SAMPLE",
                            "pdf": {
                                "isAvailable": True,
                                "downloadLink": "https://evil.example/influence.pdf",
                            },
                        },
                    }
                ]
            }
        return httpx.Response(200, headers={"content-type": "application/json"}, json=payload)
    if request.url.host == "gutendex.com":
        if pride:
            payload = {
                "results": [
                    {
                        "id": 1342,
                        "title": "Pride and Prejudice",
                        "authors": [{"name": "Austen, Jane"}],
                        "languages": ["en"],
                        "copyright": False,
                        "formats": {
                            "application/pdf": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
                        },
                    }
                ]
            }
        else:
            payload = {"results": []}
        return httpx.Response(200, headers={"content-type": "application/json"}, json=payload)
    if request.url.host == "archive.org" and request.url.path.startswith("/metadata/"):
        return httpx.Response(200, headers={"content-type": "application/json"}, json={"files": []})
    if request.url.host == "archive.org":
        payload = _empty_ia()
        if not pride:
            payload = {
                "response": {
                    "docs": [
                        {
                            "identifier": "influence0000cial",
                            "title": "Influence",
                            "access-restricted-item": True,
                        }
                    ]
                }
            }
        return httpx.Response(200, headers={"content-type": "application/json"}, json=payload)
    return httpx.Response(404, headers={"content-type": "application/json"}, json={})


def test_library_loop_enriches_commercial_book_and_downloads_legal_pdf(settings: Settings) -> None:
    output = settings.library_path
    policy = _policy()
    with SafeHttpClient(
        policy,
        transport=httpx.MockTransport(_library_handler),
        resolver=_resolver,
    ) as http:
        report = run_library_loop(
            source=FIXTURE_LIBRARY,
            output_root=output,
            http=http,
            jurisdiction="MX",
            languages=("en", "es"),
            max_rounds=3,
            jurisdiction_approved=True,
            clock=lambda: NOW,
        )
    by_title = {work.card.title: work for work in report.works}
    influence = by_title["Influence: The Psychology of Persuasion"]
    pride = by_title["Pride and Prejudice"]
    assert influence.status == LibraryWorkStatus.DOSSIER_READY
    assert influence.legal_copy is None
    assert pride.status == LibraryWorkStatus.COPY_ACQUIRED
    assert pride.legal_copy is not None
    copy_path = output / pride.work_id / pride.legal_copy.filename
    assert copy_path.read_bytes().startswith(b"%PDF")
    assert (output / "index.json").is_file()
    dossier = (output / influence.work_id / "dossier.md").read_text(encoding="utf-8")
    assert (
        "borrow" in dossier or "préstamo" in dossier or "no hay copia local" in dossier.casefold()
    )


def test_library_export_updates_markdown_without_copying_pdfs(settings: Settings) -> None:
    output = settings.library_path
    destination = settings.library_path.parent / "exported-cards"
    destination.mkdir()
    policy = _policy()
    with SafeHttpClient(
        policy,
        transport=httpx.MockTransport(_library_handler),
        resolver=_resolver,
    ) as http:
        run_library_loop(
            source=FIXTURE_LIBRARY,
            output_root=output,
            http=http,
            jurisdiction="MX",
            languages=("en",),
            max_rounds=2,
            jurisdiction_approved=True,
            clock=lambda: NOW,
        )
    with pytest.raises(ValueError, match="authorize-export"):
        export_library_markdown(output, destination, authorize_export=False)
    written = export_library_markdown(output, destination, authorize_export=True)
    assert written
    exported = (destination / "classics" / "Pride_and_Prejudice.md").read_text(encoding="utf-8")
    assert "## Investigación del curador" in exported
    assert "Pride and Prejudice" in exported
    assert not list(destination.rglob("*.pdf"))


def test_cli_library_inventory_lists_fixture_cards() -> None:
    output = StringIO()
    code = cli(["library", "inventory", "--source", str(FIXTURE_LIBRARY)], output=output)
    assert code == 0
    text = output.getvalue()
    assert "cards=2" in text
    assert "Pride and Prejudice" in text
    assert "Libros.md" not in text


def test_cli_library_research_requires_network_authorization(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, tmp_path: Path
) -> None:
    configured = settings.model_copy(
        update={
            "network_enabled": True,
            "runtime_network": True,
            "allow_real_connectors": True,
            "allowed_domains": "openlibrary.org,gutendex.com",
            "max_urls_per_run": 8,
            "research_jurisdiction": "MX",
        }
    )
    monkeypatch.setattr("sales_curator.cli._settings", lambda: configured)
    seen: dict[str, object] = {}

    class FakeHttpClient:
        def __init__(self, policy) -> None:
            seen["policy"] = policy

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def fake_loop(**kwargs):
        seen["loop"] = kwargs
        from sales_curator.contracts.research import LibraryLoopReport

        return LibraryLoopReport.create(
            jurisdiction="MX",
            languages=["en"],
            inventory_count=0,
            works=[],
            warnings=[],
            created_at=NOW,
        )

    monkeypatch.setattr("sales_curator.cli.SafeHttpClient", FakeHttpClient)
    monkeypatch.setattr("sales_curator.cli.run_library_loop", fake_loop)
    output = StringIO()
    code = cli(
        [
            "library",
            "research",
            "--source",
            str(FIXTURE_LIBRARY),
            "--output",
            str(tmp_path / "library"),
            "--url-budget",
            "8",
            "--authorize-network",
        ],
        output=output,
    )
    assert code == 0
    assert seen["policy"].run_authorized is True
    assert seen["loop"]["jurisdiction"] == "MX"
    assert "loop_id=" in output.getvalue()

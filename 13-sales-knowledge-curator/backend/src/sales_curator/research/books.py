"""Investigación bibliográfica multifuente, con fallos parciales visibles."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from sales_curator.config import resolve_lab_output_root
from sales_curator.connectors.book_catalogs import parse_google_books, parse_open_library
from sales_curator.connectors.network import NetworkDisabled, NetworkPolicyError, SafeHttpClient
from sales_curator.contracts.research import BookAccessOffer, BookResearchReport


class BookResearcher:
    def __init__(
        self,
        http: SafeHttpClient,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.http = http
        self.clock = clock or (lambda: datetime.now(UTC))

    def research(
        self,
        *,
        title: str,
        author: str | None,
        isbn: str | None,
        jurisdiction: str,
        languages: tuple[str, ...],
        providers: tuple[str, ...] = ("open_library", "google_books"),
        max_results: int = 10,
    ) -> BookResearchReport:
        if not title.strip():
            raise ValueError("title es obligatorio")
        if not jurisdiction.strip():
            raise ValueError("jurisdiction es obligatoria")
        if not languages or any(item not in {"en", "es"} for item in languages):
            raise ValueError("languages solo admite en/es")
        if not 1 <= max_results <= 40:
            raise ValueError("max_results debe estar entre 1 y 40")
        allowed_providers = {"open_library", "google_books"}
        unknown = set(providers) - allowed_providers
        if unknown:
            raise ValueError(f"proveedores no soportados: {', '.join(sorted(unknown))}")
        now = self.clock()
        offers: list[BookAccessOffer] = []
        warnings: list[str] = []
        for provider in providers:
            try:
                if provider == "open_library":
                    payload = self.http.get_json(
                        _open_library_url(title, author, isbn, max_results)
                    )
                    offers.extend(
                        parse_open_library(
                            payload,
                            retrieved_at=now,
                            jurisdiction=jurisdiction,
                        )
                    )
                elif provider == "google_books":
                    payload = self.http.get_json(
                        _google_books_url(title, author, isbn, max_results)
                    )
                    offers.extend(
                        parse_google_books(
                            payload,
                            retrieved_at=now,
                            jurisdiction=jurisdiction,
                        )
                    )
            except (NetworkDisabled, NetworkPolicyError) as exc:
                warnings.append(f"{provider}: rama fallida: {exc}")
        filtered = [
            offer for offer in offers if offer.language is None or offer.language in languages
        ]
        unique: dict[tuple[str, str], BookAccessOffer] = {}
        for offer in filtered:
            unique[(offer.provider, offer.provider_record_id)] = offer
        ordered = sorted(unique.values(), key=lambda item: (item.provider, item.title.casefold()))
        query = title.strip()
        if author and author.strip():
            query += f" — {author.strip()}"
        if isbn and isbn.strip():
            query += f" — ISBN {isbn.strip()}"
        if not ordered:
            warnings.append("ningún catálogo devolvió una coincidencia utilizable")
        return BookResearchReport.create(
            query=query,
            jurisdiction=jurisdiction.strip(),
            languages=list(languages),
            offers=ordered,
            warnings=warnings,
            created_at=now,
        )


def _open_library_url(
    title: str,
    author: str | None,
    isbn: str | None,
    limit: int,
) -> str:
    params = {
        "title": title.strip(),
        "limit": str(limit),
        "fields": (
            "key,title,author_name,isbn,language,first_publish_year,ebook_access,"
            "lending_edition_s,ia,public_scan_b"
        ),
    }
    if author and author.strip():
        params["author"] = author.strip()
    if isbn and isbn.strip():
        params["isbn"] = isbn.strip()
    return f"https://openlibrary.org/search.json?{urlencode(params)}"


def _google_books_url(
    title: str,
    author: str | None,
    isbn: str | None,
    limit: int,
) -> str:
    query = [f'intitle:"{title.strip()}"']
    if author and author.strip():
        query.append(f'inauthor:"{author.strip()}"')
    if isbn and isbn.strip():
        query.append(f"isbn:{isbn.strip()}")
    params = {
        "q": " ".join(query),
        "maxResults": str(limit),
        "printType": "books",
        "projection": "full",
    }
    return f"https://www.googleapis.com/books/v1/volumes?{urlencode(params)}"


def write_book_research_report(report: BookResearchReport, output_root: Path) -> Path:
    output_root = resolve_lab_output_root(output_root)
    folder = output_root / report.research_id
    path = folder / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("report.json.tmp")
    temporary.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)
    return path

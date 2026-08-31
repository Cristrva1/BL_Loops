from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from sales_curator.connectors.network import NetworkDisabled, NetworkPolicy, NetworkPolicyError
from sales_curator.connectors.web_crawler import (
    CrawlOutput,
    RobotsDenied,
    WebCaptureError,
    _browser_runner,
    _BrowserRequestGuard,
    capture_web_page,
)
from sales_curator.contracts.research import DocumentRights, RightsStatus


def _resolver(_host: str) -> tuple[str, ...]:
    return ("142.250.72.14",)


def _policy(*, url_budget: int = 3, max_bytes: int = 20_000) -> NetworkPolicy:
    return NetworkPolicy(
        network_enabled=True,
        runtime_network=True,
        real_connectors_enabled=True,
        allowed_domains=("openlibrary.org",),
        max_bytes=max_bytes,
        max_url_budget=url_budget,
        user_agent="BL-Loops-SalesCurator/0.2",
    ).authorize(run_authorized=True, url_budget=url_budget)


def _rights() -> DocumentRights:
    return DocumentRights(
        rights_status=RightsStatus.OPEN_LICENSE,
        license="CC0 metadata",
        usage_basis="Metadatos abiertos del catálogo",
        jurisdiction="MX",
        retention_allowed=True,
        extraction_allowed=True,
        quotation_allowed=True,
        redistribution_allowed=True,
        notebooklm_upload_allowed=True,
        evidence="Declaración de derechos revisada por operador",
    )


def test_browser_capture_checks_robots_and_persists_only_markdown(tmp_path: Path) -> None:
    seen: list[str] = []

    def runner(url: str, _policy: NetworkPolicy) -> CrawlOutput:
        seen.append(url)
        return CrawlOutput(
            final_url=url,
            title="Open Library record",
            markdown="# Record\n\nBibliographic metadata.",
            status_code=200,
        )

    record = capture_web_page(
        "https://openlibrary.org/works/OL1W",
        policy=_policy(),
        output_root=tmp_path,
        rights=_rights(),
        language="en",
        robots_fetcher=lambda _url: "User-agent: *\nAllow: /",
        runner=runner,
        resolver=_resolver,
        clock=lambda: datetime(2026, 8, 30, tzinfo=UTC),
        extractor_version="0.9.2-test",
    )
    assert seen == ["https://openlibrary.org/works/OL1W"]
    assert record.language == "en"
    assert any("JavaScript deshabilitado" in warning for warning in record.warnings)
    markdown = (tmp_path / record.markdown_path).read_text("utf-8")
    assert "Bibliographic metadata" in markdown
    assert "language: en" in markdown
    manifest = json.loads((tmp_path / record.manifest_path).read_text("utf-8"))
    assert manifest["robots_allowed"] is True
    assert "raw_html" not in manifest


def test_robots_disallow_stops_before_browser(tmp_path: Path) -> None:
    called = False

    def runner(_url: str, _policy: NetworkPolicy) -> CrawlOutput:
        nonlocal called
        called = True
        raise AssertionError("browser must not run")

    with pytest.raises(RobotsDenied):
        capture_web_page(
            "https://openlibrary.org/private",
            policy=_policy(),
            output_root=tmp_path,
            rights=_rights(),
            language="es",
            robots_fetcher=lambda _url: "User-agent: *\nDisallow: /private",
            runner=runner,
            resolver=_resolver,
        )
    assert called is False


def test_browser_redirect_outside_allowlist_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(NetworkPolicyError, match="allowlist"):
        capture_web_page(
            "https://openlibrary.org/works/OL1W",
            policy=_policy(),
            output_root=tmp_path,
            rights=_rights(),
            language="es",
            robots_fetcher=lambda _url: "User-agent: *\nAllow: /",
            runner=lambda _url, _policy: CrawlOutput(
                final_url="https://evil.example/copied",
                title="redirect",
                markdown="not allowed",
                status_code=200,
            ),
            resolver=_resolver,
        )


def test_capture_uses_safe_default_resolver_when_not_injected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resolved: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        resolved.append(host)
        return ("142.250.72.14",)

    monkeypatch.setattr("sales_curator.connectors.web_crawler.system_resolver", resolver)
    record = capture_web_page(
        "https://openlibrary.org/works/OL1W",
        policy=_policy(),
        output_root=tmp_path,
        rights=_rights(),
        language="es",
        robots_fetcher=lambda _url: "User-agent: *\nAllow: /",
        runner=lambda url, _policy: CrawlOutput(
            final_url=url,
            title="Registro",
            markdown="Contenido bibliográfico.",
            status_code=200,
        ),
        extractor_version="0.9.2-test",
    )
    assert record.language == "es"
    assert resolved == ["openlibrary.org", "openlibrary.org", "openlibrary.org"]


def test_capture_budget_counts_robots_before_browser(tmp_path: Path) -> None:
    called = False

    def runner(_url: str, _policy: NetworkPolicy) -> CrawlOutput:
        nonlocal called
        called = True
        raise AssertionError("browser must not run without a remaining URL")

    with pytest.raises(NetworkDisabled, match="presupuesto"):
        capture_web_page(
            "https://openlibrary.org/works/OL1W",
            policy=_policy(url_budget=1),
            output_root=tmp_path,
            rights=_rights(),
            language="es",
            robots_fetcher=lambda _url: "User-agent: *\nAllow: /",
            runner=runner,
            resolver=_resolver,
            extractor_version="0.9.2-test",
        )
    assert called is False


def test_capture_rejects_unsupported_language_before_side_effects(tmp_path: Path) -> None:
    called = False

    def robots_fetcher(_url: str) -> str:
        nonlocal called
        called = True
        return "User-agent: *\nAllow: /"

    with pytest.raises(ValueError, match="idioma"):
        capture_web_page(
            "https://openlibrary.org/works/OL1W",
            policy=_policy(),
            output_root=tmp_path,
            rights=_rights(),
            language="fr",  # type: ignore[arg-type]
            robots_fetcher=robots_fetcher,
            runner=lambda _url, _policy: pytest.fail("browser must not run"),
            resolver=_resolver,
            extractor_version="0.9.2-test",
        )
    assert called is False


class _FakeRoute:
    def __init__(
        self,
        url: str,
        *,
        method: str = "GET",
        resource_type: str = "document",
        child_frame: bool = False,
    ) -> None:
        self.request = SimpleNamespace(
            url=url,
            method=method,
            resource_type=resource_type,
            frame=SimpleNamespace(parent_frame=object() if child_frame else None),
        )
        self.aborted = False
        self.continued = False

    async def abort(self) -> None:
        self.aborted = True

    async def continue_(self) -> None:
        self.continued = True


def test_browser_guard_blocks_state_changing_method_on_allowed_domain() -> None:
    url = "https://openlibrary.org/works/OL1W"
    guard = _BrowserRequestGuard(policy=_policy(url_budget=2), resolver=_resolver)
    route = _FakeRoute(url, method="POST")

    asyncio.run(guard.handle(route))

    assert route.aborted is True
    assert route.continued is False
    with pytest.raises(WebCaptureError, match="POST"):
        guard.raise_if_failed()


def test_browser_guard_counts_redirect_subresource_and_fetch_fail_closed() -> None:
    initial_url = "https://openlibrary.org/works/OL1W"
    guard = _BrowserRequestGuard(policy=_policy(url_budget=3), resolver=_resolver)
    routes = [
        _FakeRoute(initial_url),
        _FakeRoute("https://openlibrary.org/works/OL1W?redirected=1"),
        _FakeRoute("https://openlibrary.org/static/site.css"),
        _FakeRoute("https://openlibrary.org/api/related.json"),
    ]

    for route in routes:
        asyncio.run(guard.handle(route))

    assert [route.continued for route in routes] == [True, True, True, False]
    assert [route.aborted for route in routes] == [False, False, False, True]
    with pytest.raises(NetworkDisabled, match="presupuesto"):
        guard.raise_if_failed()


def test_browser_guard_does_not_charge_non_network_browser_urls() -> None:
    guard = _BrowserRequestGuard(policy=_policy(url_budget=1), resolver=_resolver)
    internal_routes = [
        _FakeRoute("about:blank"),
        _FakeRoute("data:text/plain,hello"),
        _FakeRoute("blob:https://openlibrary.org/content-id"),
    ]

    for route in internal_routes:
        asyncio.run(guard.handle(route))

    assert all(route.continued for route in internal_routes)
    assert guard.policy.url_budget == 1
    guard.raise_if_failed()


def test_browser_guard_uses_injected_resolver_for_every_network_request() -> None:
    resolved: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        resolved.append(host)
        return ("142.250.72.14",)

    guard = _BrowserRequestGuard(policy=_policy(url_budget=2), resolver=resolver)
    routes = [
        _FakeRoute("https://openlibrary.org/works/OL1W"),
        _FakeRoute("https://openlibrary.org/static/site.css"),
    ]

    for route in routes:
        asyncio.run(guard.handle(route))

    assert resolved == ["openlibrary.org", "openlibrary.org"]
    assert guard.policy.url_budget == 0


@pytest.mark.parametrize(
    "resource_type",
    [
        "stylesheet",
        "image",
        "media",
        "font",
        "script",
        "xhr",
        "fetch",
        "eventsource",
        "websocket",
        "manifest",
        "other",
    ],
)
def test_browser_guard_blocks_secondary_resource_without_network(
    resource_type: str,
) -> None:
    resolved: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        resolved.append(host)
        return ("142.250.72.14",)

    guard = _BrowserRequestGuard(policy=_policy(url_budget=1), resolver=resolver)
    route = _FakeRoute(
        "https://openlibrary.org/static/resource",
        resource_type=resource_type,
    )

    asyncio.run(guard.handle(route))

    assert route.aborted is True
    assert route.continued is False
    assert resolved == []
    assert guard.policy.url_budget == 1


def test_browser_guard_blocks_child_frame_document_without_network() -> None:
    resolved: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        resolved.append(host)
        return ("142.250.72.14",)

    guard = _BrowserRequestGuard(policy=_policy(url_budget=1), resolver=resolver)
    route = _FakeRoute(
        "https://openlibrary.org/embedded",
        resource_type="document",
        child_frame=True,
    )

    asyncio.run(guard.handle(route))

    assert route.aborted is True
    assert route.continued is False
    assert resolved == []
    assert guard.policy.url_budget == 1


def test_browser_runner_fails_when_budget_overflows_even_if_crawl_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_browser_config: dict[str, object] = {}

    class FakeCacheMode:
        DISABLED = "disabled"

    class FakeStrategy:
        hook = None

        def set_hook(self, _name: str, hook) -> None:
            self.hook = hook

    class FakeContext:
        handler = None

        async def route(self, _pattern: str, handler) -> None:
            self.handler = handler

    class FakeCrawler:
        def __init__(self, **_kwargs) -> None:
            self.crawler_strategy = FakeStrategy()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args) -> None:
            return None

        async def arun(self, *, url: str, config):
            del config
            context = FakeContext()
            await self.crawler_strategy.hook(object(), context)
            for request_url in (
                url,
                "https://openlibrary.org/static/site.css",
                "https://openlibrary.org/api/related.json",
            ):
                await context.handler(_FakeRoute(request_url))
            return SimpleNamespace(success=True)

    def fake_browser_config(**kwargs):
        seen_browser_config.update(kwargs)
        return kwargs

    monkeypatch.setattr("crawl4ai.AsyncWebCrawler", FakeCrawler)
    monkeypatch.setattr("crawl4ai.BrowserConfig", fake_browser_config)
    monkeypatch.setattr("crawl4ai.CrawlerRunConfig", lambda **kwargs: kwargs)
    monkeypatch.setattr("crawl4ai.CacheMode", FakeCacheMode)

    with pytest.raises(NetworkDisabled, match="presupuesto"):
        _browser_runner(
            "https://openlibrary.org/works/OL1W",
            _policy(url_budget=2),
            resolver=_resolver,
        )
    assert seen_browser_config["java_script_enabled"] is False
    assert seen_browser_config["use_persistent_context"] is False
    assert seen_browser_config["storage_state"] is None
    assert seen_browser_config["accept_downloads"] is False

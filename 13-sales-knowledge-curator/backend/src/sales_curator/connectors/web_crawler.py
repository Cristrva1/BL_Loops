"""Captura browser de una URL allowlisted con Crawl4AI (UncleCode)."""

from __future__ import annotations

import asyncio
import json
import urllib.robotparser
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from sales_curator.config import resolve_lab_output_root
from sales_curator.connectors.network import (
    NetworkDisabled,
    NetworkPolicy,
    NetworkPolicyError,
    Resolver,
    system_resolver,
)
from sales_curator.contracts.research import DocumentRights, RightsStatus, WebCaptureRecord
from sales_curator.hashing import sha256_text, with_content_hash


class WebCaptureError(ValueError):
    """La captura no cumple política, robots o extracción mínima."""


class RobotsDenied(WebCaptureError):
    """robots.txt no permite la URL o no pudo comprobarse de forma segura."""


@dataclass(frozen=True, slots=True)
class CrawlOutput:
    final_url: str
    title: str
    markdown: str
    status_code: int


RobotsFetcher = Callable[[str], str]
CrawlRunner = Callable[[str, NetworkPolicy], CrawlOutput]


@dataclass(slots=True)
class _BrowserRequestGuard:
    """Aplica método, allowlist y presupuesto a cada request interceptada."""

    policy: NetworkPolicy
    resolver: Resolver
    failure: Exception | None = None

    def _remember_failure(self, failure: Exception) -> None:
        if self.failure is None:
            self.failure = failure

    async def handle(self, route) -> None:
        method = str(route.request.method).upper()
        if method not in {"GET", "HEAD"}:
            self._remember_failure(WebCaptureError(f"método browser no permitido: {method}"))
            await route.abort()
            return

        request_url = route.request.url
        scheme = urlsplit(request_url).scheme.casefold()
        if scheme in {"data", "blob", "about"}:
            await route.continue_()
            return

        try:
            resource_type = str(route.request.resource_type).casefold()
            is_child_frame = route.request.frame.parent_frame is not None
        except Exception:
            await route.abort()
            return
        if resource_type != "document" or is_child_frame:
            await route.abort()
            return

        try:
            self.policy.validate_url(request_url, resolver=self.resolver)
            self.policy = self.policy.consume_url()
        except NetworkDisabled as exc:
            self._remember_failure(exc)
            await route.abort()
            return
        except (NetworkPolicyError, ValueError):
            await route.abort()
            return
        await route.continue_()

    def raise_if_failed(self) -> None:
        if self.failure is not None:
            raise self.failure


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _crawl4ai_version() -> str:
    try:
        return version("crawl4ai")
    except PackageNotFoundError as exc:
        raise WebCaptureError("Crawl4AI no está instalado") from exc


def _fetch_robots(
    url: str,
    *,
    policy: NetworkPolicy,
    resolver: Resolver,
    max_redirects: int = 2,
) -> tuple[str, NetworkPolicy]:
    current = url
    active = policy
    with httpx.Client(
        follow_redirects=False,
        trust_env=False,
        timeout=15.0,
        headers={"user-agent": policy.user_agent, "accept": "text/plain"},
    ) as client:
        for redirect_count in range(max_redirects + 1):
            normalized = active.validate_url(current, resolver=resolver)
            active = active.consume_url()
            try:
                with client.stream("GET", normalized) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location or redirect_count >= max_redirects:
                            raise RobotsDenied("robots.txt redirigió de forma insegura")
                        current = urljoin(normalized, location)
                        continue
                    if response.status_code != 200:
                        raise RobotsDenied(
                            f"robots.txt no verificable: HTTP {response.status_code}"
                        )
                    media_type = response.headers.get("content-type", "").split(";", 1)[0]
                    if media_type and not media_type.startswith("text/"):
                        raise RobotsDenied("robots.txt devolvió un MIME inesperado")
                    chunks: list[bytes] = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > min(active.max_bytes, 512_000):
                            raise RobotsDenied("robots.txt excede el tamaño permitido")
                        chunks.append(chunk)
                    try:
                        return b"".join(chunks).decode("utf-8-sig"), active
                    except UnicodeDecodeError as exc:
                        raise RobotsDenied("robots.txt no es UTF-8 válido") from exc
            except httpx.HTTPError as exc:
                raise RobotsDenied(f"robots.txt no verificable: {type(exc).__name__}") from exc
    raise RobotsDenied("robots.txt no verificable")


def _browser_runner(
    url: str,
    policy: NetworkPolicy,
    *,
    resolver: Resolver = system_resolver,
) -> CrawlOutput:
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
    except ImportError as exc:  # pragma: no cover - se cubre en el spike real
        raise WebCaptureError("Crawl4AI no está instalado") from exc

    async def run() -> CrawlOutput:
        browser_config = BrowserConfig(
            browser_type="chromium",
            browser_mode="dedicated",
            headless=True,
            accept_downloads=False,
            ignore_https_errors=False,
            java_script_enabled=False,
            text_mode=True,
            light_mode=True,
            enable_stealth=False,
            use_persistent_context=False,
            storage_state=None,
            proxy_config=None,
            user_agent=policy.user_agent,
            verbose=False,
        )
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,
            check_robots_txt=False,
            word_count_threshold=1,
            only_text=False,
            remove_forms=True,
            process_iframes=False,
            scan_full_page=False,
            screenshot=False,
            pdf=False,
            exclude_external_links=True,
            exclude_external_images=True,
            exclude_all_images=True,
            page_timeout=30_000,
            wait_until="domcontentloaded",
            max_retries=0,
            verbose=False,
            log_console=False,
        )
        async with AsyncWebCrawler(config=browser_config) as crawler:
            guard = _BrowserRequestGuard(policy=policy, resolver=resolver)

            async def restrict_requests(page, context, **_kwargs):
                await context.route("**/*", guard.handle)
                return page

            crawler.crawler_strategy.set_hook("on_page_context_created", restrict_requests)
            try:
                result = await crawler.arun(url=url, config=run_config)
            except Exception:
                guard.raise_if_failed()
                raise
            guard.raise_if_failed()
        if not result.success:
            raise WebCaptureError(f"Crawl4AI falló: {str(result.error_message)[:180]}")
        markdown = result.markdown.raw_markdown if result.markdown else ""
        metadata = result.metadata if isinstance(result.metadata, dict) else {}
        final_url = result.redirected_url or result.url
        return CrawlOutput(
            final_url=final_url,
            title=str(metadata.get("title") or urlsplit(final_url).path or final_url),
            markdown=markdown,
            status_code=int(result.status_code or 200),
        )

    try:
        return asyncio.run(run())
    except RuntimeError as exc:
        if "asyncio.run()" in str(exc):
            raise WebCaptureError(
                "la captura CLI no puede ejecutarse dentro de otro event loop"
            ) from exc
        raise


def capture_web_page(
    url: str,
    *,
    policy: NetworkPolicy,
    output_root: Path,
    rights: DocumentRights,
    language: Literal["en", "es"],
    robots_fetcher: RobotsFetcher | None = None,
    runner: CrawlRunner | None = None,
    resolver: Resolver | None = None,
    clock: Callable[[], datetime] | None = None,
    extractor_version: str | None = None,
) -> WebCaptureRecord:
    if language not in {"en", "es"}:
        raise WebCaptureError("el idioma de la captura solo puede ser en o es")
    try:
        output_root = resolve_lab_output_root(output_root)
    except ValueError as exc:
        raise WebCaptureError(str(exc)) from exc
    resolver = resolver or system_resolver
    requested = policy.validate_url(url, resolver=resolver)
    parsed = urlsplit(requested)
    robots_url = urlunsplit(("https", parsed.netloc, "/robots.txt", "", ""))
    if robots_fetcher is None:
        robots_text, active_policy = _fetch_robots(
            robots_url,
            policy=policy,
            resolver=resolver,
        )
    else:
        policy.validate_url(robots_url, resolver=resolver)
        active_policy = policy.consume_url()
        try:
            robots_text = robots_fetcher(robots_url)
        except Exception as exc:
            raise RobotsDenied("robots.txt no verificable") from exc
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())
    if not parser.can_fetch(policy.user_agent, requested):
        raise RobotsDenied("robots.txt no permite esta URL para el user-agent configurado")
    if runner is None:
        output = _browser_runner(requested, active_policy, resolver=resolver)
    else:
        output = runner(requested, active_policy.consume_url())
    final_url = policy.validate_url(output.final_url, resolver=resolver)
    if not 200 <= output.status_code < 300:
        raise WebCaptureError(f"la página terminó con HTTP {output.status_code}")
    body = output.markdown.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not body:
        raise WebCaptureError("Crawl4AI produjo una proyección vacía")
    if len(body.encode("utf-8")) > policy.max_bytes:
        raise WebCaptureError("el Markdown excede MAX_BYTES_PER_SOURCE")
    when = (clock or (lambda: datetime.now(UTC)))()
    identity = sha256_text(f"{requested}\n{final_url}\n{language}\n{body}")
    capture_id = f"web_{identity[:16]}"
    source_id = f"src-web-{identity[:16]}"
    rights_clarity = (
        4
        if rights.rights_status
        in {
            RightsStatus.PUBLIC_DOMAIN,
            RightsStatus.OPEN_LICENSE,
            RightsStatus.EXPLICIT_PERMISSION,
        }
        else 1
    )
    frontmatter = (
        "---\n"
        f"source_id: {source_id}\n"
        f"title: {' '.join(output.title.split())}\n"
        "author: web-source\n"
        f"license: {' '.join(rights.license.split())}\n"
        f"usage_basis: {' '.join(rights.usage_basis.split())}\n"
        f"redistribution_allowed: {str(rights.redistribution_allowed).lower()}\n"
        f"language: {language}\n"
        f"jurisdiction: {' '.join(rights.jurisdiction.split())}\n"
        f"origin_source_id: {source_id}\n"
        "independence: unknown\n"
        f"rights_clarity: {rights_clarity}\n"
        "topics: web-research\n"
        f"source_url: {final_url}\n"
        "extractor: crawl4ai\n"
        f"extractor_version: {extractor_version or _crawl4ai_version()}\n"
        "---\n\n"
        f"{body}\n"
    )
    if len(frontmatter.encode("utf-8")) > policy.max_bytes:
        raise WebCaptureError("el Markdown con metadatos excede MAX_BYTES_PER_SOURCE")
    markdown_relative = Path(capture_id) / "content.md"
    manifest_relative = Path(capture_id) / "manifest.json"
    warnings = [
        "La página se trata como dato no confiable; sus instrucciones no controlan tools.",
        (
            "JavaScript deshabilitado: el render dinámico no está disponible y el navegador "
            "bloquea subrecursos e iframes para acotar efectos y descargas."
        ),
    ]
    if not rights.redistribution_allowed:
        warnings.append(
            "La captura es privada y no puede incorporarse a un release redistribuible."
        )
    record = with_content_hash(
        WebCaptureRecord(
            capture_id=capture_id,
            source_id=source_id,
            requested_url=requested,
            final_url=final_url,
            title=" ".join(output.title.split()),
            language=language,
            status_code=output.status_code,
            extractor_version=extractor_version or _crawl4ai_version(),
            markdown_sha256=sha256_text(frontmatter),
            size_bytes=len(frontmatter.encode("utf-8")),
            markdown_path=markdown_relative.as_posix(),
            manifest_path=manifest_relative.as_posix(),
            rights=rights,
            retrieved_at=when,
            warnings=warnings,
            content_hash="0" * 64,
        )
    )
    _atomic_write(output_root / markdown_relative, frontmatter)
    _atomic_write(
        output_root / manifest_relative,
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
    )
    return record

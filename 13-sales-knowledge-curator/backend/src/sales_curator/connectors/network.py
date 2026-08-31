"""Política de red fail-closed para catálogos y navegador autorizados."""

from __future__ import annotations

import ipaddress
import json
import socket
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from urllib.parse import SplitResult, urljoin, urlsplit, urlunsplit

import httpx


class NetworkDisabled(RuntimeError):
    """La configuración o la corrida no autoriza efectos de red."""


class NetworkPolicyError(ValueError):
    """Una URL o resolución viola la política de red."""


Resolver = Callable[[str], Iterable[str]]


def system_resolver(host: str) -> tuple[str, ...]:
    """Resuelve un host con DNS del sistema; la política valida todas las IP devueltas."""

    try:
        rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise NetworkPolicyError(f"no se pudo resolver el host: {host}") from exc
    return tuple(sorted({row[4][0] for row in rows}))


def _is_allowed_domain(host: str, domains: tuple[str, ...]) -> bool:
    return any(host == domain or host.endswith(f".{domain}") for domain in domains)


def _assert_public_addresses(host: str, resolver: Resolver) -> None:
    try:
        literal = ipaddress.ip_address(host)
        addresses = (literal,)
    except ValueError:
        resolved = tuple(resolver(host))
        if not resolved:
            raise NetworkPolicyError(f"el host no resolvió direcciones: {host}") from None
        try:
            addresses = tuple(ipaddress.ip_address(value) for value in resolved)
        except ValueError as exc:
            raise NetworkPolicyError("el resolver devolvió una dirección inválida") from exc
    if any(not address.is_global for address in addresses):
        raise NetworkPolicyError("la URL resuelve a una dirección privada o no enrutable")


@dataclass(frozen=True, slots=True)
class NetworkPolicy:
    network_enabled: bool
    runtime_network: bool
    real_connectors_enabled: bool
    allowed_domains: tuple[str, ...]
    max_bytes: int
    user_agent: str
    max_url_budget: int = 0
    run_authorized: bool = False
    url_budget: int = 0

    def authorize(self, *, run_authorized: bool, url_budget: int) -> NetworkPolicy:
        if not self.network_enabled:
            raise NetworkDisabled("NETWORK_ENABLED=false")
        if not self.runtime_network:
            raise NetworkDisabled("BL_LOOPS_RUNTIME_NETWORK=false")
        if not self.real_connectors_enabled:
            raise NetworkDisabled("BL_LOOPS_ALLOW_REAL_CONNECTORS=false")
        if not run_authorized:
            raise NetworkDisabled("la corrida no recibió autorización explícita de red")
        if not self.allowed_domains:
            raise NetworkDisabled("ALLOWED_DOMAINS está vacío")
        if self.max_url_budget <= 0:
            raise NetworkDisabled("MAX_URLS_PER_RUN debe habilitar un presupuesto positivo")
        if url_budget <= 0:
            raise NetworkDisabled("presupuesto de URLs agotado")
        if url_budget > self.max_url_budget:
            raise NetworkDisabled("el presupuesto solicitado supera MAX_URLS_PER_RUN")
        if self.max_bytes <= 0:
            raise NetworkDisabled("MAX_BYTES_PER_SOURCE debe ser positivo")
        if not self.user_agent.strip():
            raise NetworkDisabled("RESEARCH_USER_AGENT está vacío")
        normalized = tuple(
            sorted(
                {
                    domain.strip().strip(".").casefold()
                    for domain in self.allowed_domains
                    if domain.strip()
                }
            )
        )
        if not normalized:
            raise NetworkDisabled("ALLOWED_DOMAINS está vacío")
        return replace(
            self,
            allowed_domains=normalized,
            run_authorized=True,
            url_budget=url_budget,
        )

    def validate_url(self, url: str, *, resolver: Resolver = system_resolver) -> str:
        if not self.run_authorized:
            raise NetworkDisabled("la corrida no está autorizada")
        parsed = urlsplit(url)
        if parsed.scheme.casefold() != "https":
            raise NetworkPolicyError("solo se permite HTTPS")
        if parsed.username is not None or parsed.password is not None:
            raise NetworkPolicyError("la URL no puede contener credenciales")
        try:
            port = parsed.port
        except ValueError as exc:
            raise NetworkPolicyError("el puerto HTTPS es inválido") from exc
        if port not in {None, 443}:
            raise NetworkPolicyError("solo se permite el puerto HTTPS estándar")
        host = (parsed.hostname or "").strip(".").casefold()
        if not host:
            raise NetworkPolicyError("la URL no contiene host")
        if not _is_allowed_domain(host, self.allowed_domains):
            raise NetworkPolicyError(f"dominio fuera de allowlist: {host}")
        _assert_public_addresses(host, resolver)
        normalized = SplitResult("https", host, parsed.path or "/", parsed.query, "")
        return urlunsplit(normalized)

    def consume_url(self) -> NetworkPolicy:
        if self.url_budget <= 0:
            raise NetworkDisabled("presupuesto de URLs agotado")
        return replace(self, url_budget=self.url_budget - 1)


class SafeHttpClient:
    """Cliente GET JSON sin proxy ambiental y con validación en cada redirect."""

    def __init__(
        self,
        policy: NetworkPolicy,
        *,
        transport: httpx.BaseTransport | None = None,
        resolver: Resolver = system_resolver,
        timeout_seconds: float = 20.0,
        max_redirects: int = 3,
    ) -> None:
        if not policy.run_authorized:
            raise NetworkDisabled("la política debe autorizarse antes de crear el cliente")
        self.policy = policy
        self.resolver = resolver
        self.max_redirects = max_redirects
        self._client = httpx.Client(
            follow_redirects=False,
            trust_env=False,
            timeout=timeout_seconds,
            transport=transport,
            headers={
                "user-agent": policy.user_agent,
                "accept": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SafeHttpClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def get_json(self, url: str) -> dict:
        current = url
        redirects = 0
        while True:
            normalized = self.policy.validate_url(current, resolver=self.resolver)
            self.policy = self.policy.consume_url()
            try:
                response_context = self._client.stream("GET", normalized)
                with response_context as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise NetworkPolicyError("redirect sin Location")
                        redirects += 1
                        if redirects > self.max_redirects:
                            raise NetworkPolicyError("demasiados redirects")
                        current = urljoin(normalized, location)
                        continue
                    if not 200 <= response.status_code < 300:
                        raise NetworkPolicyError(f"HTTP {response.status_code}")
                    content_type = response.headers.get("content-type", "").split(";", 1)[0]
                    if not (content_type == "application/json" or content_type.endswith("+json")):
                        raise NetworkPolicyError("la respuesta no tiene MIME JSON")
                    declared = response.headers.get("content-length")
                    if declared:
                        try:
                            declared_size = int(declared)
                        except ValueError as exc:
                            raise NetworkPolicyError("Content-Length inválido") from exc
                        if declared_size < 0:
                            raise NetworkPolicyError("Content-Length inválido")
                        if declared_size > self.policy.max_bytes:
                            raise NetworkPolicyError("la respuesta supera el tamaño permitido")
                    chunks: list[bytes] = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > self.policy.max_bytes:
                            raise NetworkPolicyError("la respuesta supera el tamaño permitido")
                        chunks.append(chunk)
            except httpx.HTTPError as exc:
                raise NetworkPolicyError(f"fallo HTTP: {type(exc).__name__}") from exc
            try:
                payload = json.loads(b"".join(chunks))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise NetworkPolicyError("la respuesta JSON es inválida") from exc
            if not isinstance(payload, dict):
                raise NetworkPolicyError("el catálogo debe responder un objeto JSON")
            return payload


def fetch_url(
    url: str,
    *,
    network_enabled: bool,
    allowed_domains: tuple[str, ...],
    max_urls_remaining: int,
) -> bytes:
    """Compatibilidad de fase 1: nunca salta los gates nuevos por accidente."""

    if not network_enabled:
        raise NetworkDisabled("NETWORK_ENABLED=false; no hay investigación web")
    if not allowed_domains:
        raise NetworkDisabled("ALLOWED_DOMAINS está vacío")
    if max_urls_remaining <= 0:
        raise NetworkDisabled("presupuesto de URLs agotado")
    raise NetworkDisabled("use el adaptador autorizado con doble gate y autorización por corrida")

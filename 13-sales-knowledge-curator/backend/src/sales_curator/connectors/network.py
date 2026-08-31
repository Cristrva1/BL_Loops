"""Adaptador web fail-closed. Este corte no navega."""

from __future__ import annotations


class NetworkDisabled(RuntimeError):
    """La red está desactivada o el adaptador web no forma parte de este corte."""


def fetch_url(
    url: str,
    *,
    network_enabled: bool,
    allowed_domains: tuple[str, ...],
    max_urls_remaining: int,
) -> bytes:
    if not network_enabled:
        raise NetworkDisabled("NETWORK_ENABLED=false; no hay investigación web")
    if not allowed_domains:
        raise NetworkDisabled("ALLOWED_DOMAINS está vacío")
    if max_urls_remaining <= 0:
        raise NetworkDisabled("presupuesto de URLs agotado")
    raise NetworkDisabled("el adaptador web no está instalado en la fase 1")

"""Punto de entrada adicional; la CLI `sales-curator demo` es la vía principal."""

from __future__ import annotations

from sales_curator.cli import cli
from sales_curator.config import lab_root


def main() -> None:
    fixture = lab_root() / "fixtures" / "corpus"
    raise SystemExit(cli(["demo", "--fixture", str(fixture)]))

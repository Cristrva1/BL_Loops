from __future__ import annotations

from io import StringIO

from sales_curator.cli import cli
from sales_curator.config import Settings
from sales_curator.orchestration.service import CuratorService


def test_cli_demo_and_validate(monkeypatch, settings: Settings, corpus) -> None:
    service = CuratorService(settings)

    def fake_service() -> CuratorService:
        return service

    monkeypatch.setattr("sales_curator.cli._service", fake_service)
    output = StringIO()
    code = cli(
        ["demo", "--fixture", str(corpus), "--reviewer", "operador-local", "--reason", "demo cli"],
        output=output,
    )
    assert code == 0
    text = output.getvalue()
    assert "release=" in text
    assert "state=published" in text

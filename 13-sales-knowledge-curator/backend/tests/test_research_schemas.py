from __future__ import annotations

import json
from pathlib import Path

from sales_curator import schema_export

RESEARCH_SCHEMAS = {
    "document-rights.schema.json",
    "book-access-offer.schema.json",
    "book-research-report.schema.json",
    "document-import-record.schema.json",
    "web-capture-record.schema.json",
    "notebook-source-set.schema.json",
    "notebook-packet.schema.json",
    "rag-packet.schema.json",
}


def test_schema_export_includes_all_public_research_contracts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(schema_export, "lab_root", lambda: tmp_path)
    schema_export.main()
    generated = tmp_path / "contracts" / "generated"
    assert {path.name for path in generated.glob("*.schema.json")} >= RESEARCH_SCHEMAS
    web_schema = json.loads((generated / "web-capture-record.schema.json").read_text("utf-8"))
    assert set(web_schema["properties"]["language"]["enum"]) == {"en", "es"}

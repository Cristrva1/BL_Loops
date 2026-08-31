"""Genera JSON Schema visible en contracts/generated/."""

from __future__ import annotations

import json

from sales_curator.config import lab_root
from sales_curator.contracts.models import (
    ClaimRecord,
    ConflictRecord,
    KnowledgeRelease,
    ReviewDecision,
    RunEvent,
    RunRecord,
    SourceRecord,
)
from sales_curator.contracts.research import (
    BookAccessOffer,
    BookResearchReport,
    DocumentImportRecord,
    DocumentRights,
    NotebookPacket,
    NotebookSourceSet,
    RagPacket,
    WebCaptureRecord,
)

SCHEMAS = {
    "source-record.schema.json": SourceRecord,
    "claim-record.schema.json": ClaimRecord,
    "conflict-record.schema.json": ConflictRecord,
    "review-decision.schema.json": ReviewDecision,
    "knowledge-release.schema.json": KnowledgeRelease,
    "run-event.schema.json": RunEvent,
    "run-record.schema.json": RunRecord,
    "document-rights.schema.json": DocumentRights,
    "book-access-offer.schema.json": BookAccessOffer,
    "book-research-report.schema.json": BookResearchReport,
    "document-import-record.schema.json": DocumentImportRecord,
    "web-capture-record.schema.json": WebCaptureRecord,
    "notebook-source-set.schema.json": NotebookSourceSet,
    "notebook-packet.schema.json": NotebookPacket,
    "rag-packet.schema.json": RagPacket,
}


def main() -> None:
    output_dir = lab_root() / "contracts" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, model in SCHEMAS.items():
        path = output_dir / filename
        path.write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Generado: {path.relative_to(lab_root()).as_posix()}")


if __name__ == "__main__":
    main()

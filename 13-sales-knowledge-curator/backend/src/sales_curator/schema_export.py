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

SCHEMAS = {
    "source-record.schema.json": SourceRecord,
    "claim-record.schema.json": ClaimRecord,
    "conflict-record.schema.json": ConflictRecord,
    "review-decision.schema.json": ReviewDecision,
    "knowledge-release.schema.json": KnowledgeRelease,
    "run-event.schema.json": RunEvent,
    "run-record.schema.json": RunRecord,
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

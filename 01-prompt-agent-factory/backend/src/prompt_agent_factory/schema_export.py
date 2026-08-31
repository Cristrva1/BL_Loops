"""Genera JSON Schema legible para estudiar los contratos sin abrir Python."""

from __future__ import annotations

import json

from .config import lab_root
from .contracts import AgentSpec, PromptSpec, RunRecord, SkillSpec

SCHEMAS = {
    "prompt-spec.schema.json": PromptSpec,
    "agent-spec.schema.json": AgentSpec,
    "skill-spec.schema.json": SkillSpec,
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

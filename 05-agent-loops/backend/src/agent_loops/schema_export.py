"""Genera JSON Schema visible de los contratos del loop."""

from __future__ import annotations

import json

from .config import lab_root
from .contracts import LoopDeclaration, PromptRewrite


def main() -> None:
    output_dir = lab_root() / "contracts" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    schemas = {
        "prompt-rewrite.schema.json": PromptRewrite,
        "loop-declaration.schema.json": LoopDeclaration,
    }
    for filename, model in schemas.items():
        path = output_dir / filename
        path.write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Generado: {path.relative_to(lab_root()).as_posix()}")


if __name__ == "__main__":
    main()

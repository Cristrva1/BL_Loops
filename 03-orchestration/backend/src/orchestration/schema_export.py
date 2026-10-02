"""Genera JSON Schema visible de los handoffs y del evento de corrida."""

from __future__ import annotations

import json

from .config import lab_root
from .contracts import Plan, Review


def main() -> None:
    output_dir = lab_root() / "contracts" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    schemas = {
        "plan.schema.json": Plan,
        "review.schema.json": Review,
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

"""Exportación JSONL de una corrida evaluada de Open Generative AI Studio.

Cada línea es independiente: el comparador central de BL_Loops solo importa este archivo.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from open_genai_studio.schemas import EvaluationRecord

LAB_ID = "24-open-generative-ai-studio"


def export_evaluation_jsonl(
    record: EvaluationRecord, output_path: str | Path = ".local/eval_results.jsonl"
) -> Path:
    """Añade el registro al final del JSONL y devuelve la ruta absoluta del archivo."""

    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "lab_id": LAB_ID,
        "case_id": record.case_id,
        "model": record.model,
        "success": record.success,
        "duration_actual": record.duration_actual,
        "duration_expected": record.duration_expected,
        "render_time_seconds": record.render_time_seconds,
        "file_size_kb": record.file_size_kb,
        "shots_count": record.shots_count,
        "metrics": record.metrics,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return target

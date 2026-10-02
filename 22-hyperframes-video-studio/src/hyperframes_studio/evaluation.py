"""Módulo de evaluación y exportación JSONL según contrato de BL_Loops."""

from datetime import datetime, timezone
import json
from pathlib import Path
from hyperframes_studio.schemas import EvaluationRecord


def export_evaluation_jsonl(record: EvaluationRecord, output_path: str | Path = ".local/eval_results.jsonl") -> Path:
    """Exporta el resultado de evaluación en formato JSONL para el comparador central."""
    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lab_id": "22-hyperframes-video-studio",
        "case_id": record.case_id,
        "model": record.model,
        "success": record.success,
        "duration_actual": record.duration_actual,
        "duration_expected": record.duration_expected,
        "render_time_seconds": record.render_time_seconds,
        "file_size_kb": record.file_size_kb,
        "scenes_count": record.scenes_count,
        "metrics": record.metrics,
    }

    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return target

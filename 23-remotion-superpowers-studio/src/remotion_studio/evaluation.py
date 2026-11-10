"""Evaluación y exportación JSONL para Remotion Superpowers."""

import json
from datetime import UTC, datetime
from pathlib import Path

from remotion_studio.schemas import EvaluationRecord


def export_evaluation_jsonl(
    record: EvaluationRecord, output_path: str | Path = ".local/eval_results.jsonl"
) -> Path:
    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "lab_id": "23-remotion-superpowers-studio",
        "case_id": record.case_id,
        "model": record.model,
        "success": record.success,
        "duration_actual": record.duration_actual,
        "duration_expected": record.duration_expected,
        "render_time_seconds": record.render_time_seconds,
        "file_size_kb": record.file_size_kb,
        "total_frames": record.total_frames,
        "scenes_count": record.scenes_count,
        "metrics": record.metrics,
    }

    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return target

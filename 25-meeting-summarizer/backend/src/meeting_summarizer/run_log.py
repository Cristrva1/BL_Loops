"""Exportador de corridas y métricas a JSONL según el estándar de BL_Loops."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import MeetingSummaryReport


def export_run_record(
    report: MeetingSummaryReport,
    runs_dir: Path,
    duration_ms: float | None = None,
    extra_metrics: dict[str, Any] | None = None,
) -> Path:
    """Exporta un registro sanitizado de la ejecución a un archivo JSONL.

    La traza es la evidencia que puede compartirse con el comparador central: guarda métricas y una
    huella del informe, nunca nombres, compromisos ni texto de la reunión. El informe completo vive
    solo en el SQLite local del laboratorio.
    """
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"run_{report.meeting_id}_{uuid.uuid4().hex[:8]}"
    file_path = runs_dir / f"{run_id}.jsonl"

    record = {
        "run_id": run_id,
        "meeting_id": report.meeting_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "model": report.model_used,
        "mode": report.mode,
        "duration_ms": duration_ms,
        "metrics": {
            "total_words": report.metadata.total_words,
            "total_turns": report.metadata.total_turns,
            "participants_count": len(report.metadata.participants),
            "decisions_count": len(report.decisions),
            "action_items_count": len(report.action_items),
            "topics_count": len(report.topics),
            "open_questions_count": len(report.open_questions),
            **(extra_metrics or {}),
        },
        "report_sha256": report_fingerprint(report),
        "raw_content_stored": False,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return file_path


def report_fingerprint(report: MeetingSummaryReport) -> str:
    """Huella SHA-256 del informe: permite enlazar la traza con SQLite sin copiar su contenido."""

    payload = json.dumps(report.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

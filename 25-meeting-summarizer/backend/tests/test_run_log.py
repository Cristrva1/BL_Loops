import json
from pathlib import Path

from meeting_summarizer.contracts import (
    ActionItem,
    KeyDecision,
    MeetingMetadata,
    MeetingSummaryReport,
)
from meeting_summarizer.run_log import export_run_record, report_fingerprint


def _report() -> MeetingSummaryReport:
    metadata = MeetingMetadata(title="Revisión sintética", participants=["Lucía Ferrer"])
    return MeetingSummaryReport(
        meeting_id="meet-001",
        title=metadata.title,
        executive_summary="Resumen con un dato confidencial",
        decisions=[KeyDecision(decision="Publicar en Markdown")],
        action_items=[ActionItem(task="Revisar enlaces", assignee="Lucía Ferrer")],
        email_followup="Hola equipo, adjunto la minuta.",
        metadata=metadata,
        model_used="qwen3.5:9b",
        created_at="2026-11-05T10:00:00Z",
    )


def test_jsonl_keeps_metrics_and_fingerprint_but_no_meeting_content(tmp_path: Path) -> None:
    report = _report()

    path = export_run_record(report, tmp_path / "runs", duration_ms=12.5)

    raw = path.read_text(encoding="utf-8")
    record = json.loads(raw)
    assert record["metrics"]["action_items_count"] == 1
    assert record["metrics"]["participants_count"] == 1
    assert record["report_sha256"] == report_fingerprint(report)
    assert record["raw_content_stored"] is False
    assert "report" not in record
    for secret in ("Lucía Ferrer", "dato confidencial", "Revisar enlaces", "adjunto la minuta"):
        assert secret not in raw

import tempfile
from pathlib import Path

from meeting_summarizer.contracts import (
    ActionItem,
    KeyDecision,
    MeetingMetadata,
    MeetingSummaryReport,
    TranscriptFormat,
)
from meeting_summarizer.storage import Storage


def test_storage_lifecycle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_meetings.db"
        storage = Storage(db_path)

        meta = MeetingMetadata(
            title="Reunión de prueba",
            detected_format=TranscriptFormat.MEET,
            total_words=120,
            total_turns=4,
            duration_seconds=180,
            participants=["Juan", "María"],
            speaker_turn_counts={"Juan": 2, "María": 2},
        )

        storage.save_meeting(
            meeting_id="meet-001",
            title=meta.title,
            raw_transcript="Juan: Hola\nMaría: Hola",
            metadata=meta,
        )

        meeting = storage.get_meeting("meet-001")
        assert meeting is not None
        assert meeting["title"] == "Reunión de prueba"
        assert meeting["total_words"] == 120
        assert "Juan" in meeting["participants"]

        report = MeetingSummaryReport(
            meeting_id="meet-001",
            title=meta.title,
            executive_summary="Resumen de prueba",
            topics=[],
            decisions=[KeyDecision(decision="Decisión 1")],
            action_items=[ActionItem(task="Tarea 1", assignee="Juan")],
            open_questions=[],
            email_followup="Email de prueba",
            metadata=meta,
            model_used="qwen3.5:9b",
            mode="completo",
            created_at="2026-09-19T10:00:00Z",
        )

        storage.save_summary(report)
        latest = storage.get_latest_summary("meet-001")
        assert latest is not None
        assert latest.executive_summary == "Resumen de prueba"
        assert len(latest.action_items) == 1

        # Test chat
        storage.save_chat_message("meet-001", "¿Quién asistió?", "Juan y María")
        chat = storage.get_chat_history("meet-001")
        assert len(chat) == 1
        assert chat[0]["question"] == "¿Quién asistió?"

        # Test list
        items = storage.list_meetings()
        assert len(items) == 1
        assert items[0].meeting_id == "meet-001"

from meeting_summarizer.contracts import (
    ActionItem,
    KeyDecision,
    MeetingMetadata,
    MeetingSummaryReport,
    TranscriptFormat,
)


def test_contracts_serialization():
    meta = MeetingMetadata(
        title="Sync Semanal",
        detected_format=TranscriptFormat.MEET,
        total_words=250,
        total_turns=12,
        duration_seconds=300,
        participants=["Carlos", "Ana"],
        speaker_turn_counts={"Carlos": 7, "Ana": 5},
    )

    action = ActionItem(
        task="Revisar base de datos",
        assignee="Carlos",
        deadline="2026-09-22",
        priority="alta",
        context="Optimización de índices",
    )

    decision = KeyDecision(
        decision="Usar SQLite local",
        rationale="Simplicidad y aislamiento",
        impact="Cero dependencias externas",
    )

    report = MeetingSummaryReport(
        meeting_id="meet-12345",
        title=meta.title,
        executive_summary="Resumen de la reunión de sincronización.",
        topics=[],
        decisions=[decision],
        action_items=[action],
        open_questions=["¿Qué modelo usar en producción?"],
        email_followup="Minuta para el equipo...",
        metadata=meta,
        model_used="qwen3.5:9b",
        mode="completo",
        created_at="2026-09-19T10:00:00Z",
    )

    dumped = report.model_dump()
    assert dumped["meeting_id"] == "meet-12345"
    assert len(dumped["action_items"]) == 1
    assert dumped["action_items"][0]["assignee"] == "Carlos"

    rehydrated = MeetingSummaryReport.model_validate(dumped)
    assert rehydrated.title == "Sync Semanal"
    assert rehydrated.action_items[0].priority == "alta"

"""Almacenamiento SQLite local para persistencia de transcripciones y resúmenes."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import (
    MeetingListItem,
    MeetingMetadata,
    MeetingSummaryReport,
)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class Storage:
    """Gestiona la base de datos SQLite aislada del laboratorio."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    format TEXT NOT NULL,
                    raw_transcript TEXT NOT NULL,
                    total_words INTEGER NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    participants_json TEXT NOT NULL,
                    turn_counts_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(id)
                );

                CREATE TABLE IF NOT EXISTS chat_history (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(id)
                );
                """
            )

    def save_meeting(
        self,
        meeting_id: str,
        title: str,
        raw_transcript: str,
        metadata: MeetingMetadata,
    ) -> None:
        """Guarda o actualiza la reunión base."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO meetings (
                    id, title, format, raw_transcript, total_words,
                    duration_seconds, participants_json, turn_counts_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meeting_id,
                    title,
                    metadata.detected_format.value,
                    raw_transcript,
                    metadata.total_words,
                    metadata.duration_seconds,
                    json.dumps(metadata.participants, ensure_ascii=False),
                    json.dumps(metadata.speaker_turn_counts, ensure_ascii=False),
                    _utc_now_iso(),
                ),
            )

    def save_summary(self, report: MeetingSummaryReport) -> str:
        """Guarda un reporte generado para la reunión."""
        summary_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO summaries (
                    id, meeting_id, model_used, mode, report_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    summary_id,
                    report.meeting_id,
                    report.model_used,
                    report.mode,
                    report.model_dump_json(),
                    report.created_at,
                ),
            )
        return summary_id

    def get_meeting(self, meeting_id: str) -> dict[str, Any] | None:
        """Recupera los datos de una reunión."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
            ).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "title": row["title"],
                "format": row["format"],
                "raw_transcript": row["raw_transcript"],
                "total_words": row["total_words"],
                "duration_seconds": row["duration_seconds"],
                "participants": json.loads(row["participants_json"]),
                "speaker_turn_counts": json.loads(row["turn_counts_json"]),
                "created_at": row["created_at"],
            }

    def get_latest_summary(self, meeting_id: str) -> MeetingSummaryReport | None:
        """Recupera el último resumen generado para una reunión."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT report_json FROM summaries
                WHERE meeting_id = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (meeting_id,),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["report_json"])
            return MeetingSummaryReport.model_validate(data)

    def list_meetings(self, limit: int = 50) -> list[MeetingListItem]:
        """Obtiene la lista de reuniones procesadas."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, format, total_words, duration_seconds,
                       participants_json, created_at
                FROM meetings
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            items: list[MeetingListItem] = []
            for r in rows:
                parts = json.loads(r["participants_json"]) if r["participants_json"] else []
                items.append(
                    MeetingListItem(
                        meeting_id=r["id"],
                        title=r["title"],
                        format=r["format"],
                        total_words=r["total_words"],
                        duration_seconds=r["duration_seconds"],
                        participants_count=len(parts),
                        created_at=r["created_at"],
                    )
                )
            return items

    def save_chat_message(self, meeting_id: str, question: str, answer: str) -> str:
        """Guarda un turno de conversación sobre la reunión."""
        chat_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_history (id, meeting_id, question, answer, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (chat_id, meeting_id, question, answer, _utc_now_iso()),
            )
        return chat_id

    def get_chat_history(self, meeting_id: str) -> list[dict[str, str]]:
        """Recupera el historial de preguntas y respuestas de una reunión."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, question, answer, created_at
                FROM chat_history
                WHERE meeting_id = ?
                ORDER BY created_at ASC
                """,
                (meeting_id,),
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "question": r["question"],
                    "answer": r["answer"],
                    "created_at": r["created_at"],
                }
                for r in rows
            ]

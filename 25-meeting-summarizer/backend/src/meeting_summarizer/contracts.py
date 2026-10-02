"""Modelos de datos y contratos Pydantic para el laboratorio de resúmenes."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TranscriptFormat(StrEnum):
    MEET = "meet"
    ZOOM_VTT = "zoom_vtt"
    TEAMS = "teams"
    PLAIN_TEXT = "plain_text"
    GENERIC = "generic"


class SpeakerTurn(BaseModel):
    """Representa una intervención individual dentro de la reunión."""

    turn_index: int
    speaker: str
    timestamp: str | None = None
    text: str


class MeetingMetadata(BaseModel):
    """Metadatos cuantitativos y descriptivos de la reunión."""

    title: str = "Reunión de equipo"
    detected_format: TranscriptFormat = TranscriptFormat.GENERIC
    total_words: int = 0
    total_turns: int = 0
    duration_seconds: int = 0
    participants: list[str] = Field(default_factory=list)
    speaker_turn_counts: dict[str, int] = Field(default_factory=dict)


class ActionItem(BaseModel):
    """Tarea o compromiso acordado con responsable y plazo."""

    task: str
    assignee: str = "Sin asignar"
    deadline: str | None = None
    priority: Literal["alta", "media", "baja"] = "media"
    context: str | None = None


class KeyDecision(BaseModel):
    """Decisión explícita adoptada durante la conversación."""

    decision: str
    rationale: str | None = None
    impact: str | None = None


class TopicDiscussion(BaseModel):
    """Resumen de un tema clave discutido."""

    topic: str
    summary: str
    participants_involved: list[str] = Field(default_factory=list)


class MeetingSummaryReport(BaseModel):
    """Reporte estructurado completo resultante del análisis de la transcripción."""

    meeting_id: str
    title: str
    executive_summary: str
    topics: list[TopicDiscussion] = Field(default_factory=list)
    decisions: list[KeyDecision] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    email_followup: str
    metadata: MeetingMetadata
    model_used: str
    mode: str = "completo"
    created_at: str


class SummarizeRequest(BaseModel):
    """Petición de procesamiento de transcripción."""

    transcript_text: str = Field(min_length=10)
    title: str | None = None
    model: str | None = None
    mode: Literal["completo", "ejecutivo", "tareas", "tecnico"] = "completo"
    save_to_db: bool = True


class ChatQuestionRequest(BaseModel):
    """Consulta interactiva (Q&A) sobre una reunión ya procesada."""

    meeting_id: str
    question: str = Field(min_length=3)
    model: str | None = None


class ChatResponse(BaseModel):
    """Respuesta a una consulta sobre la reunión."""

    meeting_id: str
    question: str
    answer: str
    citations: list[str] = Field(default_factory=list)


class PipelineEvent(BaseModel):
    """Evento SSE emitido durante la ejecución del pipeline."""

    stage: str
    progress: int = Field(ge=0, le=100)
    message: str
    payload: dict[str, Any] | None = None


class MeetingListItem(BaseModel):
    """Resumen liviano para listados de historial."""

    meeting_id: str
    title: str
    format: str
    total_words: int
    duration_seconds: int
    participants_count: int
    created_at: str

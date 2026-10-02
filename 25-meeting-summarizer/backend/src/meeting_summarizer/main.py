"""Servidor FastAPI con endpoints REST y streaming SSE para el laboratorio."""

from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from . import __version__
from .config import Settings, lab_root
from .contracts import (
    ChatQuestionRequest,
    ChatResponse,
    MeetingListItem,
    MeetingSummaryReport,
    SummarizeRequest,
)
from .ollama_client import OllamaClient, OllamaError
from .storage import Storage
from .summarizer import MeetingSummarizerEngine

settings = Settings()
storage = Storage(settings.get_db_path())
ollama = OllamaClient(
    base_url=settings.ollama_base_url,
    default_model=settings.ollama_model,
    timeout_seconds=settings.ollama_timeout_seconds,
    num_ctx=settings.ollama_num_ctx,
)
engine = MeetingSummarizerEngine(ollama, storage)

app = FastAPI(
    title="BL_Loops · 25 Resúmenes de Videollamadas",
    version=__version__,
    description="Procesamiento local de transcripciones de reuniones con Ollama.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://127.0.0.1:{settings.frontend_port}",
        f"http://localhost:{settings.frontend_port}",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "lab": "25-meeting-summarizer",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    ollama_ok = ollama.is_available()
    return {
        "status": "ok",
        "lab": "25-meeting-summarizer",
        "version": __version__,
        "ollama_available": ollama_ok,
        "default_model": settings.ollama_model,
    }


@app.get("/api/v1/models")
def list_models() -> dict[str, Any]:
    """Obtiene los modelos disponibles en Ollama local."""
    models = ollama.list_models()
    return {
        "models": models,
        "current_default": settings.ollama_model,
    }


@app.post("/api/v1/parse")
def parse_preview(req: SummarizeRequest) -> dict[str, Any]:
    """Pre-visualiza los metadatos y turnos detectados sin ejecutar LLM."""
    metadata, total_turns = engine.parse_only(req.transcript_text, req.title)
    return {
        "metadata": metadata.model_dump(),
        "total_turns": total_turns,
    }


@app.post("/api/v1/summarize", response_model=MeetingSummaryReport)
async def summarize_sync(req: SummarizeRequest) -> MeetingSummaryReport:
    """Procesamiento sincrónico directo."""
    report: MeetingSummaryReport | None = None
    try:
        async for event in engine.summarize_stream(req):
            if event.stage == "completed" and event.payload:
                report = MeetingSummaryReport.model_validate(event.payload["report"])
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not report:
        raise HTTPException(status_code=500, detail="No se pudo completar el análisis.")
    return report


@app.post("/api/v1/summarize/stream")
async def summarize_stream_sse(req: SummarizeRequest) -> StreamingResponse:
    """Procesamiento con streaming SSE para visualización de nodos en frontend."""

    async def event_generator():
        try:
            async for event in engine.summarize_stream(req):
                yield f"data: {event.model_dump_json()}\n\n"
        except OllamaError as exc:
            err_event = {
                "stage": "error",
                "progress": 0,
                "message": f"Error de inferencia: {str(exc)}",
                "payload": None,
            }
            yield f"data: {json.dumps(err_event)}\n\n"
        except Exception as exc:
            err_event = {
                "stage": "error",
                "progress": 0,
                "message": f"Error inesperado: {str(exc)}",
                "payload": None,
            }
            yield f"data: {json.dumps(err_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/v1/meetings", response_model=list[MeetingListItem])
def list_meetings() -> list[MeetingListItem]:
    """Obtiene el historial de reuniones almacenadas."""
    return storage.list_meetings()


@app.get("/api/v1/meetings/{meeting_id}")
def get_meeting_detail(meeting_id: str) -> dict[str, Any]:
    """Recupera la información completa de una reunión y su último resumen."""
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    latest_report = storage.get_latest_summary(meeting_id)
    chat_history = storage.get_chat_history(meeting_id)

    return {
        "meeting": meeting,
        "report": latest_report.model_dump() if latest_report else None,
        "chat_history": chat_history,
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
def ask_question(req: ChatQuestionRequest) -> ChatResponse:
    """Responde una consulta específica sobre una reunión."""
    try:
        return engine.ask_meeting_question(req.meeting_id, req.question, req.model)
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/v1/fixtures")
def get_sample_fixtures() -> dict[str, Any]:
    """Retorna transcripciones sintéticas de prueba disponibles en el laboratorio."""
    fixtures_dir = lab_root() / "fixtures"
    samples: list[dict[str, str]] = []
    if fixtures_dir.exists():
        for f in fixtures_dir.glob("*.*"):
            if f.suffix in (".txt", ".vtt", ".srt"):
                try:
                    content = f.read_text(encoding="utf-8")
                    samples.append({
                        "name": f.name,
                        "title": f.stem.replace("_", " ").title(),
                        "content": content,
                    })
                except Exception:
                    pass
    return {"fixtures": samples}

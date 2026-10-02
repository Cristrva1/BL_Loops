"""API FastAPI del laboratorio de orquestacion."""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from . import __version__
from .api_models import (
    ExampleResponse,
    ExperimentIntake,
    HealthResponse,
    LessonResponse,
    LessonStage,
    RunSnapshotResponse,
    StartRunResponse,
)
from .config import ConfigurationError, Settings, lab_root
from .ollama_client import OllamaClient, OllamaError
from .orchestrator import ExperimentRequest, OrchestrationError, run_experiment, variant_id_for
from .prompts import CASE_ID, DEFAULT_TASK
from .run_log import LAB_ID, RunLogger
from .store import STORE

app = FastAPI(
    title="BL_Loops · Orquestación multiagente",
    version=__version__,
    description=(
        "Compara un agente único con un pipeline planificador-autor-revisor sobre Ollama local."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5172", "http://localhost:5172"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_settings() -> Settings:
    return Settings.load()


def get_client(settings: Settings) -> OllamaClient:
    return OllamaClient(settings.base_url, settings.model, settings.timeout_seconds)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Orquestación local lista", "docs": "/docs", "lesson": "/api/v1/lesson"}


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    local = settings.base_url.startswith(("http://127.0.0.1", "http://localhost", "http://[::1]"))
    scope = "lab" if (lab_root() / ".env").is_file() else "workspace-or-defaults"
    return HealthResponse(
        version=__version__,
        lab_id=LAB_ID,
        model=settings.model,
        local_ollama_configured=local,
        phase="a0-own-orchestrator",
        configuration_scope=scope,
    )


@app.get("/api/v1/lesson", response_model=LessonResponse)
def lesson() -> LessonResponse:
    return LessonResponse(
        title="Parte A0 · Qué cambia al separar roles",
        learning_goal=(
            "Ver la diferencia observable entre un agente único y un pipeline "
            "planificador-autor-revisor con un gate determinista."
        ),
        stages=[
            LessonStage(
                number=1,
                name="Tarea",
                question="¿Qué guía hay que producir y cómo se comprueba?",
                output="Caso I-ORCH-001 con lista de checks.",
            ),
            LessonStage(
                number=2,
                name="Línea base",
                question="¿Qué logra un solo modelo con la misma entrada?",
                output="Markdown puntuado sin handoffs.",
            ),
            LessonStage(
                number=3,
                name="Plan y autoría",
                question="¿El plan JSON obliga a una estructura que el autor debe respetar?",
                output="Handoff Plan → Markdown.",
            ),
            LessonStage(
                number=4,
                name="Revisión",
                question="¿El revisor comprueba requisitos o solo opina?",
                output="Opinión del modelo más gate determinista.",
            ),
            LessonStage(
                number=5,
                name="Comparación",
                question="¿La orquestación mejoró los checks, el tiempo o ambas cosas?",
                output="Tabla y JSONL sanitizado.",
            ),
        ],
        glossary={
            "Handoff": "Contrato tipado que un agente entrega al siguiente.",
            "Línea base": "El mismo caso resuelto por un solo agente.",
            "Gate determinista": "Lista de checks ejecutada por código, no por el modelo.",
            "Corrección única": "Un segundo intento del autor si el gate falla. No es un loop.",
        },
        deferred=[
            "LangGraph, CrewAI o AG2",
            "Ejecución en paralelo",
            "Loops con presupuesto de iteraciones",
            "Comparación de los cuatro modelos iniciales",
        ],
    )


@app.get("/api/v1/examples/i-orch-001", response_model=ExampleResponse)
def example() -> ExampleResponse:
    return ExampleResponse(
        case_id=CASE_ID,
        title="Guía breve para ejecutar un agente local",
        task=DEFAULT_TASK,
    )


@app.post("/api/v1/experiments", response_model=StartRunResponse)
def start_experiment(intake: ExperimentIntake) -> StartRunResponse:
    if not intake.include_baseline and not intake.include_orchestrated:
        raise HTTPException(
            status_code=422,
            detail="Selecciona al menos una variante: agente único u orquestada.",
        )
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    run_id = f"run-{uuid4()}"
    request = ExperimentRequest(
        task=intake.task,
        include_baseline=intake.include_baseline,
        include_orchestrated=intake.include_orchestrated,
    )
    STORE.create(
        run_id,
        case_id=CASE_ID,
        model=settings.model,
        include_baseline=intake.include_baseline,
        include_orchestrated=intake.include_orchestrated,
    )
    thread = threading.Thread(
        target=_execute_run,
        args=(run_id, request, settings),
        daemon=True,
        name=f"orch-{run_id[:12]}",
    )
    thread.start()
    return StartRunResponse(run_id=run_id, status="queued", case_id=CASE_ID)


@app.get("/api/v1/runs/{run_id}", response_model=RunSnapshotResponse)
def get_run(run_id: str) -> RunSnapshotResponse:
    snapshot = STORE.get(run_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No existe esa corrida en memoria.")
    return RunSnapshotResponse.model_validate(snapshot.public_dict())


@app.get("/api/v1/runs/{run_id}/events")
async def stream_events(run_id: str) -> StreamingResponse:
    if STORE.get(run_id) is None:
        raise HTTPException(status_code=404, detail="No existe esa corrida en memoria.")

    async def generate() -> AsyncIterator[str]:
        last = 0
        while True:
            snapshot = STORE.get(run_id)
            if snapshot is None:
                break
            while last < len(snapshot.events):
                event = snapshot.events[last]
                last += 1
                envelope = {"event": event, "snapshot": snapshot.public_dict()}
                yield f"data: {json.dumps(envelope, ensure_ascii=False)}\n\n"
            if snapshot.status in {"completed", "failed"} and last >= len(snapshot.events):
                break
            await asyncio.sleep(0.15)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _execute_run(run_id: str, request: ExperimentRequest, settings: Settings) -> None:
    logger = RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        variant_id_for(request),
        listener=lambda event: STORE.apply(run_id, event),
        run_id=run_id,
    )
    try:
        client = get_client(settings)
        result = run_experiment(request, settings, client, logger)
    except (OllamaError, OrchestrationError, ConfigurationError) as exc:
        logger.finish(status="failed", reason=str(exc))
        snapshot = STORE.get(run_id)
        if snapshot is not None:
            snapshot.status = "failed"
            snapshot.error = str(exc)
        return
    except Exception:
        logger.finish(status="failed", reason="Fallo interno del orquestador.")
        snapshot = STORE.get(run_id)
        if snapshot is not None:
            snapshot.status = "failed"
            snapshot.error = "Fallo interno del orquestador."
        return

    try:
        relative = result.jsonl_path.resolve().relative_to(settings.root.resolve()).as_posix()
    except ValueError:
        relative = result.jsonl_path.name
    STORE.finish(run_id, result, relative)

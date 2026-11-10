"""API FastAPI del laboratorio de agentes en paralelo."""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator
from typing import Any
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
    SourceSummary,
    StartRunResponse,
)
from .config import ConfigurationError, Settings, lab_root
from .ollama_client import OllamaClient, OllamaError
from .orchestrator import ExperimentRequest, ParallelError, run_experiment, variant_id_for
from .prompts import CASE_ID, DEFAULT_TASK
from .run_log import LAB_ID, RunLogger
from .sources import source_summaries
from .store import STORE, TERMINAL_EVENTS

app = FastAPI(
    title="BL_Loops · Agentes en paralelo",
    version=__version__,
    description=(
        "Compara una extracción secuencial con un fan-out/fan-in de tres fuentes "
        "sobre un modelo Ollama compartido."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5175", "http://localhost:5175"],
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
    return {"message": "Fan-out local listo", "docs": "/docs", "lesson": "/api/v1/lesson"}


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
        phase="a-asyncio-fanout",
        configuration_scope=scope,
        max_in_flight=settings.max_in_flight,
    )


@app.get("/api/v1/lesson", response_model=LessonResponse)
def lesson() -> LessonResponse:
    return LessonResponse(
        title="Parte A · Cuándo el paralelismo ahorra tiempo",
        learning_goal=(
            "Ver un fan-out/fan-in de tres fuentes independientes, medir el tiempo "
            "secuencial frente al paralelo y no presentar una rama fallida como completa."
        ),
        stages=[
            LessonStage(
                number=1,
                name="Fuentes",
                question="¿Qué tres documentos independientes hay que leer?",
                output="Caso I-PARALLEL-002 con procedencia por fuente.",
            ),
            LessonStage(
                number=2,
                name="Secuencial",
                question="¿Cuánto tarda extraer A, luego B, luego C?",
                output="Tres ramas en serie y una tabla unida.",
            ),
            LessonStage(
                number=3,
                name="Fan-out",
                question="¿Las tres ramas llegan a running a la vez?",
                output="Tres HTTP concurrentes al mismo modelo.",
            ),
            LessonStage(
                number=4,
                name="Fan-in",
                question="¿El agregador espera resultados o un timeout explícito?",
                output="Tabla solo con ramas completas.",
            ),
            LessonStage(
                number=5,
                name="Comparación",
                question="¿Bajó el tiempo de pared sin perder hechos?",
                output="Speedup, overlap y JSONL sanitizado.",
            ),
        ],
        glossary={
            "Fan-out": "Lanzar varias ramas independientes a la vez.",
            "Fan-in": "Esperar esas ramas y unir solo lo que terminó bien.",
            "Procedencia": "Cada hecho recuerda de qué fuente salió.",
            "max_in_flight": "Tope de ramas que pueden llamar al modelo a la vez.",
        },
        deferred=[
            "LangGraphJS con ramas paralelas",
            "CrewAI o AG2",
            "Varios modelos simultáneos en VRAM",
            "Comparación de los cuatro modelos iniciales",
        ],
    )


@app.get("/api/v1/examples/i-parallel-002", response_model=ExampleResponse)
def example() -> ExampleResponse:
    try:
        sources = [SourceSummary.model_validate(item) for item in source_summaries()]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ExampleResponse(
        case_id=CASE_ID,
        title="Tres fuentes independientes del Taller Norte",
        task=DEFAULT_TASK,
        sources=sources,
    )


@app.post("/api/v1/experiments", response_model=StartRunResponse)
def start_experiment(intake: ExperimentIntake) -> StartRunResponse:
    if not intake.include_sequential and not intake.include_parallel:
        raise HTTPException(
            status_code=422,
            detail="Selecciona al menos una variante: secuencial o paralela.",
        )
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    run_id = f"run-{uuid4()}"
    request = ExperimentRequest(
        task=intake.task,
        include_sequential=intake.include_sequential,
        include_parallel=intake.include_parallel,
    )
    STORE.create(
        run_id,
        case_id=CASE_ID,
        model=settings.model,
        include_sequential=intake.include_sequential,
        include_parallel=intake.include_parallel,
    )
    thread = threading.Thread(
        target=_execute_run,
        args=(run_id, request, settings),
        daemon=True,
        name=f"par-{run_id[:12]}",
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
            batch = STORE.read_since(run_id, last)
            if batch is None:
                break
            events, public_snapshot, finished = batch
            for event in events:
                last += 1
                envelope = {"event": event, "snapshot": public_snapshot}
                yield f"data: {json.dumps(envelope, ensure_ascii=False)}\n\n"
            if finished:
                break
            await asyncio.sleep(0.15)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _execute_run(run_id: str, request: ExperimentRequest, settings: Settings) -> None:
    terminal_events: list[dict[str, Any]] = []

    def listener(event: dict[str, Any]) -> None:
        # run.completed/run.failed esperan al resultado: ver STORE.finish y STORE.fail.
        if event["event_type"] in TERMINAL_EVENTS:
            terminal_events.append(event)
        else:
            STORE.apply(run_id, event)

    logger = RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        variant_id_for(request),
        listener=listener,
        run_id=run_id,
    )
    try:
        client = get_client(settings)
        result = run_experiment(request, settings, client, logger)
    except (OllamaError, ParallelError, ConfigurationError) as exc:
        logger.finish(status="failed", reason=str(exc))
        STORE.fail(run_id, str(exc), terminal_events)
        return
    except Exception:
        logger.finish(status="failed", reason="Fallo interno del orquestador paralelo.")
        STORE.fail(run_id, "Fallo interno del orquestador paralelo.", terminal_events)
        return

    try:
        relative = result.jsonl_path.resolve().relative_to(settings.root.resolve()).as_posix()
    except ValueError:
        relative = result.jsonl_path.name
    STORE.finish(run_id, result, relative, terminal_events)

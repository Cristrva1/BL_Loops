"""API FastAPI del laboratorio de loops acotados."""

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
    HealthResponse,
    LessonResponse,
    LessonStage,
    LoopIntake,
    RunSnapshotResponse,
    StartRunResponse,
)
from .config import ConfigurationError, Settings, lab_root
from .engine import Budget, LoopError, LoopRequest, run_loop
from .ollama_client import OllamaClient, OllamaError
from .prompts import CASE_ID, DEFAULT_TASK, INITIAL_PROMPT
from .run_log import LAB_ID, RunLogger
from .store import STORE

app = FastAPI(
    title="BL_Loops · Loops acotados",
    version=__version__,
    description=(
        "Mejora un prompt con presupuesto de iteraciones, errores y tiempo. "
        "El gate es determinista y se conserva el mejor candidato."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5176", "http://localhost:5176"],
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
    return {"message": "Loop local listo", "docs": "/docs", "lesson": "/api/v1/lesson"}


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
        phase="a0-typed-python-loop",
        configuration_scope=scope,
    )


@app.get("/api/v1/lesson", response_model=LessonResponse)
def lesson() -> LessonResponse:
    return LessonResponse(
        title="Parte A0 · Un loop que sabe parar",
        learning_goal=(
            "Ver cómo un ciclo mejora un prompt con score, presupuesto y mejor candidato, "
            "sin quedarse ejecutando para siempre."
        ),
        stages=[
            LessonStage(
                number=1,
                name="Declaración",
                question="¿Cuál es el objetivo, el score inicial y el presupuesto?",
                output="Caso I-LOOP-003 con cinco assertions.",
            ),
            LessonStage(
                number=2,
                name="Generar",
                question="¿Qué produce el prompt actual?",
                output="Salida del modelo, sin guardar el texto crudo en el JSONL.",
            ),
            LessonStage(
                number=3,
                name="Puntuar",
                question="¿Cuántas assertions estructurales cumple el JSON?",
                output="Score determinista 0/5 a 5/5.",
            ),
            LessonStage(
                number=4,
                name="Decidir",
                question="¿Se alcanzó el umbral o se agotó el presupuesto?",
                output="Motivo de salida explícito.",
            ),
            LessonStage(
                number=5,
                name="Mejorar",
                question="¿El nuevo prompt sube el score o solo cambia el estilo?",
                output="Mejor candidato conservado, no necesariamente el último.",
            ),
        ],
        glossary={
            "Loop": "Ciclo generate → score → decide → improve con condición de parada.",
            "Presupuesto": "Tope de iteraciones, errores y tiempo. Lo que ocurra primero gana.",
            "Mejor candidato": "El prompt y la salida con más checks, aunque no sea el último.",
            "Gate determinista": "Cinco assertions ejecutadas por código, no por el modelo.",
        },
        deferred=[
            "LangGraphJS y criterios de loop-engineering como runtime",
            "OpenEvolve y funciones de fitness de código",
            "Comparación de los cuatro modelos iniciales",
        ],
    )


@app.get("/api/v1/examples/i-loop-003", response_model=ExampleResponse)
def example() -> ExampleResponse:
    budget = Budget()
    return ExampleResponse(
        case_id=CASE_ID,
        title="Mejorar un prompt hasta cinco assertions",
        task=DEFAULT_TASK,
        initial_prompt=INITIAL_PROMPT,
        budget=budget.as_view().model_dump(mode="json"),
    )


@app.post("/api/v1/experiments", response_model=StartRunResponse)
def start_experiment(intake: LoopIntake) -> StartRunResponse:
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    run_id = f"run-{uuid4()}"
    request = LoopRequest(task=intake.task, initial_prompt=intake.initial_prompt)
    STORE.create(run_id, case_id=CASE_ID, model=settings.model)
    thread = threading.Thread(
        target=_execute_run,
        args=(run_id, request, settings),
        daemon=True,
        name=f"loop-{run_id[:12]}",
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


def _execute_run(run_id: str, request: LoopRequest, settings: Settings) -> None:
    logger = RunLogger(
        settings.runs_dir,
        settings.model,
        settings.base_url,
        "bounded-loop",
        listener=lambda event: STORE.apply(run_id, event),
        run_id=run_id,
    )
    try:
        client = get_client(settings)
        result = run_loop(request, settings, client, logger)
    except (OllamaError, LoopError, ConfigurationError) as exc:
        logger.finish(status="failed", reason=str(exc))
        snapshot = STORE.get(run_id)
        if snapshot is not None:
            snapshot.status = "failed"
            snapshot.error = str(exc)
        return
    except Exception:
        logger.finish(status="failed", reason="Fallo interno del loop.")
        snapshot = STORE.get(run_id)
        if snapshot is not None:
            snapshot.status = "failed"
            snapshot.error = "Fallo interno del loop."
        return

    try:
        relative = result.jsonl_path.resolve().relative_to(settings.root.resolve()).as_posix()
    except ValueError:
        relative = result.jsonl_path.name
    STORE.finish(run_id, result, relative)

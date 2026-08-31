"""API FastAPI de la Parte 1 de la fábrica."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .api_models import (
    ContractSchemaResponse,
    ExportRequest,
    ExportResult,
    FactoryIntake,
    FactoryResult,
    GuidanceResult,
    HealthResponse,
    LessonResponse,
    LessonStage,
)
from .config import Settings, configuration_scope, find_env_file
from .contracts import AgentSpec, PromptSpec, RunRecord, SkillSpec
from .exporter import display_path, export_artifact
from .factory import (
    IncompleteIntakeError,
    analyze_intake,
    build_artifact,
    exported_events,
)
from .hashing import has_valid_content_hash

app = FastAPI(
    title="BL_Loops · Fábrica de Prompts y Agentes",
    version=__version__,
    description=(
        "Parte 1 educativa: convierte un briefing en contratos tipados sin invocar un LLM."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "message": "Fábrica local lista",
        "docs": "/docs",
        "lesson": "/api/v1/lesson",
    }


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = Settings()
    env_file = find_env_file()
    return HealthResponse(
        version=__version__,
        local_ollama_configured=settings.ollama_base_url.startswith(
            ("http://127.0.0.1", "http://localhost", "http://[::1]")
        ),
        configuration_scope=configuration_scope(env_file),
    )


@app.get("/api/v1/lesson", response_model=LessonResponse)
def lesson() -> LessonResponse:
    return LessonResponse(
        title="Parte 1 · Del deseo humano al contrato verificable",
        learning_goal=(
            "Distinguir una idea, un briefing y un artefacto validado antes de añadir IA."
        ),
        stages=[
            LessonStage(
                number=1,
                name="Capturar",
                question="¿Qué quieres lograr?",
                output="Idea tratada como dato.",
            ),
            LessonStage(
                number=2,
                name="Aclarar",
                question="¿Qué huecos impedirían verificarlo?",
                output="Briefing completo.",
            ),
            LessonStage(
                number=3,
                name="Contratar",
                question="¿Qué campos y límites debe tener?",
                output="PromptSpec, AgentSpec o SkillSpec.",
            ),
            LessonStage(
                number=4,
                name="Validar",
                question="¿Cumple tipos, permisos y parada?",
                output="Artefacto Pydantic válido.",
            ),
            LessonStage(
                number=5,
                name="Exportar",
                question="¿Puede reutilizarse sin dependencia de runtime?",
                output="JSON local con huella SHA-256.",
            ),
        ],
        glossary={
            "PromptSpec": "Plano validado de una instrucción para un modelo.",
            "AgentSpec": "Prompt más modelo, tools, memoria, permisos y parada.",
            "SkillSpec": "Procedimiento portable con disparadores y recursos.",
            "RunRecord": "Registro JSONL para comparar una ejecución.",
            "content_hash": "Huella que cambia si cambia el contenido.",
        },
        deferred=[
            "Generación asistida por Ollama",
            "Persistencia SQLite",
            "Eventos SSE en tiempo real",
            "Ejecución de un agente",
        ],
    )


@app.get(
    "/api/v1/contracts/{contract_name}",
    response_model=ContractSchemaResponse,
    response_model_by_alias=True,
)
def contract_schema(
    contract_name: Literal["prompt", "agent", "skill", "run"],
) -> ContractSchemaResponse:
    contracts = {
        "prompt": (PromptSpec, "Contrato de una instrucción reproducible."),
        "agent": (AgentSpec, "Contrato de un agente con autoridad acotada."),
        "skill": (SkillSpec, "Contrato de una skill portable."),
        "run": (RunRecord, "Sobre JSONL para evaluación independiente."),
    }
    model, description = contracts[contract_name]
    return ContractSchemaResponse(
        name=contract_name,
        description=description,
        schema_=model.model_json_schema(),
    )


@app.post("/api/v1/factory/questions", response_model=GuidanceResult)
def questions(intake: FactoryIntake) -> GuidanceResult:
    return analyze_intake(intake)


@app.post("/api/v1/factory/draft", response_model=FactoryResult)
def draft(intake: FactoryIntake) -> FactoryResult:
    try:
        return build_artifact(intake)
    except IncompleteIntakeError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "incomplete_intake",
                "message": str(exc),
                "guidance": exc.guidance.model_dump(mode="json"),
            },
        ) from exc


@app.post("/api/v1/artifacts/export", response_model=ExportResult)
def export(request: ExportRequest) -> ExportResult:
    if not has_valid_content_hash(request.artifact):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "content_hash_mismatch",
                "message": "El artefacto cambió después de validarse.",
            },
        )
    path = export_artifact(request.artifact)
    return ExportResult(
        artifact_id=request.artifact.artifact_id,
        relative_path=display_path(path),
        content_hash=request.artifact.content_hash,
        events=exported_events(),
    )

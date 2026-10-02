"""Contratos Pydantic para HyperFrames Video Studio."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class PipelineState(str, Enum):
    IDLE = "IDLE"
    ANALYZING_BRIEF = "ANALYZING_BRIEF"
    GENERATING_SCRIPT = "GENERATING_SCRIPT"
    BUILDING_COMPOSITION = "BUILDING_COMPOSITION"
    VALIDATING_LINT = "VALIDATING_LINT"
    RENDERING_VIDEO = "RENDERING_VIDEO"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SceneSpec(BaseModel):
    id: str = Field(..., description="Identificador único de la escena")
    title: str = Field(..., description="Título de la escena")
    start_time: float = Field(..., description="Segundo de inicio")
    duration: float = Field(..., description="Duración en segundos")
    headline: str = Field(..., description="Encabezado principal en pantalla")
    body: str = Field(..., description="Texto descriptivo o de código")
    bg_gradient: str = Field(
        default="linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
        description="Fondo CSS para la escena",
    )
    accent_color: str = Field(default="#6366f1", description="Color de acento")
    badge_text: str = Field(default="HyperFrames", description="Badge superior")
    code_snippet: str | None = Field(
        default=None, description="Snippet de código o CLI para mostrar"
    )


class VideoBrief(BaseModel):
    topic: str = Field(
        default="Explicar qué es HyperFrames, cómo usarlo y qué puede hacer",
        description="Tema central del video",
    )
    target_duration: float = Field(default=15.0, description="Duración objetivo en segundos")
    width: int = Field(default=1920, description="Ancho en píxeles")
    height: int = Field(default=1080, description="Alto en píxeles")
    fps: int = Field(default=30, description="Cuadros por segundo")
    model: str = Field(default="qwen3.5:9b", description="Modelo Ollama a utilizar")


class PipelineEvent(BaseModel):
    timestamp: str
    state: PipelineState
    node: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class RenderResult(BaseModel):
    video_path: str
    duration: float
    width: int
    height: int
    fps: int
    file_size_bytes: int
    render_elapsed_seconds: float
    success: bool
    error: str | None = None


class EvaluationRecord(BaseModel):
    case_id: str
    model: str
    success: bool
    duration_actual: float
    duration_expected: float
    render_time_seconds: float
    file_size_kb: float
    scenes_count: int
    metrics: dict[str, float | str | bool]

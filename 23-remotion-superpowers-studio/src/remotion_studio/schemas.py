"""Contratos de datos Pydantic para Remotion Superpowers Studio."""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from remotion_studio.config import validate_model


class RemotionState(StrEnum):
    IDLE = "IDLE"
    ANALYZING_BRIEF = "ANALYZING_BRIEF"
    PLANNING_SCENES = "PLANNING_SCENES"
    CALCULATING_FRAMES = "CALCULATING_FRAMES"
    WRITING_REACT_PROPS = "WRITING_REACT_PROPS"
    RENDERING_VIDEO = "RENDERING_VIDEO"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RemotionScene(BaseModel):
    id: str
    title: str
    start_frame: int
    duration_in_frames: int
    headline: str
    subheadline: str
    bg_gradient: str = "linear-gradient(135deg, #090d16 0%, #1e1b4b 100%)"
    accent_color: str = "#6366f1"
    badge: str = "Remotion Superpowers"
    code: str | None = None


class RemotionBrief(BaseModel):
    topic: str = Field(
        default="Demostrar Remotion y el patrón Remotion Superpowers con React y IA Local",
        description="Tema a cubrir en el video",
    )
    target_duration: float = Field(default=12.0, ge=4.0, le=60.0, description="Duración en segundos")
    # Root.tsx fija la composición en 1920x1080 a 30 fps: el contrato no admite otros valores.
    fps: Literal[30] = Field(default=30, description="Fotogramas por segundo")
    width: Literal[1920] = Field(default=1920, description="Ancho")
    height: Literal[1080] = Field(default=1080, description="Alto")
    model: str = Field(default="qwen3.5:9b", description="Modelo Ollama")

    @field_validator("model")
    @classmethod
    def _local_model(cls, value: str) -> str:
        return validate_model(value)


class PipelineEvent(BaseModel):
    timestamp: str
    state: RemotionState
    node: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class RenderResult(BaseModel):
    video_path: str
    duration: float
    width: int
    height: int
    fps: int
    total_frames: int
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
    total_frames: int
    scenes_count: int
    metrics: dict[str, int | float | str | bool]

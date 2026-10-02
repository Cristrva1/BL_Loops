"""Contratos Pydantic para Open Generative AI Studio."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class StudioState(str, Enum):
    IDLE = "IDLE"
    ANALYZING_CONCEPT = "ANALYZING_CONCEPT"
    EXPANDING_PROMPTS = "EXPANDING_PROMPTS"
    GENERATING_STORYBOARD = "GENERATING_STORYBOARD"
    RENDERING_ANIMATIC = "RENDERING_ANIMATIC"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ShotType(str, Enum):
    EXTREME_WIDE = "Extreme Wide Shot"
    WIDE = "Wide Shot"
    MEDIUM = "Medium Shot"
    CLOSE_UP = "Close-up"
    EXTREME_CLOSE_UP = "Extreme Close-up"
    DRONE_AERIAL = "Drone Aerial"


class CameraMovement(str, Enum):
    STATIC = "Static"
    SLOW_PAN_RIGHT = "Slow Pan Right"
    SLOW_PAN_LEFT = "Slow Pan Left"
    DOLLY_IN = "Dolly In (Push In)"
    DOLLY_OUT = "Dolly Out (Pull Back)"
    TRACKING_SHOT = "Tracking Shot"
    CRANE_DOWN = "Crane Down"


class StoryboardShot(BaseModel):
    shot_number: int
    shot_type: ShotType = ShotType.WIDE
    camera_movement: CameraMovement = CameraMovement.DOLLY_IN
    duration_seconds: float = Field(default=3.0, ge=1.0)
    headline: str
    description: str
    prompt_expansion: str = Field(
        ..., description="Prompt cinematográfico de alta densidad para generadores"
    )
    lighting: str = "Cinematic volumetric lighting, warm rim light, moody contrast"
    aspect_ratio: str = "16:9"
    accent_color: str = "#6366f1"


class PromptExpansionRequest(BaseModel):
    raw_idea: str = Field(
        default="Un astronauta descubre ruinas antiguas en un desierto alienígena bioluminiscente",
        description="Idea o brief inicial del usuario",
    )
    style: str = "Cinematográfico Sci-Fi 35mm"
    model: str = "qwen3.5:9b"


class StoryboardProject(BaseModel):
    title: str = "Expedición Nebular"
    narrative_concept: str = Field(
        default="Un equipo de exploración descubre una señal alienígena enterrada en un cañón de hielo",
        description="Sinopsis del proyecto",
    )
    total_duration_target: float = 12.0
    shots: list[StoryboardShot] = Field(default_factory=list)
    model: str = "qwen3.5:9b"


class PipelineEvent(BaseModel):
    timestamp: str
    state: StudioState
    node: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class RenderResult(BaseModel):
    video_path: str
    duration: float
    width: int
    height: int
    fps: int
    shots_count: int
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
    shots_count: int
    metrics: dict[str, float | str | bool]

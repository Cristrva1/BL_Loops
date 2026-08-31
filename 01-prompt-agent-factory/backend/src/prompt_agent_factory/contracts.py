"""Contratos centrales de la fábrica.

Un contrato convierte expectativas humanas en datos que Python puede validar.
Los nombres están en inglés para que los artefactos sean portables; las
descripciones y la interfaz permanecen en español para facilitar el aprendizaje.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    """Base común: rechaza campos desconocidos y limpia espacios accidentales."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ArtifactType(StrEnum):
    PROMPT = "prompt"
    AGENT = "agent"
    SKILL = "skill"


class OutputFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"
    YAML = "yaml"
    CODE = "code"


class PermissionEffect(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class RunStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class FlowStatus(StrEnum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class SourceRef(StrictModel):
    """Rastro de la fuente que justificó una decisión del artefacto."""

    path: str = Field(min_length=1, max_length=500)
    section: str | None = Field(default=None, max_length=200)
    note: str = Field(min_length=1, max_length=500)


class InputSpec(StrictModel):
    """Dato que el prompt, agente o skill espera recibir."""

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=80)
    description: str = Field(min_length=3, max_length=500)
    required: bool = True
    example: str | None = Field(default=None, max_length=500)


class OutputContract(StrictModel):
    """Forma verificable que debe tener la respuesta."""

    format: OutputFormat
    description: str = Field(min_length=3, max_length=500)
    schema_name: str | None = Field(default=None, max_length=120)
    required_sections: list[str] = Field(default_factory=list, max_length=20)
    max_items: int | None = Field(default=None, ge=1, le=1000)


class PermissionRule(StrictModel):
    """Capacidad concreta que se permite o se niega."""

    capability: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$", max_length=120)
    effect: PermissionEffect
    scope: str = Field(min_length=1, max_length=300)
    reason: str = Field(min_length=3, max_length=500)
    requires_approval: bool = False


class PermissionPolicy(StrictModel):
    """Límite de autoridad. Lo no declarado queda negado."""

    default_effect: Literal[PermissionEffect.DENY] = PermissionEffect.DENY
    runtime_network: bool = False
    external_writes: bool = False
    rules: list[PermissionRule] = Field(default_factory=list, max_length=50)


class StopCondition(StrictModel):
    """Regla observable que impide que un agente o flujo continúe sin límite."""

    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=80)
    description: str = Field(min_length=3, max_length=500)
    outcome: Literal["done", "blocked", "failed"]


class ExampleSpec(StrictModel):
    """Ejemplo compacto de entrada y salida; enseña el formato, no hechos nuevos."""

    input: dict[str, Any]
    output: dict[str, Any] | str
    note: str = Field(min_length=3, max_length=300)


class ToolSpec(StrictModel):
    """Herramienta explícita y acotada que puede usar un agente."""

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=80)
    description: str = Field(min_length=3, max_length=500)
    mode: Literal["simulated", "read_only_local"] = "simulated"
    input_schema: dict[str, Any]
    requires_approval: bool = True


class MemoryPolicy(StrictModel):
    """Qué estado puede conservar el agente y durante cuánto tiempo."""

    short_term: bool = True
    long_term: bool = False
    stores_raw_pii: Literal[False] = False
    retention: Literal["run_only", "session"] = "run_only"


class BaseArtifact(StrictModel):
    """Campos comunes a cualquier resultado reutilizable de la fábrica."""

    artifact_id: str = Field(pattern=r"^[a-z]+_[0-9a-f]{12}$")
    artifact_type: ArtifactType
    schema_version: Literal["1.0.0"] = "1.0.0"
    title: str = Field(min_length=3, max_length=160)
    purpose: str = Field(min_length=10, max_length=2000)
    inputs: list[InputSpec] = Field(min_length=1, max_length=30)
    instructions: list[str] = Field(min_length=1, max_length=30)
    constraints: list[str] = Field(min_length=1, max_length=30)
    output_contract: OutputContract
    permissions: PermissionPolicy
    stop_conditions: list[StopCondition] = Field(min_length=1, max_length=20)
    evaluation_refs: list[str] = Field(min_length=1, max_length=20)
    source_refs: list[SourceRef] = Field(min_length=1, max_length=50)
    created_at: datetime
    generator_model: str = Field(min_length=3, max_length=160)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at debe incluir zona horaria")
        return value


class PromptSpec(BaseArtifact):
    """Plano de una instrucción reproducible para un modelo."""

    artifact_type: Literal[ArtifactType.PROMPT] = ArtifactType.PROMPT
    role: str = Field(min_length=3, max_length=300)
    system_message: str = Field(min_length=20, max_length=8000)
    user_template: str = Field(min_length=10, max_length=8000)
    examples: list[ExampleSpec] = Field(default_factory=list, max_length=5)
    uncertainty_policy: str = Field(min_length=10, max_length=500)


class AgentSpec(BaseArtifact):
    """Plano de un agente: prompt más modelo, tools, memoria, autoridad y parada."""

    artifact_type: Literal[ArtifactType.AGENT] = ArtifactType.AGENT
    model_ref: str = Field(min_length=3, max_length=160)
    role: str = Field(min_length=3, max_length=300)
    goal: str = Field(min_length=10, max_length=2000)
    tools: list[ToolSpec] = Field(default_factory=list, max_length=20)
    memory: MemoryPolicy = Field(default_factory=MemoryPolicy)
    max_steps: int = Field(default=4, ge=1, le=20)
    human_approval: bool = True


class SkillSpec(BaseArtifact):
    """Plano portable de una skill con disparadores y revelado progresivo."""

    artifact_type: Literal[ArtifactType.SKILL] = ArtifactType.SKILL
    triggers: list[str] = Field(min_length=1, max_length=20)
    instruction_template: str = Field(min_length=20, max_length=12000)
    resource_refs: list[str] = Field(default_factory=list, max_length=50)
    progressive_disclosure: list[str] = Field(min_length=1, max_length=10)


Artifact = Annotated[PromptSpec | AgentSpec | SkillSpec, Field(discriminator="artifact_type")]


class RunEvent(StrictModel):
    """Un cambio de estado observable durante una corrida."""

    sequence: int = Field(ge=1)
    event_id: str = Field(pattern=r"^evt_[0-9a-f]{12}$")
    occurred_at: datetime
    node_id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$", max_length=100)
    status: FlowStatus
    message: str = Field(min_length=1, max_length=500)
    payload_sanitized: dict[str, Any] = Field(default_factory=dict)


class ResourceUsage(StrictModel):
    latency_ms: float = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    ram_peak_mb: float | None = Field(default=None, ge=0)
    vram_peak_mb: float | None = Field(default=None, ge=0)


class MetricScore(StrictModel):
    name: Literal[
        "task_success",
        "quality",
        "fidelity",
        "tool_use",
        "latency_efficiency",
        "token_efficiency",
        "resource_efficiency",
        "stability",
        "human_rating",
    ]
    applicable: bool = True
    value: float | None = Field(default=None, ge=0, le=1)
    note: str | None = Field(default=None, max_length=500)


class RunRecord(StrictModel):
    """Sobre JSONL autocontenido que consumirá el evaluador central."""

    run_id: str = Field(pattern=r"^run_[0-9a-f]{12}$")
    schema_version: Literal["1.0.0"] = "1.0.0"
    lab_id: Literal["01-prompt-agent-factory"] = "01-prompt-agent-factory"
    variant: str = Field(min_length=1, max_length=120)
    commit_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{7,40}$")
    model_ref: str
    evaluation_case: str
    case_version: str
    artifact_refs: list[str] = Field(default_factory=list)
    events: list[RunEvent] = Field(min_length=1)
    inputs_sanitized: dict[str, Any]
    outputs_sanitized: dict[str, Any]
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    resource_usage: ResourceUsage
    scores: list[MetricScore]
    aggregate_score: float | None = Field(default=None, ge=0, le=1)
    status: RunStatus
    failure_reasons: list[str] = Field(default_factory=list)
    created_at: datetime
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

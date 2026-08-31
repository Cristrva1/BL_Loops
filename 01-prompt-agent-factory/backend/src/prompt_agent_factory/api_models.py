"""Modelos de entrada y salida de la API educativa."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, field_validator

from .contracts import Artifact, ArtifactType, FlowStatus, OutputFormat, StrictModel


def _unique_text(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = value.strip()
        key = clean.casefold()
        if clean and key not in seen:
            result.append(clean)
            seen.add(key)
    return result


class FactoryIntake(StrictModel):
    """Briefing humano que la fábrica convierte en un contrato."""

    artifact_type: ArtifactType
    idea: str = Field(min_length=15, max_length=2000)
    title: str | None = Field(default=None, min_length=3, max_length=160)
    audience: str | None = Field(default=None, min_length=3, max_length=300)
    context: str | None = Field(default=None, min_length=10, max_length=2000)
    input_name: str | None = Field(
        default=None,
        pattern=r"^[a-z][a-z0-9_]*$",
        max_length=80,
    )
    output_format: OutputFormat | None = None
    success_criteria: list[str] = Field(default_factory=list, max_length=20)
    constraints: list[str] = Field(default_factory=list, max_length=20)
    source_refs: list[str] = Field(default_factory=list, max_length=30)
    allowed_tools: list[str] = Field(default_factory=list, max_length=20)
    tools_confirmed: bool = False
    requires_human_approval: bool = True

    @field_validator("success_criteria", "constraints", "source_refs", "allowed_tools")
    @classmethod
    def normalize_lists(cls, value: list[str]) -> list[str]:
        return _unique_text(value)


class GuidedQuestion(StrictModel):
    question_id: str = Field(pattern=r"^q_[a-z0-9_]+$")
    field: str
    prompt: str
    why: str
    example: str
    required: bool = True


class FlowEvent(StrictModel):
    sequence: int = Field(ge=1)
    node_id: Literal["capture", "clarify", "contract", "validate", "export"]
    status: FlowStatus
    title: str
    detail: str


class GuidanceResult(StrictModel):
    ready: bool
    readiness: float = Field(ge=0, le=1)
    completed_fields: list[str]
    required_fields: list[str]
    questions: list[GuidedQuestion]
    events: list[FlowEvent]


class FactoryResult(StrictModel):
    artifact: Artifact
    events: list[FlowEvent]
    explanation: list[str]


class ExportRequest(StrictModel):
    artifact: Artifact


class ExportResult(StrictModel):
    artifact_id: str
    relative_path: str
    content_hash: str
    events: list[FlowEvent]


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    lab: Literal["01-prompt-agent-factory"] = "01-prompt-agent-factory"
    version: str
    phase: Literal["part-1-contracts"] = "part-1-contracts"
    llm_used: Literal[False] = False
    local_ollama_configured: bool
    configuration_scope: Literal["lab", "workspace", "defaults"]


class LessonStage(StrictModel):
    number: int
    name: str
    question: str
    output: str


class LessonResponse(StrictModel):
    title: str
    learning_goal: str
    stages: list[LessonStage]
    glossary: dict[str, str]
    deferred: list[str]


class ContractSchemaResponse(StrictModel):
    name: Literal["prompt", "agent", "skill", "run"]
    description: str
    schema_: dict[str, Any] = Field(serialization_alias="schema")

"""Contratos HTTP del dashboard y de la API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .contracts import ComparisonView, NodeView, StrictModel, VariantView


class ExperimentIntake(StrictModel):
    task: str = Field(min_length=20, max_length=4000)
    include_baseline: bool = True
    include_orchestrated: bool = True


class StartRunResponse(StrictModel):
    run_id: str
    status: Literal["queued", "running"]
    case_id: str


class RunSnapshotResponse(StrictModel):
    run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    case_id: str
    model: str
    include_baseline: bool
    include_orchestrated: bool
    nodes: list[NodeView]
    event_count: int
    baseline: VariantView | None = None
    orchestrated: VariantView | None = None
    comparison: ComparisonView | None = None
    jsonl_path: str | None = None
    error: str | None = None


class HealthResponse(StrictModel):
    version: str
    lab_id: Literal["03-orchestration"]
    model: str
    local_ollama_configured: bool
    llm_used: bool = True
    phase: str
    configuration_scope: str


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


class ExampleResponse(StrictModel):
    case_id: str
    title: str
    task: str
    include_baseline: bool = True
    include_orchestrated: bool = True


class StreamEnvelope(StrictModel):
    event: dict[str, Any]
    snapshot: RunSnapshotResponse

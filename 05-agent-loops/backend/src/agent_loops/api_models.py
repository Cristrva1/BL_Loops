"""Contratos HTTP del dashboard y de la API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .contracts import CandidateView, IterationView, LoopDeclaration, NodeView, StrictModel
from .prompts import INITIAL_PROMPT


class LoopIntake(StrictModel):
    task: str = Field(min_length=20, max_length=4000)
    initial_prompt: str = Field(default=INITIAL_PROMPT, min_length=8, max_length=4000)


class StartRunResponse(StrictModel):
    run_id: str
    status: Literal["queued", "running"]
    case_id: str


class RunSnapshotResponse(StrictModel):
    run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    case_id: str
    model: str
    nodes: list[NodeView]
    event_count: int
    declaration: LoopDeclaration | None = None
    iterations: list[IterationView] = Field(default_factory=list)
    best: CandidateView | None = None
    stop_reason: str | None = None
    jsonl_path: str | None = None
    error: str | None = None


class HealthResponse(StrictModel):
    version: str
    lab_id: Literal["05-agent-loops"]
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
    initial_prompt: str
    budget: dict[str, Any]


class StreamEnvelope(StrictModel):
    event: dict[str, Any]
    snapshot: RunSnapshotResponse

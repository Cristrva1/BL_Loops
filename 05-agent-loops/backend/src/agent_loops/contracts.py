"""Contratos del loop: presupuesto, candidato, declaracion y reescritura."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PromptRewrite(StrictModel):
    prompt: str = Field(min_length=8, max_length=4000)
    rationale: str = Field(default="", max_length=400)


class BudgetView(StrictModel):
    max_iterations: int = Field(ge=1, le=20)
    max_errors: int = Field(ge=1, le=10)
    timeout_seconds: float = Field(gt=0, le=1800)
    threshold: int = Field(ge=1, le=5)


class CheckView(StrictModel):
    check_id: str
    title: str
    passed: bool
    evidence: str


class NodeView(StrictModel):
    id: str
    title: str
    state: Literal["idle", "queued", "running", "waiting", "retrying", "done", "failed", "blocked"]
    detail: str = ""


class CandidateView(StrictModel):
    iteration: int
    checks_passed: int
    checks_total: int
    passed: bool
    is_best: bool = False
    prompt_chars: int
    output_chars: int
    preview: str = ""
    checks: list[CheckView] = Field(default_factory=list)


class IterationView(StrictModel):
    iteration: int
    checks_passed: int
    checks_total: int
    passed: bool
    is_best: bool
    prompt_chars: int
    output_chars: int
    failed_checks: list[str] = Field(default_factory=list)
    error: str | None = None


class LoopDeclaration(StrictModel):
    objective: str
    initial_score: int | None = None
    best_known_score: int | None = None
    budget: BudgetView
    improvement_condition: str
    stop_condition: str
    stop_reason: str | None = None

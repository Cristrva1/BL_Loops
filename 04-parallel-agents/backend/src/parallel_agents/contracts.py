"""Contratos de extraccion, union y comparacion."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Fact(StrictModel):
    fact_id: str = Field(min_length=3, max_length=40)
    topic: str = Field(min_length=2, max_length=80)
    value: str = Field(min_length=1, max_length=120)
    evidence: str = Field(min_length=3, max_length=240)

    @field_validator("fact_id", mode="before")
    @classmethod
    def slugify_fact_id(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        slug = value.strip().casefold().replace(" ", "_")
        return slug[:40] or "fact"


class FactBundle(StrictModel):
    source_id: str = Field(pattern=r"^source-[abc]$")
    facts: list[Fact] = Field(min_length=1, max_length=8)


class NodeView(StrictModel):
    id: str
    title: str
    state: Literal["idle", "queued", "running", "waiting", "retrying", "done", "failed", "blocked"]
    detail: str = ""


class CheckView(StrictModel):
    check_id: str
    title: str
    passed: bool
    evidence: str


class FactRowView(StrictModel):
    fact_id: str
    topic: str
    value: str
    source_id: str
    evidence: str = ""


class BranchView(StrictModel):
    source_id: str
    node_id: str
    title: str
    status: Literal["completed", "failed", "timeout"]
    fact_ids: list[str] = Field(default_factory=list)
    facts: list[FactRowView] = Field(default_factory=list)
    latency_ms: float | None = None
    error: str | None = None


class TableView(StrictModel):
    rows: list[FactRowView] = Field(default_factory=list)
    completed_sources: list[str] = Field(default_factory=list)
    failed_sources: list[str] = Field(default_factory=list)
    preview: str = ""


class LaneView(StrictModel):
    status: Literal["idle", "running", "passed", "failed"]
    passed: bool | None = None
    wall_ms: float | None = None
    overlap_observed: bool = False
    max_in_flight: int | None = None
    completed_sources: list[str] = Field(default_factory=list)
    failed_sources: list[str] = Field(default_factory=list)
    fact_count: int = 0
    preview: str = ""
    checks: list[CheckView] = Field(default_factory=list)
    branches: list[BranchView] = Field(default_factory=list)
    table: TableView | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None


class ComparisonView(StrictModel):
    winner: Literal["sequential", "parallel", "tie", "incomplete"]
    sequential_passed: bool | None = None
    parallel_passed: bool | None = None
    sequential_ms: float | None = None
    parallel_ms: float | None = None
    speedup: float | None = None
    completed_delta: int | None = None
    overlap_observed: bool = False
    explanation: list[str] = Field(default_factory=list)

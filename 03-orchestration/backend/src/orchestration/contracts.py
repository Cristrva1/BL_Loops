"""Contratos de handoff entre agentes especializados."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PlanSection(StrictModel):
    section_id: str = Field(min_length=1, max_length=40)
    heading: str = Field(min_length=3, max_length=80)
    must_include: list[str] = Field(min_length=1, max_length=6)

    @model_validator(mode="before")
    @classmethod
    def default_section_id(cls, value: object) -> object:
        if isinstance(value, dict) and not value.get("section_id") and value.get("heading"):
            updated = dict(value)
            updated["section_id"] = str(value["heading"])
            return updated
        return value

    @field_validator("section_id", mode="before")
    @classmethod
    def slugify_section_id(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        slug = re.sub(r"[^a-z0-9_]+", "_", value.strip().casefold()).strip("_")
        return slug[:40] or "section"


class Plan(StrictModel):
    title: str = Field(min_length=4, max_length=160)
    audience: str = Field(min_length=4, max_length=200)
    outline: list[PlanSection] = Field(min_length=3, max_length=8)
    success_checks: list[str] = Field(min_length=3, max_length=8)


class ReviewCheck(StrictModel):
    check_id: str = Field(min_length=3, max_length=60)
    passed: bool
    evidence: str = Field(min_length=3, max_length=240)


class Review(StrictModel):
    passed: bool
    checks: list[ReviewCheck] = Field(min_length=1, max_length=12)
    required_changes: list[str] = Field(default_factory=list, max_length=8)


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


class VariantView(StrictModel):
    status: Literal["idle", "running", "passed", "failed"]
    word_count: int | None = None
    checks_passed: int | None = None
    checks_total: int | None = None
    passed: bool | None = None
    revision_used: bool = False
    headings: list[str] = Field(default_factory=list)
    preview: str = ""
    latency_ms: float | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    checks: list[CheckView] = Field(default_factory=list)
    llm_review_passed: bool | None = None
    llm_review_available: bool = False


class ComparisonView(StrictModel):
    winner: Literal["baseline", "orchestrated", "tie", "incomplete"]
    baseline_passed: bool | None = None
    orchestrated_passed: bool | None = None
    check_delta: int | None = None
    latency_delta_ms: float | None = None
    explanation: list[str] = Field(default_factory=list)

"""Checks deterministas del caso I-PARALLEL-002."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import BranchView, CheckView, FactBundle, FactRowView, LaneView, TableView
from .sources import SourceDoc


@dataclass(frozen=True, slots=True)
class ScoreResult:
    passed: bool
    checks: tuple[CheckView, ...]

    @property
    def checks_passed(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def checks_total(self) -> int:
        return len(self.checks)


def preview_text(text: str, limit: int = 200) -> str:
    compact = re.sub(r"\s+", " ", text.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def render_table(rows: list[FactRowView]) -> str:
    lines = [
        "| fact_id | topic | value | source_id |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row.fact_id} | {row.topic} | {row.value} | {row.source_id} |")
    if len(rows) == 0:
        lines.append("| — | — | — | — |")
    return "\n".join(lines)


def join_branches(branches: list[BranchView]) -> TableView:
    rows: list[FactRowView] = []
    completed: list[str] = []
    failed: list[str] = []
    for branch in branches:
        if branch.status == "completed":
            completed.append(branch.source_id)
            rows.extend(branch.facts)
        else:
            failed.append(branch.source_id)
    markdown = render_table(rows)
    return TableView(
        rows=rows,
        completed_sources=completed,
        failed_sources=failed,
        preview=preview_text(markdown),
    )


def score_bundle(source: SourceDoc, bundle: FactBundle) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if bundle.source_id != source.source_id:
        missing.append(f"source_id esperado {source.source_id}")
        return False, missing
    by_id = {fact.fact_id: fact for fact in bundle.facts}
    for required in source.required_facts:
        fact = by_id.get(required.fact_id)
        if fact is None:
            missing.append(required.fact_id)
            continue
        haystack = fact.value.casefold()
        needle = required.expected_contains.casefold()
        if needle not in haystack and needle.replace(":", "") not in haystack.replace(":", ""):
            missing.append(f"{required.fact_id}!={required.expected_contains}")
    return len(missing) == 0, missing


def score_lane(sources: tuple[SourceDoc, ...], lane: LaneView) -> ScoreResult:
    source_by_id = {source.source_id: source for source in sources}
    branches = {branch.source_id: branch for branch in lane.branches}
    table = lane.table or TableView()
    checks: list[CheckView] = []

    dispatched = len(lane.branches) == len(sources)
    checks.append(
        CheckView(
            check_id="three_branches",
            title="Tres ramas con procedencia propia",
            passed=dispatched,
            evidence=f"{len(lane.branches)} ramas." if dispatched else "No hay tres ramas.",
        )
    )

    provenance_ok = all(row.source_id for row in table.rows)
    checks.append(
        CheckView(
            check_id="provenance",
            title="Cada fila conserva su fuente",
            passed=provenance_ok,
            evidence="Todas las filas tienen source_id."
            if provenance_ok
            else "Hay filas sin procedencia.",
        )
    )

    leaked = [
        source_id
        for source_id in table.failed_sources
        if source_id in table.completed_sources
    ]
    failed_rows = [row.source_id for row in table.rows if row.source_id in table.failed_sources]
    failed_clean = not leaked and not failed_rows
    checks.append(
        CheckView(
            check_id="failed_not_complete",
            title="Una rama fallida no se presenta como completa",
            passed=failed_clean,
            evidence="Las fallidas quedan fuera de la tabla."
            if failed_clean
            else f"Fugas: {leaked or failed_rows}.",
        )
    )

    required_ok = True
    missing_required: list[str] = []
    for source_id in table.completed_sources:
        source = source_by_id.get(source_id)
        branch = branches.get(source_id)
        if source is None or branch is None:
            required_ok = False
            missing_required.append(source_id)
            continue
        present = {fact.fact_id: fact.value for fact in branch.facts}
        for required in source.required_facts:
            value = present.get(required.fact_id, "").casefold()
            needle = required.expected_contains.casefold()
            if needle not in value and needle.replace(":", "") not in value.replace(":", ""):
                required_ok = False
                missing_required.append(required.fact_id)
    checks.append(
        CheckView(
            check_id="required_facts",
            title="Las ramas completas conservan los hechos exigidos",
            passed=required_ok,
            evidence="Hechos exigidos presentes."
            if required_ok
            else f"Faltan: {', '.join(missing_required) or 'desconocido'}.",
        )
    )

    timed = lane.wall_ms is not None and lane.wall_ms >= 0
    checks.append(
        CheckView(
            check_id="time_measured",
            title="La variante registra su tiempo de pared",
            passed=timed,
            evidence=f"{lane.wall_ms} ms" if timed else "Sin wall_ms.",
        )
    )

    explicit_status = all(
        branch.status in {"completed", "failed", "timeout"} for branch in lane.branches
    )
    checks.append(
        CheckView(
            check_id="explicit_status",
            title="Cada rama termina en completed, failed o timeout",
            passed=explicit_status and len(lane.branches) > 0,
            evidence="Estados explicitos." if explicit_status else "Hay ramas sin estado terminal.",
        )
    )

    return ScoreResult(passed=all(check.passed for check in checks), checks=tuple(checks))

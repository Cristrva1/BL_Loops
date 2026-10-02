"""Orquestador secuencial propio: planificador, autor, revisor y linea base."""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .config import Settings
from .contracts import ComparisonView, Plan, Review, VariantView
from .json_parse import JsonParseError, extract_json_object
from .ollama_client import ChatResult, OllamaClient, OllamaError
from .prompts import (
    AUTHOR_SYSTEM,
    BASELINE_SYSTEM,
    CASE_ID,
    PLANNER_SYSTEM,
    REVIEWER_SYSTEM,
    REVISER_SYSTEM,
    author_user,
    baseline_user,
    planner_user,
    reviewer_user,
    reviser_user,
)
from .run_log import RunLogger
from .scoring import ScoreResult, preview_text, score_guide

GRAPH_NODES: tuple[tuple[str, str], ...] = (
    ("intake", "Tarea"),
    ("baseline", "Agente único"),
    ("planner", "Planificador"),
    ("author", "Autor"),
    ("reviewer", "Revisor"),
    ("reviser", "Corrección"),
    ("score", "Comparación"),
)


class OrchestrationError(RuntimeError):
    """Fallo de un nodo que no es un error de transporte con Ollama."""


@dataclass(frozen=True, slots=True)
class ExperimentRequest:
    task: str
    include_baseline: bool = True
    include_orchestrated: bool = True


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    run_id: str
    status: str
    case_id: str
    model: str
    jsonl_path: Path
    baseline: VariantView | None
    orchestrated: VariantView | None
    comparison: ComparisonView | None
    error: str | None


def variant_id_for(request: ExperimentRequest) -> str:
    if request.include_baseline and request.include_orchestrated:
        return "baseline-and-orchestrated"
    if request.include_orchestrated:
        return "orchestrated"
    return "baseline"


def run_experiment(
    request: ExperimentRequest,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
) -> ExperimentResult:
    task = request.task.strip()
    if len(task) < 20:
        raise OrchestrationError("La tarea debe tener al menos 20 caracteres.")
    if not request.include_baseline and not request.include_orchestrated:
        raise OrchestrationError("Selecciona al menos una variante: agente unico u orquestada.")

    logger.emit(
        "run.started",
        payload={
            "case_id": CASE_ID,
            "include_baseline": request.include_baseline,
            "include_orchestrated": request.include_orchestrated,
            "task_chars": len(task),
            "network_allowed": False,
        },
    )
    _run_node(logger, "intake", "input", "Captura la tarea humana.", lambda: None)

    baseline_view: VariantView | None = None
    orchestrated_view: VariantView | None = None
    error: str | None = None

    try:
        if request.include_baseline:
            baseline_view = _run_baseline(task, settings, client, logger)
        else:
            logger.emit("node.skipped", node_id="baseline", node_type="agent", state="idle")

        if request.include_orchestrated:
            orchestrated_view = _run_orchestrated(task, settings, client, logger)
        else:
            for node_id in ("planner", "author", "reviewer", "reviser"):
                logger.emit("node.skipped", node_id=node_id, node_type="agent", state="idle")
    except OllamaError as exc:
        error = str(exc)
        logger.finish(status="failed", reason=error)
        return ExperimentResult(
            run_id=logger.run_id,
            status="failed",
            case_id=CASE_ID,
            model=settings.model,
            jsonl_path=logger.path,
            baseline=baseline_view,
            orchestrated=orchestrated_view,
            comparison=None,
            error=error,
        )

    comparison = compare_variants(baseline_view, orchestrated_view)
    _run_node(
        logger,
        "score",
        "evaluator",
        "Compara las variantes con la misma lista.",
        lambda: None,
        payload=comparison.model_dump(mode="json"),
    )

    status = "completed"
    reason = "Comparacion determinista lista."
    if baseline_view is None and orchestrated_view is None:
        status = "failed"
        reason = "Ninguna variante produjo una guia puntuable."

    logger.finish(status=status, reason=reason)
    return ExperimentResult(
        run_id=logger.run_id,
        status=status,
        case_id=CASE_ID,
        model=settings.model,
        jsonl_path=logger.path,
        baseline=baseline_view,
        orchestrated=orchestrated_view,
        comparison=comparison,
        error=error,
    )


def compare_variants(
    baseline: VariantView | None,
    orchestrated: VariantView | None,
) -> ComparisonView:
    if baseline is None and orchestrated is None:
        return ComparisonView(
            winner="incomplete",
            explanation=["No hay variantes para comparar."],
        )
    if baseline is None:
        winner = "orchestrated" if orchestrated and orchestrated.passed else "incomplete"
        return ComparisonView(
            winner=winner,
            orchestrated_passed=None if orchestrated is None else orchestrated.passed,
            explanation=[
                "Solo se ejecuto la variante orquestada. Sin linea base no se afirma una mejora.",
            ],
        )
    if orchestrated is None:
        winner = "baseline" if baseline.passed else "incomplete"
        return ComparisonView(
            winner=winner,
            baseline_passed=baseline.passed,
            explanation=["Solo se ejecuto el agente unico."],
        )

    check_delta = None
    if baseline.checks_passed is not None and orchestrated.checks_passed is not None:
        check_delta = orchestrated.checks_passed - baseline.checks_passed
    latency_delta = None
    if baseline.latency_ms is not None and orchestrated.latency_ms is not None:
        latency_delta = round(orchestrated.latency_ms - baseline.latency_ms, 1)

    if orchestrated.passed and not baseline.passed:
        winner = "orchestrated"
    elif baseline.passed and not orchestrated.passed:
        winner = "baseline"
    elif (orchestrated.checks_passed or 0) > (baseline.checks_passed or 0):
        winner = "orchestrated"
    elif (baseline.checks_passed or 0) > (orchestrated.checks_passed or 0):
        winner = "baseline"
    else:
        winner = "tie"

    explanation = [
        (
            f"Agente unico: {baseline.checks_passed}/{baseline.checks_total} checks, "
            f"passed={baseline.passed}."
        ),
        (
            f"Orquestada: {orchestrated.checks_passed}/{orchestrated.checks_total} checks, "
            f"passed={orchestrated.passed}, correccion={orchestrated.revision_used}."
        ),
        "El ganador se decide por la lista determinista, no por estilo ni por el modelo revisor.",
    ]
    return ComparisonView(
        winner=winner,
        baseline_passed=baseline.passed,
        orchestrated_passed=orchestrated.passed,
        check_delta=check_delta,
        latency_delta_ms=latency_delta,
        explanation=explanation,
    )


def _run_baseline(
    task: str,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
) -> VariantView:
    started = time.perf_counter()
    tokens = {"prompt": 0, "output": 0}

    def work() -> VariantView:
        result = _chat(
            client,
            logger,
            "baseline",
            [
                {"role": "system", "content": BASELINE_SYSTEM},
                {"role": "user", "content": baseline_user(task)},
            ],
            tokens,
        )
        markdown = result.content
        score = score_guide(markdown)
        path = _write_artifact(settings, logger, "baseline.md", markdown)
        return _variant_from_score(
            score,
            status="passed" if score.passed else "failed",
            revision_used=False,
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
            tokens=tokens,
            preview=preview_text(markdown),
            artifact=path,
        )

    return _run_node(logger, "baseline", "agent", "Un solo modelo escribe la guia.", work)


def _run_orchestrated(
    task: str,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
) -> VariantView:
    started = time.perf_counter()
    tokens = {"prompt": 0, "output": 0}
    revision_used = False

    def plan_work() -> Plan:
        result = _chat(
            client,
            logger,
            "planner",
            [
                {"role": "system", "content": PLANNER_SYSTEM},
                {"role": "user", "content": planner_user(task)},
            ],
            tokens,
            response_format="json",
        )
        try:
            plan = Plan.model_validate(extract_json_object(result.content))
        except (JsonParseError, ValidationError) as exc:
            raise OrchestrationError(
                "El planificador no devolvio un Plan JSON valido."
            ) from exc
        logger.emit(
            "handoff.recorded",
            node_id="planner",
            node_type="agent",
            state="done",
            payload={
                "title": plan.title,
                "headings": [section.heading for section in plan.outline],
                "success_checks": plan.success_checks,
            },
        )
        return plan

    try:
        plan = _run_node(logger, "planner", "agent", "Separa la tarea en secciones.", plan_work)
    except OrchestrationError:
        return _failed_variant("El planificador no produjo un handoff valido.", started, tokens)

    plan_json = plan.model_dump_json()

    def author_work() -> str:
        result = _chat(
            client,
            logger,
            "author",
            [
                {"role": "system", "content": AUTHOR_SYSTEM},
                {"role": "user", "content": author_user(task, plan_json)},
            ],
            tokens,
        )
        markdown = result.content
        if len(markdown) < 40:
            raise OrchestrationError("El autor devolvio un Markdown demasiado corto.")
        draft_score = score_guide(markdown)
        logger.emit(
            "handoff.recorded",
            node_id="author",
            node_type="agent",
            state="done",
            payload={
                "headings": list(draft_score.headings),
                "word_count": draft_score.word_count,
                "preview": preview_text(markdown),
            },
        )
        return markdown

    try:
        markdown = _run_node(
            logger,
            "author",
            "agent",
            "Escribe la guia a partir del plan.",
            author_work,
        )
    except OrchestrationError as exc:
        return _failed_variant(str(exc), started, tokens)

    score = score_guide(markdown)
    llm_review: Review | None = None

    def reviewer_work() -> Review | None:
        check_ids = [check.check_id for check in score.checks]
        result = _chat(
            client,
            logger,
            "reviewer",
            [
                {"role": "system", "content": REVIEWER_SYSTEM},
                {"role": "user", "content": reviewer_user(markdown, check_ids)},
            ],
            tokens,
            response_format="json",
        )
        try:
            review = Review.model_validate(extract_json_object(result.content))
        except (JsonParseError, ValidationError):
            logger.emit(
                "handoff.recorded",
                node_id="reviewer",
                node_type="agent",
                state="done",
                payload={
                    "llm_review_available": False,
                    "deterministic_passed": score.passed,
                    "failed_checks": score.failed_ids(),
                },
            )
            return None
        logger.emit(
            "handoff.recorded",
            node_id="reviewer",
            node_type="agent",
            state="done",
            payload={
                "llm_review_available": True,
                "llm_review_passed": review.passed,
                "deterministic_passed": score.passed,
                "required_changes": review.required_changes,
                "failed_checks": score.failed_ids(),
            },
        )
        return review

    llm_review = _run_node(
        logger,
        "reviewer",
        "agent",
        "El modelo opina; el gate es la lista determinista.",
        reviewer_work,
    )

    if not score.passed:
        revision_used = True

        def reviser_work() -> str:
            changes = score.failed_ids()
            if llm_review is not None:
                changes = llm_review.required_changes or changes
            result = _chat(
                client,
                logger,
                "reviser",
                [
                    {"role": "system", "content": REVISER_SYSTEM},
                    {"role": "user", "content": reviser_user(markdown, changes)},
                ],
                tokens,
            )
            revised = result.content
            if len(revised) < 40:
                raise OrchestrationError("La correccion devolvio un Markdown demasiado corto.")
            return revised

        try:
            markdown = _run_node(
                logger,
                "reviser",
                "agent",
                "Una sola correccion si el gate determinista falla.",
                reviser_work,
            )
            score = score_guide(markdown)
        except OrchestrationError as exc:
            return _failed_variant(str(exc), started, tokens)
    else:
        logger.emit("node.skipped", node_id="reviser", node_type="agent", state="idle")

    path = _write_artifact(settings, logger, "orchestrated.md", markdown)
    return _variant_from_score(
        score,
        status="passed" if score.passed else "failed",
        revision_used=revision_used,
        latency_ms=round((time.perf_counter() - started) * 1000, 1),
        tokens=tokens,
        preview=preview_text(markdown),
        artifact=path,
        llm_review=llm_review,
    )


def _chat(
    client: OllamaClient,
    logger: RunLogger,
    node_id: str,
    messages: list[dict[str, str]],
    tokens: dict[str, int],
    *,
    response_format: str | None = None,
) -> ChatResult:
    logger.emit(
        "model.requested",
        node_id=node_id,
        node_type="model",
        state="waiting",
        payload={
            "message_count": len(messages),
            "raw_prompt_stored": False,
            "response_format": response_format,
        },
    )
    started = time.perf_counter()
    result = client.chat(messages, response_format=response_format)
    wall_ms = round((time.perf_counter() - started) * 1000, 1)
    if result.prompt_tokens:
        tokens["prompt"] += result.prompt_tokens
    if result.output_tokens:
        tokens["output"] += result.output_tokens
    logger.emit(
        "model.completed",
        node_id=node_id,
        node_type="model",
        state="running",
        payload={"content_chars": len(result.content), "raw_content_stored": False},
        metrics={
            "wall_duration_ms": wall_ms,
            "ollama_duration_ms": result.total_duration_ms,
            "prompt_tokens": result.prompt_tokens,
            "output_tokens": result.output_tokens,
        },
    )
    return result


def _run_node[T](
    logger: RunLogger,
    node_id: str,
    node_type: str,
    detail: str,
    work: Callable[[], T],
    payload: dict[str, Any] | None = None,
) -> T:
    logger.emit(
        "node.queued",
        node_id=node_id,
        node_type=node_type,
        state="queued",
        payload={"detail": detail},
    )
    logger.emit("node.started", node_id=node_id, node_type=node_type, state="running")
    try:
        result = work()
    except (OrchestrationError, OllamaError):
        logger.emit(
            "node.failed",
            node_id=node_id,
            node_type=node_type,
            state="failed",
            payload={"detail": detail},
        )
        raise
    logger.emit(
        "node.completed",
        node_id=node_id,
        node_type=node_type,
        state="done",
        payload=payload or {"detail": detail},
    )
    return result


def _write_artifact(settings: Settings, logger: RunLogger, filename: str, content: str) -> Path:
    folder = settings.artifacts_dir / logger.run_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_text(content, encoding="utf-8")
    relative = path.resolve().relative_to(settings.root.resolve()).as_posix()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    logger.emit(
        "artifact.written",
        payload={"filename": filename, "sha256": digest, "bytes": len(content.encode("utf-8"))},
        artifact_refs=[relative],
    )
    return path


def _variant_from_score(
    score: ScoreResult,
    *,
    status: str,
    revision_used: bool,
    latency_ms: float,
    tokens: dict[str, int],
    preview: str,
    artifact: Path,
    llm_review: Review | None = None,
) -> VariantView:
    _ = artifact
    return VariantView(
        status="passed" if status == "passed" else "failed",
        word_count=score.word_count,
        checks_passed=score.checks_passed,
        checks_total=score.checks_total,
        passed=score.passed,
        revision_used=revision_used,
        headings=list(score.headings),
        preview=preview,
        latency_ms=latency_ms,
        prompt_tokens=tokens["prompt"] or None,
        output_tokens=tokens["output"] or None,
        checks=list(score.checks),
        llm_review_passed=None if llm_review is None else llm_review.passed,
        llm_review_available=llm_review is not None,
    )


def _failed_variant(reason: str, started: float, tokens: dict[str, int]) -> VariantView:
    return VariantView(
        status="failed",
        passed=False,
        revision_used=False,
        preview=reason,
        latency_ms=round((time.perf_counter() - started) * 1000, 1),
        prompt_tokens=tokens["prompt"] or None,
        output_tokens=tokens["output"] or None,
    )

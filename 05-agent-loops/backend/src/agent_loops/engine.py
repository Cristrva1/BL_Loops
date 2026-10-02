"""Loop tipado: generar, puntuar, decidir, mejorar, conservar el mejor."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .config import Settings
from .contracts import (
    BudgetView,
    CandidateView,
    IterationView,
    LoopDeclaration,
    PromptRewrite,
)
from .json_parse import JsonParseError, extract_json_object
from .ollama_client import ChatResult, OllamaClient, OllamaError
from .prompts import (
    CASE_ID,
    GENERATOR_FALLBACK_SYSTEM,
    IMPROVEMENT_CONDITION,
    IMPROVER_SYSTEM,
    INITIAL_PROMPT,
    OBJECTIVE,
    STOP_CONDITION,
    generator_user,
    improver_user,
)
from .run_log import RunLogger
from .scoring import ScoreResult, preview_text, score_output

GRAPH_NODES: tuple[tuple[str, str], ...] = (
    ("intake", "Tarea y presupuesto"),
    ("generate", "Generar"),
    ("score", "Puntuar"),
    ("decide", "Decidir"),
    ("improve", "Mejorar prompt"),
    ("best", "Mejor candidato"),
)

NowFn = Callable[[], float]


class LoopError(RuntimeError):
    """Fallo de un nodo que no es un error de transporte con Ollama."""


@dataclass(frozen=True, slots=True)
class Budget:
    max_iterations: int = 5
    max_errors: int = 2
    timeout_seconds: float = 180.0
    threshold: int = 5

    def as_view(self) -> BudgetView:
        return BudgetView(
            max_iterations=self.max_iterations,
            max_errors=self.max_errors,
            timeout_seconds=self.timeout_seconds,
            threshold=self.threshold,
        )


@dataclass(frozen=True, slots=True)
class LoopRequest:
    task: str
    initial_prompt: str = INITIAL_PROMPT
    budget: Budget = Budget()


@dataclass
class InternalCandidate:
    iteration: int
    prompt: str
    output: str
    score: ScoreResult


@dataclass(frozen=True, slots=True)
class LoopResult:
    run_id: str
    status: str
    case_id: str
    model: str
    stop_reason: str | None
    declaration: LoopDeclaration
    iterations: tuple[IterationView, ...]
    best: CandidateView | None
    jsonl_path: Path
    error: str | None


def run_loop(
    request: LoopRequest,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
    now: NowFn | None = None,
) -> LoopResult:
    clock = now or time.monotonic
    task = request.task.strip()
    if len(task) < 20:
        raise LoopError("La tarea debe tener al menos 20 caracteres.")
    prompt = request.initial_prompt.strip() or INITIAL_PROMPT
    if len(prompt) < 8:
        raise LoopError("El prompt inicial debe tener al menos 8 caracteres.")

    budget = request.budget
    started = clock()
    errors = 0
    tokens = {"prompt": 0, "output": 0}
    best: InternalCandidate | None = None
    history: list[IterationView] = []
    initial_score: int | None = None
    stop_reason: str | None = None
    error: str | None = None

    logger.emit(
        "run.started",
        payload={
            "case_id": CASE_ID,
            "task_chars": len(task),
            "prompt_chars": len(prompt),
            "network_allowed": False,
            "budget": budget.as_view().model_dump(mode="json"),
            "objective": OBJECTIVE,
            "improvement_condition": IMPROVEMENT_CONDITION,
            "stop_condition": STOP_CONDITION,
        },
    )
    _run_node(
        logger,
        "intake",
        "input",
        "Declara objetivo, presupuesto y condicion de parada.",
        lambda: None,
        payload={
            "detail": "Declara objetivo, presupuesto y condicion de parada.",
            "max_iterations": budget.max_iterations,
            "max_errors": budget.max_errors,
            "timeout_seconds": budget.timeout_seconds,
            "threshold": budget.threshold,
        },
    )

    try:
        for iteration in range(1, budget.max_iterations + 1):
            if clock() - started >= budget.timeout_seconds:
                stop_reason = "timeout"
                _complete_node(logger, "decide", "evaluator", "Presupuesto de tiempo agotado.")
                break

            output = ""
            iteration_error: str | None = None

            current_prompt = prompt

            def generate_work(bound_prompt: str = current_prompt) -> str:
                result = _chat(
                    client,
                    logger,
                    "generate",
                    [
                        {
                            "role": "system",
                            "content": bound_prompt or GENERATOR_FALLBACK_SYSTEM,
                        },
                        {"role": "user", "content": generator_user(task)},
                    ],
                    tokens,
                )
                return result.content

            try:
                output = _run_node(
                    logger,
                    "generate",
                    "agent",
                    f"Iteracion {iteration}: el prompt actual produce una salida.",
                    generate_work,
                )
            except (OllamaError, LoopError) as exc:
                errors += 1
                iteration_error = str(exc)
                output = ""

            score = score_output(output)
            if initial_score is None:
                initial_score = score.checks_passed

            candidate = InternalCandidate(
                iteration=iteration,
                prompt=prompt,
                output=output,
                score=score,
            )
            replaced = best is None or score.checks_passed > best.score.checks_passed
            if replaced:
                best = candidate

            _run_node(
                logger,
                "score",
                "evaluator",
                f"{score.checks_passed}/{score.checks_total} checks en la iteracion {iteration}.",
                lambda: None,
                payload={
                    "detail": (
                        f"{score.checks_passed}/{score.checks_total} checks "
                        f"en la iteracion {iteration}."
                    ),
                    "iteration": iteration,
                    "checks_passed": score.checks_passed,
                    "checks_total": score.checks_total,
                    "failed_checks": score.failed_ids(),
                    "initial_score": initial_score,
                },
            )

            if replaced and best is not None:
                _run_node(
                    logger,
                    "best",
                    "memory",
                    f"Nuevo mejor candidato: {best.score.checks_passed}/{best.score.checks_total}.",
                    lambda: None,
                    payload={
                        "detail": (
                            f"Nuevo mejor candidato: "
                            f"{best.score.checks_passed}/{best.score.checks_total}."
                        ),
                        "iteration": best.iteration,
                        "checks_passed": best.score.checks_passed,
                        "checks_total": best.score.checks_total,
                    },
                )

            history.append(
                IterationView(
                    iteration=iteration,
                    checks_passed=score.checks_passed,
                    checks_total=score.checks_total,
                    passed=score.passed,
                    is_best=replaced,
                    prompt_chars=len(prompt),
                    output_chars=len(output),
                    failed_checks=score.failed_ids(),
                    error=iteration_error,
                )
            )
            logger.emit(
                "iteration.recorded",
                node_id="score",
                node_type="evaluator",
                state="done",
                payload={
                    "iteration": iteration,
                    "checks_passed": score.checks_passed,
                    "checks_total": score.checks_total,
                    "passed": score.passed,
                    "is_best": replaced,
                    "prompt_chars": len(prompt),
                    "output_chars": len(output),
                    "failed_checks": score.failed_ids(),
                    "error": iteration_error,
                },
            )

            if score.passed or score.checks_passed >= budget.threshold:
                stop_reason = "threshold_reached"
                _complete_node(
                    logger,
                    "decide",
                    "evaluator",
                    "El umbral se alcanzo. El loop se detiene.",
                )
                logger.emit("node.skipped", node_id="improve", node_type="agent", state="idle")
                break

            if errors >= budget.max_errors:
                stop_reason = "max_errors"
                _complete_node(
                    logger,
                    "decide",
                    "evaluator",
                    "Se agoto el presupuesto de errores.",
                )
                logger.emit("node.skipped", node_id="improve", node_type="agent", state="idle")
                break

            if iteration >= budget.max_iterations:
                stop_reason = "max_iterations"
                _complete_node(
                    logger,
                    "decide",
                    "evaluator",
                    "Se agoto el presupuesto de iteraciones.",
                )
                logger.emit("node.skipped", node_id="improve", node_type="agent", state="idle")
                break

            if clock() - started >= budget.timeout_seconds:
                stop_reason = "timeout"
                _complete_node(logger, "decide", "evaluator", "Presupuesto de tiempo agotado.")
                logger.emit("node.skipped", node_id="improve", node_type="agent", state="idle")
                break

            _complete_node(
                logger,
                "decide",
                "evaluator",
                "El umbral no se alcanzo. Se reescribe el prompt.",
            )

            failed_ids = tuple(score.failed_ids())
            prompt_to_improve = prompt

            def improve_work(
                bound_prompt: str = prompt_to_improve,
                bound_failed: tuple[str, ...] = failed_ids,
            ) -> str:
                result = _chat(
                    client,
                    logger,
                    "improve",
                    [
                        {"role": "system", "content": IMPROVER_SYSTEM},
                        {
                            "role": "user",
                            "content": improver_user(task, bound_prompt, list(bound_failed)),
                        },
                    ],
                    tokens,
                    response_format="json",
                )
                try:
                    rewrite = PromptRewrite.model_validate(extract_json_object(result.content))
                except (JsonParseError, ValidationError) as exc:
                    raise LoopError("El mejorador no devolvio un prompt JSON valido.") from exc
                return rewrite.prompt

            try:
                prompt = _run_node(
                    logger,
                    "improve",
                    "agent",
                    "El mejorador reescribe el prompt con los checks fallidos.",
                    improve_work,
                )
            except (OllamaError, LoopError) as exc:
                errors += 1
                error = str(exc)
                if errors >= budget.max_errors:
                    stop_reason = "max_errors"
                    break
    except OllamaError as exc:
        error = str(exc)
        logger.finish(status="failed", reason=error)
        return _result(
            logger,
            settings,
            budget,
            "failed",
            stop_reason,
            initial_score,
            history,
            best,
            error,
        )

    if stop_reason is None:
        stop_reason = "max_iterations"

    if best is not None:
        _write_artifact(settings, logger, "best-prompt.txt", best.prompt)
        _write_artifact(settings, logger, "best-output.txt", best.output)
    summary = {
        "stop_reason": stop_reason,
        "initial_score": initial_score,
        "best_known_score": None if best is None else best.score.checks_passed,
        "iterations": [item.model_dump(mode="json") for item in history],
    }
    _write_artifact(
        settings,
        logger,
        "summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    )

    status = "completed"
    reason = _reason_text(stop_reason)
    if best is None:
        status = "failed"
        reason = "Ninguna iteracion produjo una salida puntuable."
        error = error or reason

    logger.finish(status=status, reason=reason)
    return _result(
        logger,
        settings,
        budget,
        status,
        stop_reason,
        initial_score,
        history,
        best,
        error,
    )


def _result(
    logger: RunLogger,
    settings: Settings,
    budget: Budget,
    status: str,
    stop_reason: str | None,
    initial_score: int | None,
    history: list[IterationView],
    best: InternalCandidate | None,
    error: str | None,
) -> LoopResult:
    declaration = LoopDeclaration(
        objective=OBJECTIVE,
        initial_score=initial_score,
        best_known_score=None if best is None else best.score.checks_passed,
        budget=budget.as_view(),
        improvement_condition=IMPROVEMENT_CONDITION,
        stop_condition=STOP_CONDITION,
        stop_reason=stop_reason,
    )
    best_view = None if best is None else _candidate_view(best, is_best=True)
    marked: list[IterationView] = []
    for item in history:
        marked.append(
            item.model_copy(
                update={
                    "is_best": best is not None and item.iteration == best.iteration,
                }
            )
        )
    return LoopResult(
        run_id=logger.run_id,
        status=status,
        case_id=CASE_ID,
        model=settings.model,
        stop_reason=stop_reason,
        declaration=declaration,
        iterations=tuple(marked),
        best=best_view,
        jsonl_path=logger.path,
        error=error,
    )


def _candidate_view(candidate: InternalCandidate, *, is_best: bool) -> CandidateView:
    return CandidateView(
        iteration=candidate.iteration,
        checks_passed=candidate.score.checks_passed,
        checks_total=candidate.score.checks_total,
        passed=candidate.score.passed,
        is_best=is_best,
        prompt_chars=len(candidate.prompt),
        output_chars=len(candidate.output),
        preview=preview_text(candidate.output),
        checks=list(candidate.score.checks),
    )


def _reason_text(stop_reason: str) -> str:
    labels = {
        "threshold_reached": "El umbral de 5/5 se alcanzo.",
        "max_iterations": "Se agoto el presupuesto de iteraciones.",
        "max_errors": "Se agoto el presupuesto de errores.",
        "timeout": "Se agoto el presupuesto de tiempo.",
    }
    return labels.get(stop_reason, stop_reason)


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
        node_type=node_type_for(node_id),
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


def node_type_for(node_id: str) -> str:
    if node_id in {"score", "decide"}:
        return "evaluator"
    if node_id == "best":
        return "memory"
    if node_id == "intake":
        return "input"
    return "agent"


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
    except (LoopError, OllamaError):
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


def _complete_node(logger: RunLogger, node_id: str, node_type: str, detail: str) -> None:
    _run_node(logger, node_id, node_type, detail, lambda: None, payload={"detail": detail})


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

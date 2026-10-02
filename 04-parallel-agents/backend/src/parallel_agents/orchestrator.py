"""Fan-out/fan-in propio: extraccion secuencial frente a tres ramas concurrentes."""

from __future__ import annotations

import asyncio
import hashlib
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .config import Settings
from .contracts import (
    BranchView,
    ComparisonView,
    FactBundle,
    FactRowView,
    LaneView,
    TableView,
)
from .json_parse import JsonParseError, extract_json_object
from .ollama_client import ChatResult, OllamaClient, OllamaError
from .prompts import CASE_ID, EXTRACTOR_SYSTEM, extractor_user
from .run_log import RunLogger
from .scoring import join_branches, preview_text, render_table, score_bundle, score_lane
from .sources import SourceDoc, load_sources

GRAPH_NODES: tuple[tuple[str, str], ...] = (
    ("intake", "Tarea"),
    ("seq-a", "Secuencial A"),
    ("seq-b", "Secuencial B"),
    ("seq-c", "Secuencial C"),
    ("seq-join", "Unión secuencial"),
    ("par-a", "Paralelo A"),
    ("par-b", "Paralelo B"),
    ("par-c", "Paralelo C"),
    ("par-join", "Unión paralela"),
    ("compare", "Comparación"),
)

NODE_FOR: dict[str, dict[str, str]] = {
    "sequential": {"a": "seq-a", "b": "seq-b", "c": "seq-c", "join": "seq-join"},
    "parallel": {"a": "par-a", "b": "par-b", "c": "par-c", "join": "par-join"},
}


class ParallelError(RuntimeError):
    """Fallo de una rama que no es un error de transporte global."""


@dataclass(frozen=True, slots=True)
class ExperimentRequest:
    task: str
    include_sequential: bool = True
    include_parallel: bool = True


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    run_id: str
    status: str
    case_id: str
    model: str
    jsonl_path: Path
    sequential: LaneView | None
    parallel: LaneView | None
    comparison: ComparisonView | None
    error: str | None


@dataclass
class _CancelToken:
    cancelled: bool = False


@dataclass
class _TokenCounter:
    prompt: int = 0
    output: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add(self, prompt_tokens: int | None, output_tokens: int | None) -> None:
        with self._lock:
            if prompt_tokens:
                self.prompt += prompt_tokens
            if output_tokens:
                self.output += output_tokens


@dataclass
class _OverlapTracker:
    current: int = 0
    peak: int = 0

    def begin(self) -> None:
        self.current += 1
        self.peak = max(self.peak, self.current)

    def end(self) -> None:
        self.current = max(0, self.current - 1)


def variant_id_for(request: ExperimentRequest) -> str:
    if request.include_sequential and request.include_parallel:
        return "sequential-and-parallel"
    if request.include_parallel:
        return "parallel"
    return "sequential"


def run_experiment(
    request: ExperimentRequest,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
    sources: tuple[SourceDoc, ...] | None = None,
) -> ExperimentResult:
    task = request.task.strip()
    if len(task) < 20:
        raise ParallelError("La tarea debe tener al menos 20 caracteres.")
    if not request.include_sequential and not request.include_parallel:
        raise ParallelError("Selecciona al menos una variante: secuencial o paralela.")

    documents = sources or load_sources()
    logger.emit(
        "run.started",
        payload={
            "case_id": CASE_ID,
            "include_sequential": request.include_sequential,
            "include_parallel": request.include_parallel,
            "source_ids": [source.source_id for source in documents],
            "max_in_flight": settings.max_in_flight,
            "task_chars": len(task),
            "network_allowed": False,
        },
    )
    _run_node(logger, "intake", "input", "Captura la tarea y las tres fuentes.", lambda: None)

    sequential: LaneView | None = None
    parallel: LaneView | None = None
    error: str | None = None

    try:
        if request.include_sequential:
            sequential = _run_sequential(task, documents, settings, client, logger)
        else:
            for node_id in ("seq-a", "seq-b", "seq-c", "seq-join"):
                logger.emit("node.skipped", node_id=node_id, node_type="agent", state="idle")

        if request.include_parallel:
            parallel = _run_parallel(task, documents, settings, client, logger)
        else:
            for node_id in ("par-a", "par-b", "par-c", "par-join"):
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
            sequential=sequential,
            parallel=parallel,
            comparison=None,
            error=error,
        )

    comparison = compare_lanes(sequential, parallel)
    _run_node(
        logger,
        "compare",
        "evaluator",
        "Compara tiempo y coherencia de las dos variantes.",
        lambda: None,
        payload=comparison.model_dump(mode="json"),
    )

    status = "completed"
    reason = "Comparacion de fan-out/fan-in lista."
    if sequential is None and parallel is None:
        status = "failed"
        reason = "Ninguna variante produjo una tabla puntuable."

    logger.finish(status=status, reason=reason)
    return ExperimentResult(
        run_id=logger.run_id,
        status=status,
        case_id=CASE_ID,
        model=settings.model,
        jsonl_path=logger.path,
        sequential=sequential,
        parallel=parallel,
        comparison=comparison,
        error=error,
    )


def compare_lanes(
    sequential: LaneView | None,
    parallel: LaneView | None,
) -> ComparisonView:
    if sequential is None and parallel is None:
        return ComparisonView(
            winner="incomplete",
            explanation=["No hay variantes para comparar."],
        )
    if sequential is None:
        return ComparisonView(
            winner="incomplete" if parallel is None or not parallel.passed else "parallel",
            parallel_passed=None if parallel is None else parallel.passed,
            parallel_ms=None if parallel is None else parallel.wall_ms,
            overlap_observed=False if parallel is None else parallel.overlap_observed,
            explanation=[
                "Solo se ejecuto la variante paralela.",
                "Sin linea secuencial no se afirma un ahorro.",
            ],
        )
    if parallel is None:
        return ComparisonView(
            winner="incomplete" if not sequential.passed else "sequential",
            sequential_passed=sequential.passed,
            sequential_ms=sequential.wall_ms,
            explanation=["Solo se ejecuto la variante secuencial."],
        )

    completed_delta = len(parallel.completed_sources) - len(sequential.completed_sources)
    speedup = None
    if sequential.wall_ms and parallel.wall_ms and parallel.wall_ms > 0:
        speedup = round(sequential.wall_ms / parallel.wall_ms, 2)

    sequential_quality = len(sequential.completed_sources)
    parallel_quality = len(parallel.completed_sources)
    if parallel_quality < sequential_quality:
        winner = "sequential"
        quality_note = "El paralelo perdio hechos; el tiempo no justifica peor coherencia."
    elif sequential.passed and not parallel.passed:
        winner = "sequential"
        quality_note = "El gate secuencial aprobo y el paralelo no."
    elif parallel.passed and not sequential.passed:
        winner = "parallel"
        quality_note = "El gate paralelo aprobo y el secuencial no."
    elif sequential.wall_ms is None or parallel.wall_ms is None:
        winner = "tie"
        quality_note = "Falta una medicion de tiempo."
    else:
        ratio = parallel.wall_ms / sequential.wall_ms if sequential.wall_ms else 1
        if 0.95 <= ratio <= 1.05:
            winner = "tie"
            quality_note = "Los tiempos de pared quedan en una banda del 5%."
        elif parallel.wall_ms < sequential.wall_ms:
            winner = "parallel"
            quality_note = "Misma o mejor coherencia y menor tiempo de pared."
        else:
            winner = "sequential"
            quality_note = "El paralelo no redujo el tiempo de pared."

    explanation = [
        (
            f"Secuencial: {len(sequential.completed_sources)} fuentes completas, "
            f"{sequential.wall_ms} ms, passed={sequential.passed}."
        ),
        (
            f"Paralelo: {len(parallel.completed_sources)} fuentes completas, "
            f"{parallel.wall_ms} ms, overlap={parallel.overlap_observed}, "
            f"max_in_flight={parallel.max_in_flight}, passed={parallel.passed}."
        ),
        quality_note,
        "Ollama puede serializar un unico modelo; el laboratorio mide tiempo real, no teoriza.",
    ]
    return ComparisonView(
        winner=winner,
        sequential_passed=sequential.passed,
        parallel_passed=parallel.passed,
        sequential_ms=sequential.wall_ms,
        parallel_ms=parallel.wall_ms,
        speedup=speedup,
        completed_delta=completed_delta,
        overlap_observed=parallel.overlap_observed,
        explanation=explanation,
    )


def _run_sequential(
    task: str,
    sources: tuple[SourceDoc, ...],
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
) -> LaneView:
    started = time.perf_counter()
    tokens = _TokenCounter()
    nodes = NODE_FOR["sequential"]
    branches: list[BranchView] = []
    for source in sources:
        node_id = nodes[source.key]
        branch = _run_node(
            logger,
            node_id,
            "agent",
            f"Extrae hechos de {source.source_id}.",
            lambda current=source, current_node=node_id: _extract_branch(
                task,
                current,
                current_node,
                settings,
                client,
                logger,
                tokens,
            ),
        )
        branches.append(branch)

    table = join_branches(branches)
    path = _write_artifact(settings, logger, "sequential-table.md", render_table(table.rows))
    _run_node(
        logger,
        nodes["join"],
        "aggregator",
        "Espera las tres ramas y une solo las completas.",
        lambda: None,
        payload={
            "completed_sources": table.completed_sources,
            "failed_sources": table.failed_sources,
            "row_count": len(table.rows),
            "artifact": path.name,
        },
    )
    return _lane_from_branches(
        sources,
        branches,
        table,
        wall_ms=round((time.perf_counter() - started) * 1000, 1),
        overlap_observed=False,
        max_in_flight=1,
        tokens=tokens,
    )


def _run_parallel(
    task: str,
    sources: tuple[SourceDoc, ...],
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
) -> LaneView:
    started = time.perf_counter()
    tokens = _TokenCounter()
    nodes = NODE_FOR["parallel"]
    for source in sources:
        logger.emit(
            "node.queued",
            node_id=nodes[source.key],
            node_type="agent",
            state="queued",
            payload={"detail": f"Espera hueco para {source.source_id}."},
        )

    async def run_all() -> list[BranchView]:
        semaphore = asyncio.Semaphore(settings.max_in_flight)
        overlap = _OverlapTracker()

        async def one(source: SourceDoc) -> BranchView:
            node_id = nodes[source.key]
            token = _CancelToken()
            async with semaphore:
                overlap.begin()
                try:
                    return await asyncio.wait_for(
                        asyncio.to_thread(
                            _extract_branch,
                            task,
                            source,
                            node_id,
                            settings,
                            client,
                            logger,
                            tokens,
                            token,
                            True,
                        ),
                        timeout=settings.branch_timeout_seconds,
                    )
                except TimeoutError:
                    token.cancelled = True
                    logger.emit(
                        "node.failed",
                        node_id=node_id,
                        node_type="agent",
                        state="failed",
                        payload={
                            "detail": f"Timeout explicito de {source.source_id}.",
                            "source_id": source.source_id,
                            "status": "timeout",
                        },
                    )
                    return BranchView(
                        source_id=source.source_id,
                        node_id=node_id,
                        title=source.title,
                        status="timeout",
                        error=f"La rama {source.source_id} supero el timeout.",
                    )
                finally:
                    overlap.end()

        results = await asyncio.gather(*[one(source) for source in sources])
        holder["peak"] = overlap.peak
        return list(results)

    holder = {"peak": 1}
    branches = asyncio.run(run_all())
    peak = holder["peak"]
    overlap_observed = peak >= 2

    table = join_branches(branches)
    path = _write_artifact(settings, logger, "parallel-table.md", render_table(table.rows))
    _run_node(
        logger,
        nodes["join"],
        "aggregator",
        "Espera resultados o timeouts y une solo lo completo.",
        lambda: None,
        payload={
            "completed_sources": table.completed_sources,
            "failed_sources": table.failed_sources,
            "row_count": len(table.rows),
            "overlap_observed": overlap_observed,
            "max_in_flight": settings.max_in_flight,
            "overlap_peak": peak,
            "artifact": path.name,
        },
    )
    return _lane_from_branches(
        sources,
        branches,
        table,
        wall_ms=round((time.perf_counter() - started) * 1000, 1),
        overlap_observed=overlap_observed,
        max_in_flight=settings.max_in_flight,
        tokens=tokens,
    )


def _extract_branch(
    task: str,
    source: SourceDoc,
    node_id: str,
    settings: Settings,
    client: OllamaClient,
    logger: RunLogger,
    tokens: _TokenCounter,
    token: _CancelToken | None = None,
    already_queued: bool = False,
) -> BranchView:
    if already_queued:
        logger.emit("node.started", node_id=node_id, node_type="agent", state="running")
    if token is not None and token.cancelled:
        return BranchView(
            source_id=source.source_id,
            node_id=node_id,
            title=source.title,
            status="timeout",
            error="La rama fue cancelada por timeout.",
        )
    started = time.perf_counter()
    try:
        result = _chat(
            client,
            logger,
            node_id,
            [
                {"role": "system", "content": EXTRACTOR_SYSTEM},
                {"role": "user", "content": extractor_user(task, source)},
            ],
            tokens,
            response_format="json",
            token=token,
        )
        if token is not None and token.cancelled:
            return BranchView(
                source_id=source.source_id,
                node_id=node_id,
                title=source.title,
                status="timeout",
                error="La rama termino despues del timeout y se descarta.",
            )
        try:
            bundle = FactBundle.model_validate(extract_json_object(result.content))
        except (JsonParseError, ValidationError) as exc:
            raise ParallelError(
                f"La rama {source.source_id} no devolvio un FactBundle JSON valido."
            ) from exc
        ok, missing = score_bundle(source, bundle)
        if not ok:
            raise ParallelError(
                f"La rama {source.source_id} no cubre los hechos exigidos: {', '.join(missing)}."
            )
        facts = [
            FactRowView(
                fact_id=fact.fact_id,
                topic=fact.topic,
                value=fact.value,
                source_id=source.source_id,
                evidence=preview_text(fact.evidence, 80),
            )
            for fact in bundle.facts
            if fact.fact_id in source.required_ids
        ]
        logger.emit(
            "handoff.recorded",
            node_id=node_id,
            node_type="agent",
            state="done",
            payload={
                "source_id": source.source_id,
                "fact_ids": [fact.fact_id for fact in facts],
                "status": "completed",
            },
        )
        if already_queued:
            logger.emit(
                "node.completed",
                node_id=node_id,
                node_type="agent",
                state="done",
                payload={"detail": f"Hechos de {source.source_id} listos."},
            )
        return BranchView(
            source_id=source.source_id,
            node_id=node_id,
            title=source.title,
            status="completed",
            fact_ids=[fact.fact_id for fact in facts],
            facts=facts,
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
        )
    except (ParallelError, OllamaError) as exc:
        if token is not None and token.cancelled:
            return BranchView(
                source_id=source.source_id,
                node_id=node_id,
                title=source.title,
                status="timeout",
                error="La rama fue cancelada por timeout.",
            )
        logger.emit(
            "handoff.recorded",
            node_id=node_id,
            node_type="agent",
            state="failed",
            payload={
                "source_id": source.source_id,
                "status": "failed",
                "reason": str(exc)[:200],
            },
        )
        if already_queued:
            logger.emit(
                "node.failed",
                node_id=node_id,
                node_type="agent",
                state="failed",
                payload={"detail": str(exc)[:200], "source_id": source.source_id},
            )
        return BranchView(
            source_id=source.source_id,
            node_id=node_id,
            title=source.title,
            status="failed",
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
            error=str(exc),
        )


def _lane_from_branches(
    sources: tuple[SourceDoc, ...],
    branches: list[BranchView],
    table: TableView,
    *,
    wall_ms: float,
    overlap_observed: bool,
    max_in_flight: int,
    tokens: _TokenCounter,
) -> LaneView:
    lane = LaneView(
        status="running",
        wall_ms=wall_ms,
        overlap_observed=overlap_observed,
        max_in_flight=max_in_flight,
        completed_sources=list(table.completed_sources),
        failed_sources=list(table.failed_sources),
        fact_count=len(table.rows),
        preview=table.preview,
        branches=branches,
        table=table,
        prompt_tokens=tokens.prompt or None,
        output_tokens=tokens.output or None,
    )
    scored = score_lane(sources, lane)
    passed = scored.passed and len(table.failed_sources) == 0
    return lane.model_copy(
        update={
            "status": "passed" if passed else "failed",
            "passed": passed,
            "checks": list(scored.checks),
        }
    )


def _chat(
    client: OllamaClient,
    logger: RunLogger,
    node_id: str,
    messages: list[dict[str, str]],
    tokens: _TokenCounter,
    *,
    response_format: str | None = None,
    token: _CancelToken | None = None,
) -> ChatResult:
    if token is not None and token.cancelled:
        raise ParallelError("La rama fue cancelada por timeout.")
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
    tokens.add(result.prompt_tokens, result.output_tokens)
    if token is None or not token.cancelled:
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
    except (ParallelError, OllamaError):
        logger.emit(
            "node.failed",
            node_id=node_id,
            node_type=node_type,
            state="failed",
            payload={"detail": detail},
        )
        raise
    if isinstance(result, BranchView) and result.status != "completed":
        logger.emit(
            "node.failed",
            node_id=node_id,
            node_type=node_type,
            state="failed",
            payload={"detail": result.error or detail, "source_id": result.source_id},
        )
        return result
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

"""Corte vertical recuperar -> aumentar -> generar con estados visibles."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol, TextIO

from naive_rag.config import Settings
from naive_rag.corpus import CorpusIndex, SearchResult
from naive_rag.ollama_client import ChatResult, OllamaClient
from naive_rag.prompting import (
    CitationCheck,
    build_messages,
    citation_label,
    validate_answer_citations,
)
from naive_rag.run_log import RunLogger


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> ChatResult: ...


@dataclass(frozen=True, slots=True)
class RagAnswer:
    answer: str
    sources: tuple[SearchResult, ...]
    citation_check: CitationCheck
    abstained: bool
    run_path: Path


def run_question(
    settings: Settings,
    question: str,
    *,
    client: ChatClient | None = None,
    output: TextIO = sys.stdout,
) -> RagAnswer:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("La pregunta no puede estar vacia.")

    index_ref = settings.index_path.relative_to(settings.root).as_posix()
    logger = RunLogger(
        settings.runs_dir,
        model=settings.model,
        base_url=settings.base_url,
        index_ref=index_ref,
    )
    logger.emit(
        "run.started",
        payload={
            "interface": "windows-cli",
            "retriever": "sqlite-fts5",
            "top_k": settings.top_k,
            "input_chars": len(clean_question),
            "raw_input_stored": False,
        },
    )
    _write(output, f"RAG local | modelo: {settings.model} | recuperador: SQLite FTS5")
    _write(output, "Flujo: pregunta -> buscar -> aumentar -> Ollama -> respuesta")

    corpus = CorpusIndex(settings.index_path)
    logger.emit("node.queued", node_id="retrieve", node_type="retriever", state="queued")
    logger.emit("node.started", node_id="retrieve", node_type="retriever", state="running")
    logger.emit(
        "tool.requested",
        node_id="retrieve",
        node_type="retriever",
        state="waiting",
        payload={"tool": "sqlite-fts5", "top_k": settings.top_k},
    )
    retrieval_started = perf_counter()
    try:
        sources = corpus.search(clean_question, top_k=settings.top_k)
    except Exception as exc:
        duration_ms = round((perf_counter() - retrieval_started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="retrieve",
            node_type="retriever",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": duration_ms},
        )
        logger.emit("node.failed", node_id="retrieve", node_type="retriever", state="failed")
        logger.finish(status="failed", reason="retrieval_error", sources=0, abstained=True)
        raise

    retrieval_ms = round((perf_counter() - retrieval_started) * 1000, 3)
    logger.emit(
        "tool.completed",
        node_id="retrieve",
        node_type="retriever",
        state="done",
        payload={"tool": "sqlite-fts5", "matches": len(sources)},
        metrics={"wall_duration_ms": retrieval_ms},
    )
    logger.emit("node.completed", node_id="retrieve", node_type="retriever", state="done")
    _write(
        output,
        f"[1/3 buscar] queued -> running -> done | {len(sources)} fragmentos | "
        f"{retrieval_ms:.1f} ms",
    )

    if not sources:
        answer = "No encontre fragmentos lexicos suficientes para responder esa pregunta."
        logger.emit("node.completed", node_id="augment", node_type="context", state="skipped")
        logger.emit("node.completed", node_id="generate", node_type="model", state="skipped")
        _write(output, "[2/3 aumentar] skipped | sin contexto")
        _write(output, "[3/3 generar] skipped | Ollama no fue invocado")
        _write(output, f"\nRespuesta > {answer}")
        citation_check = validate_answer_citations(answer, source_count=0)
        logger.finish(status="completed", reason="no_matches", sources=0, abstained=True)
        _write(output, f"Traza JSONL: {logger.path.relative_to(settings.root)}")
        return RagAnswer(
            answer=answer,
            sources=(),
            citation_check=citation_check,
            abstained=True,
            run_path=logger.path,
        )

    logger.emit("node.started", node_id="augment", node_type="context", state="running")
    messages = build_messages(clean_question, sources)
    context_chars = sum(len(source.content) for source in sources)
    logger.emit(
        "node.completed",
        node_id="augment",
        node_type="context",
        state="done",
        payload={"sources": len(sources), "context_chars": context_chars},
    )
    _write(
        output,
        f"[2/3 aumentar] running -> done | {len(sources)} fuentes | {context_chars} caracteres",
    )

    actual_client = client or OllamaClient(
        settings.base_url,
        settings.model,
        settings.timeout_seconds,
    )
    logger.emit("node.queued", node_id="generate", node_type="model", state="queued")
    logger.emit(
        "model.requested",
        node_id="generate",
        node_type="model",
        state="waiting",
        payload={"messages": len(messages), "sources": len(sources)},
    )
    generation_started = perf_counter()
    try:
        model_result = actual_client.chat(messages)
    except BaseException as exc:
        duration_ms = round((perf_counter() - generation_started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="generate",
            node_type="model",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": duration_ms},
        )
        logger.emit("node.failed", node_id="generate", node_type="model", state="failed")
        logger.finish(
            status="failed", reason="generation_error", sources=len(sources), abstained=True
        )
        raise

    generation_ms = round((perf_counter() - generation_started) * 1000, 3)
    citation_check = validate_answer_citations(model_result.content, source_count=len(sources))
    metrics = {
        "wall_duration_ms": generation_ms,
        "ollama_duration_ms": model_result.total_duration_ms,
        "prompt_tokens": model_result.prompt_tokens,
        "output_tokens": model_result.output_tokens,
    }
    logger.emit(
        "model.completed",
        node_id="generate",
        node_type="model",
        state="done",
        payload={
            "response_chars": len(model_result.content),
            "response_model": model_result.model,
            "citation_valid": citation_check.valid,
            "citation_count": len(citation_check.cited_ids),
            "invalid_citation_count": len(citation_check.invalid_ids),
        },
        metrics=metrics,
    )
    logger.emit("node.completed", node_id="generate", node_type="model", state="done")
    logger.emit("metric.recorded", metrics=metrics)
    _write(output, f"[3/3 generar] waiting -> done | {generation_ms:.1f} ms")
    _write(output, f"\nRespuesta > {model_result.content}")
    _write(output, "\nFuentes recuperadas:")
    for source_id, source in enumerate(sources, 1):
        _write(output, f"- {citation_label(source_id, source)} | {source.heading}")
    if not citation_check.valid:
        _write(output, "ADVERTENCIA: la respuesta no uso citas validas; revisa las fuentes.")

    logger.finish(status="completed", reason="answered", sources=len(sources), abstained=False)
    _write(output, f"Traza JSONL: {logger.path.relative_to(settings.root)}")
    return RagAnswer(
        answer=model_result.content,
        sources=tuple(sources),
        citation_check=citation_check,
        abstained=False,
        run_path=logger.path,
    )


def _write(output: TextIO, text: str) -> None:
    print(text, file=output, flush=True)

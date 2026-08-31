"""Recuperar de forma hibrida, aumentar contexto y generar con citas."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol, TextIO

from vector_rag.config import Settings
from vector_rag.embeddings import EMBEDDING_PROFILE, EmbeddingClient
from vector_rag.index import Embedder, HybridIndex, SearchResult
from vector_rag.ollama_client import ChatResult, OllamaClient
from vector_rag.prompting import label, messages, valid_citations
from vector_rag.run_log import RunLogger


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> ChatResult: ...


@dataclass(frozen=True, slots=True)
class RagAnswer:
    answer: str
    sources: tuple[SearchResult, ...]
    citation_valid: bool
    run_path: Path


def run_question(
    settings: Settings,
    question: str,
    *,
    embedder: Embedder | None = None,
    client: ChatClient | None = None,
    output: TextIO = sys.stdout,
) -> RagAnswer:
    query = question.strip()
    if not query:
        raise ValueError("La pregunta no puede estar vacia.")
    actual_embedder = embedder or EmbeddingClient(
        settings.base_url,
        settings.embedding_model,
        settings.embedding_dimensions,
        settings.timeout_seconds,
    )
    index = HybridIndex(
        settings.index_path,
        settings.embedding_model,
        settings.embedding_dimensions,
        actual_embedder.profile if embedder else EMBEDDING_PROFILE,
    )
    logger = RunLogger(
        settings.runs_dir,
        chat_model=settings.chat_model,
        embedding_model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
        mode=settings.retrieval_mode,
        index_ref=settings.index_path.relative_to(settings.root).as_posix(),
    )
    logger.emit(
        "run.started",
        payload={"input_chars": len(query), "top_k": settings.top_k, "raw_input_stored": False},
    )
    print(
        f"RAG {settings.retrieval_mode} | chat={settings.chat_model} | "
        f"embedding={settings.embedding_model}/{settings.embedding_dimensions}",
        file=output,
    )
    logger.emit("node.started", node_id="retrieve", state="running")
    started = perf_counter()
    try:
        sources = index.search(
            query,
            top_k=settings.top_k,
            mode=settings.retrieval_mode,
            embedder=actual_embedder,
        )
    except (Exception, KeyboardInterrupt) as exc:
        elapsed = round((perf_counter() - started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="retrieve",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": elapsed},
        )
        logger.finish("failed", "retrieval_error", sources=0)
        raise
    retrieval_ms = round((perf_counter() - started) * 1000, 3)
    logger.emit(
        "tool.completed",
        node_id="retrieve",
        state="done",
        payload={"matches": len(sources), "mode": settings.retrieval_mode},
        metrics={"wall_duration_ms": retrieval_ms},
    )
    print(f"[1/3 recuperar] {settings.retrieval_mode} -> {len(sources)} fuentes", file=output)
    if not sources:
        answer = "No encontre evidencia suficiente en el corpus filtrado."
        print("[2/3 aumentar] skipped\n[3/3 generar] skipped", file=output)
        print(f"\nRespuesta > {answer}", file=output)
        logger.finish("completed", "no_matches", sources=0)
        return RagAnswer(answer, (), True, logger.path)

    prompt_messages = messages(query, sources)
    logger.emit(
        "node.completed",
        node_id="augment",
        state="done",
        payload={"sources": len(sources), "context_chars": sum(len(s.content) for s in sources)},
    )
    print(f"[2/3 aumentar] {len(sources)} fragmentos citables", file=output)
    actual_client = client or OllamaClient(
        settings.base_url, settings.chat_model, settings.timeout_seconds
    )
    logger.emit("model.requested", node_id="generate", state="waiting")
    generation_started = perf_counter()
    try:
        generated = actual_client.chat(prompt_messages)
    except (Exception, KeyboardInterrupt) as exc:
        elapsed = round((perf_counter() - generation_started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="generate",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": elapsed},
        )
        logger.finish("failed", "generation_error", sources=len(sources))
        raise
    generation_ms = round((perf_counter() - generation_started) * 1000, 3)
    citation_ok = valid_citations(generated.content, len(sources))
    metrics = {
        "wall_duration_ms": generation_ms,
        "ollama_duration_ms": generated.total_duration_ms,
        "prompt_tokens": generated.prompt_tokens,
        "output_tokens": generated.output_tokens,
    }
    logger.emit(
        "model.completed",
        node_id="generate",
        state="done",
        payload={"answer_chars": len(generated.content), "citation_valid": citation_ok},
        metrics=metrics,
    )
    print(f"[3/3 generar] done | {generation_ms:.1f} ms\n", file=output)
    print(f"Respuesta > {generated.content}\n\nFuentes:", file=output)
    for number, source in enumerate(sources, 1):
        vector = "-" if source.vector_score is None else f"{source.vector_score:.3f}"
        print(
            f"- {label(number, source)} | estado={source.source_status} | "
            f"lexical={source.lexical_rank or '-'} | vector={vector}",
            file=output,
        )
    if not citation_ok:
        print("ADVERTENCIA: la respuesta no uso citas validas.", file=output)
    logger.finish("completed", "answered", sources=len(sources))
    print(f"Traza JSONL: {logger.path.relative_to(settings.root)}", file=output)
    return RagAnswer(generated.content, tuple(sources), citation_ok, logger.path)

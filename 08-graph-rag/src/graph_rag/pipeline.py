"""Recorrer el grafo, contrastar con FTS5 y generar con citas."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol, TextIO

from graph_rag.config import Settings
from graph_rag.graph import GraphIndex, GraphPath, SearchBundle, ascii_path
from graph_rag.ollama_client import ChatResult, OllamaClient
from graph_rag.prompting import (
    format_lexical,
    format_path_block,
    label,
    messages,
    unique_hops,
    valid_citations,
)
from graph_rag.run_log import RunLogger


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> ChatResult: ...


@dataclass(frozen=True, slots=True)
class GraphAnswer:
    answer: str
    path: GraphPath | None
    citation_valid: bool
    abstained: bool
    run_path: Path


def run_question(
    settings: Settings,
    question: str,
    *,
    client: ChatClient | None = None,
    output: TextIO = sys.stdout,
) -> GraphAnswer:
    query = question.strip()
    if not query:
        raise ValueError("La pregunta no puede estar vacia.")
    index = GraphIndex(settings.index_path)
    logger = RunLogger(
        settings.runs_dir,
        chat_model=settings.model,
        mode=settings.retrieval_mode,
        max_hops=settings.max_hops,
        index_ref=settings.index_path.relative_to(settings.root).as_posix(),
    )
    logger.emit(
        "run.started",
        payload={
            "input_chars": len(query),
            "top_k": settings.top_k,
            "max_hops": settings.max_hops,
            "raw_input_stored": False,
        },
    )
    print(
        f"RAG {settings.retrieval_mode} | chat={settings.model} | hops<={settings.max_hops}",
        file=output,
    )
    logger.emit("node.started", node_id="traverse", state="running")
    started = perf_counter()
    try:
        bundle = index.search(
            query,
            top_k=settings.top_k,
            mode=settings.retrieval_mode,
            max_hops=settings.max_hops,
        )
    except (Exception, KeyboardInterrupt) as exc:
        elapsed = round((perf_counter() - started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="traverse",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": elapsed},
        )
        logger.finish("failed", "retrieval_error", sources=0, paths=0)
        raise
    retrieval_ms = round((perf_counter() - started) * 1000, 3)
    path = _best_path(bundle)
    path_count = 0 if bundle.graph is None else len(bundle.graph.paths)
    hop_count = 0 if path is None else len(path.hops)
    inferred = 0 if path is None or path.inferred is None else 1
    logger.emit(
        "tool.completed",
        node_id="traverse",
        state="done",
        payload={
            "paths": path_count,
            "extracted_hops": hop_count,
            "inferred": inferred,
            "lexical_hits": len(bundle.lexical),
            "mode": settings.retrieval_mode,
        },
        metrics={"wall_duration_ms": retrieval_ms},
    )
    print(
        f"[1/3 recorrer] {settings.retrieval_mode} -> {path_count} rutas, "
        f"{hop_count} aristas extraidas, {inferred} inferida",
        file=output,
    )
    if settings.retrieval_mode in {"lexical", "compare"} and bundle.lexical:
        print("Comparacion lexica (no reconstruye la ruta):", file=output)
        for line in format_lexical(bundle.lexical):
            print(line, file=output)

    if path is None or not path.hops:
        answer = "No encontre una ruta en el grafo con las entidades de la pregunta."
        print("[2/3 aumentar] skipped\n[3/3 generar] skipped", file=output)
        print(f"\nRespuesta > {answer}", file=output)
        logger.finish("completed", "no_path", sources=0, paths=0)
        print(f"Traza JSONL: {logger.path.relative_to(settings.root)}", file=output)
        return GraphAnswer(answer, None, True, True, logger.path)

    hops = unique_hops(path)
    logger.emit(
        "node.completed",
        node_id="augment",
        state="done",
        payload={"sources": len(hops), "hops": len(path.hops), "inferred": inferred},
    )
    print(f"[2/3 aumentar] {len(hops)} fuentes citables", file=output)
    print("\nRuta:\n" + format_path_block(path), file=output)
    actual_client = client or OllamaClient(
        settings.base_url, settings.model, settings.timeout_seconds
    )
    logger.emit("model.requested", node_id="generate", state="waiting")
    generation_started = perf_counter()
    try:
        generated = actual_client.chat(messages(query, path, hops))
    except (Exception, KeyboardInterrupt) as exc:
        elapsed = round((perf_counter() - generation_started) * 1000, 3)
        logger.emit(
            "error.raised",
            node_id="generate",
            state="failed",
            payload={"error_type": type(exc).__name__},
            metrics={"wall_duration_ms": elapsed},
        )
        logger.finish("failed", "generation_error", sources=len(hops), paths=1)
        raise
    generation_ms = round((perf_counter() - generation_started) * 1000, 3)
    citation_ok = valid_citations(generated.content, len(hops))
    logger.emit(
        "model.completed",
        node_id="generate",
        state="done",
        payload={"answer_chars": len(generated.content), "citation_valid": citation_ok},
        metrics={
            "wall_duration_ms": generation_ms,
            "ollama_duration_ms": generated.total_duration_ms,
            "prompt_tokens": generated.prompt_tokens,
            "output_tokens": generated.output_tokens,
        },
    )
    print(f"[3/3 generar] done | {generation_ms:.1f} ms\n", file=output)
    print(f"Respuesta > {generated.content}\n\nFuentes:", file=output)
    for number, hop in enumerate(hops, 1):
        print(f"- {label(number, hop)} | extracted | {hop.predicate}", file=output)
    if path.inferred is not None:
        print(
            f"- inferred | {path.inferred.subject} --{path.inferred.predicate}--> "
            f"{path.inferred.object}",
            file=output,
        )
    if not citation_ok:
        print("ADVERTENCIA: la respuesta no uso citas validas.", file=output)
    logger.finish("completed", "answered", sources=len(hops), paths=1)
    print(f"Traza JSONL: {logger.path.relative_to(settings.root)}", file=output)
    return GraphAnswer(generated.content, path, citation_ok, False, logger.path)


def _best_path(bundle: SearchBundle) -> GraphPath | None:
    if bundle.graph is None or not bundle.graph.paths:
        return None
    return max(bundle.graph.paths, key=lambda item: (len(item.hops), ascii_path(item)))

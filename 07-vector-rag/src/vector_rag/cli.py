"""CLI para construir, comparar y consultar el indice hibrido."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from vector_rag.config import ConfigurationError, Settings
from vector_rag.embeddings import EMBEDDING_PROFILE, EmbeddingClient, EmbeddingError
from vector_rag.index import HybridIndex, IndexingError, SearchError
from vector_rag.ollama_client import OllamaError
from vector_rag.pipeline import run_question


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vector-rag")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Crear la proyeccion FTS5 + vectores.")
    index.add_argument("--source", required=True, type=Path)
    search = commands.add_parser("search", help="Comparar resultados sin generar respuesta.")
    search.add_argument("--mode", choices=("lexical", "vector", "hybrid"), default=None)
    search.add_argument("question", nargs="+")
    ask = commands.add_parser("ask", help="Recuperar y responder con citas.")
    ask.add_argument("--mode", choices=("lexical", "vector", "hybrid"), default=None)
    ask.add_argument("question", nargs="*")
    commands.add_parser("stats")
    return parser


def cli(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    error_output: TextIO = sys.stderr,
) -> int:
    args = _parser().parse_args(argv)
    try:
        settings = Settings.load()
    except ConfigurationError as exc:
        print(f"Configuracion invalida: {exc}", file=error_output)
        return 2
    mode = getattr(args, "mode", None) or settings.retrieval_mode
    if mode != settings.retrieval_mode:
        settings = Settings(
            settings.root,
            settings.base_url,
            settings.chat_model,
            settings.embedding_model,
            settings.embedding_dimensions,
            settings.embedding_batch_size,
            settings.timeout_seconds,
            settings.index_path,
            settings.runs_dir,
            settings.top_k,
            settings.chunk_chars,
            mode,
        )
    embedder = EmbeddingClient(
        settings.base_url,
        settings.embedding_model,
        settings.embedding_dimensions,
        settings.timeout_seconds,
    )
    index = HybridIndex(
        settings.index_path,
        settings.embedding_model,
        settings.embedding_dimensions,
        EMBEDDING_PROFILE,
    )
    try:
        if args.command == "index":
            last = 0

            def progress(done: int, total: int) -> None:
                nonlocal last
                percent = int(done * 100 / total)
                if percent >= last + 10 or done == total:
                    print(f"[embeddings] {done}/{total} ({percent}%)", file=output)
                    last = percent

            stats = index.build(
                args.source,
                chunk_chars=settings.chunk_chars,
                batch_size=settings.embedding_batch_size,
                embedder=embedder,
                progress=progress,
            )
            print(
                f"Indice listo: {stats.indexed_documents}/{stats.discovered_documents} docs, "
                f"{stats.chunks} vectores, {stats.excluded_sections} secciones excluidas, "
                f"{stats.unreviewed_documents} fuentes no revisadas.",
                file=output,
            )
            return 0
        if args.command == "stats":
            stats = index.current_stats()
            print(
                f"Indice: {stats.indexed_documents} docs, {stats.chunks} vectores de "
                f"{stats.dimensions}d, {stats.excluded_sections} secciones excluidas.",
                file=output,
            )
            return 0
        question = " ".join(args.question).strip()
        if not question:
            question = input("Pregunta > ").strip()
        if args.command == "search":
            results = index.search(question, top_k=settings.top_k, mode=mode, embedder=embedder)
            for position, result in enumerate(results, 1):
                vector = "-" if result.vector_score is None else f"{result.vector_score:.3f}"
                print(
                    f"{position}. {result.source_path}:L{result.start_line}-L{result.end_line} "
                    f"status={result.source_status} lexical={result.lexical_rank or '-'} "
                    f"vector={vector}",
                    file=output,
                )
            return 0
        run_question(settings, question, embedder=embedder, output=output)
        return 0
    except (IndexingError, SearchError, EmbeddingError, OllamaError, ValueError) as exc:
        print(f"Operacion fallida: {exc}", file=error_output)
        return 1
    except KeyboardInterrupt:
        print("\nOperacion cancelada.", file=output)
        return 130


def main() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(cli())

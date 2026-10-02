"""CLI para construir, comparar y consultar el grafo local."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from graph_rag.config import ConfigurationError, Settings
from graph_rag.graph import GraphIndex, IndexingError, SearchError
from graph_rag.ollama_client import OllamaError
from graph_rag.pipeline import run_question
from graph_rag.prompting import format_lexical, format_path_block


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graph-rag")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Crear la proyeccion de documentos y aristas.")
    index.add_argument("--source", required=True, type=Path)
    search = commands.add_parser("search", help="Mostrar rutas o fragmentos sin generar.")
    search.add_argument("--mode", choices=("graph", "lexical", "compare"), default=None)
    search.add_argument("question", nargs="+")
    ask = commands.add_parser("ask", help="Recorrer el grafo y responder con citas.")
    ask.add_argument("--mode", choices=("graph", "lexical", "compare"), default=None)
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
            settings.model,
            settings.timeout_seconds,
            settings.index_path,
            settings.runs_dir,
            settings.top_k,
            settings.chunk_chars,
            settings.max_hops,
            mode,
        )
    index = GraphIndex(settings.index_path)
    try:
        if args.command == "index":
            stats = index.build(args.source, chunk_chars=settings.chunk_chars)
            relative_index = stats.index_path.relative_to(settings.root)
            print(
                f"Indice listo: {stats.indexed_documents}/{stats.discovered_documents} docs, "
                f"{stats.nodes} nodos, {stats.extracted_edges} aristas extraidas, "
                f"{stats.chunks} fragmentos.",
                file=output,
            )
            print(f"SQLite: {relative_index}", file=output)
            print(f"Corpus SHA-256: {stats.corpus_hash}", file=output)
            return 0
        if args.command == "stats":
            stats = index.current_stats()
            print(
                f"Indice: {stats.indexed_documents} docs, {stats.nodes} nodos, "
                f"{stats.extracted_edges} aristas extraidas, {stats.chunks} fragmentos.",
                file=output,
            )
            print(f"Corpus SHA-256: {stats.corpus_hash}", file=output)
            return 0
        question = " ".join(args.question).strip()
        if not question:
            question = input("Pregunta > ").strip()
        if not question:
            print("La pregunta no puede estar vacia.", file=error_output)
            return 2
        if args.command == "search":
            bundle = index.search(
                question,
                top_k=settings.top_k,
                mode=mode,
                max_hops=settings.max_hops,
            )
            if bundle.graph is not None:
                if not bundle.graph.paths:
                    seeds = ", ".join(bundle.graph.seeds or ("(ninguna)",))
                    print(f"Sin rutas. Semillas: {seeds}", file=output)
                for position, path in enumerate(bundle.graph.paths, 1):
                    print(f"{position}.", file=output)
                    print(format_path_block(path), file=output)
                    print(file=output)
            if bundle.lexical:
                print("Comparacion lexica:", file=output)
                for line in format_lexical(bundle.lexical):
                    print(line, file=output)
            return 0
        run_question(settings, question, output=output)
        return 0
    except (IndexingError, SearchError, OllamaError, ValueError) as exc:
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

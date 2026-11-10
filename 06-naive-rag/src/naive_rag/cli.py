"""Comandos PowerShell para indexar, consultar e inspeccionar el RAG."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from naive_rag.config import ConfigurationError, Settings
from naive_rag.corpus import CorpusIndex, IndexingError, SearchError
from naive_rag.ollama_client import OllamaError
from naive_rag.pipeline import run_question
from naive_rag.prompting import citation_label

PREVIEW_CHARS = 160


def _preview(text: str, limit: int = PREVIEW_CHARS) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="naive-rag",
        description="RAG lexico local: Markdown -> SQLite FTS5 -> Ollama -> citas.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    index_parser = subparsers.add_parser("index", help="Recrear el indice desde Markdown.")
    index_parser.add_argument("--source", required=True, type=Path, help="Carpeta fuente de .md")
    search_parser = subparsers.add_parser(
        "search",
        help="Ver los fragmentos que recibiria el modelo, sin invocar Ollama.",
    )
    search_parser.add_argument("question", nargs="+", help="Pregunta a buscar.")
    ask_parser = subparsers.add_parser("ask", help="Responder una pregunta con el indice.")
    ask_parser.add_argument("question", nargs="*", help="Pregunta; omitir abre un prompt.")
    subparsers.add_parser("stats", help="Mostrar el tamano de la proyeccion local.")
    return parser


def cli(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    error_output: TextIO = sys.stderr,
) -> int:
    args = _build_parser().parse_args(argv)
    try:
        settings = Settings.load()
    except ConfigurationError as exc:
        print(f"Configuracion invalida: {exc}", file=error_output)
        return 2

    index = CorpusIndex(settings.index_path)
    if args.command == "index":
        try:
            stats = index.build(args.source, chunk_chars=settings.chunk_chars)
        except IndexingError as exc:
            print(f"Indexacion fallida: {exc}", file=error_output)
            return 1
        relative_index = stats.index_path.relative_to(settings.root)
        print(
            "Indice listo: "
            f"{stats.indexed_documents}/{stats.discovered_documents} documentos, "
            f"{stats.chunks} fragmentos, {stats.duplicate_documents} duplicados omitidos.",
            file=output,
        )
        print(f"SQLite: {relative_index}", file=output)
        print(f"Corpus SHA-256: {stats.corpus_hash}", file=output)
        return 0

    if args.command == "stats":
        try:
            stats = index.current_stats()
        except SearchError as exc:
            print(f"Indice invalido: {exc}", file=error_output)
            return 1
        print(
            f"Indice: {stats.indexed_documents} documentos, {stats.chunks} fragmentos, "
            f"{stats.duplicate_documents} duplicados omitidos.",
            file=output,
        )
        print(f"Corpus SHA-256: {stats.corpus_hash}", file=output)
        return 0

    if args.command == "search":
        return _search(index, settings, " ".join(args.question).strip(), output, error_output)

    question = " ".join(args.question).strip()
    if not question:
        try:
            question = input("Pregunta > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nConsulta cancelada.", file=output)
            return 0
    if not question:
        print("La pregunta no puede estar vacia.", file=error_output)
        return 2
    try:
        run_question(settings, question, output=output)
    except (SearchError, OllamaError, ValueError) as exc:
        print(f"Consulta fallida: {exc}", file=error_output)
        return 1
    except KeyboardInterrupt:
        print("\nConsulta cancelada.", file=output)
        return 130
    return 0


def _search(
    index: CorpusIndex,
    settings: Settings,
    question: str,
    output: TextIO,
    error_output: TextIO,
) -> int:
    """Muestra el contexto que `ask` entregaria al modelo; no genera ni registra JSONL."""

    try:
        results = index.search(question, top_k=settings.top_k)
    except SearchError as exc:
        print(f"Busqueda fallida: {exc}", file=error_output)
        return 1
    print(
        f"Recuperador: SQLite FTS5 (BM25) | top_k={settings.top_k} | Ollama no se invoca",
        file=output,
    )
    if not results:
        print(
            "Sin coincidencias lexicas: `ask` se abstendria sin llamar al modelo.",
            file=output,
        )
        return 0
    print("bm25 de SQLite: cuanto mas negativo, mas relevante.", file=output)
    for position, result in enumerate(results, 1):
        print(
            f"{citation_label(position, result)} bm25={result.score:.3f} | {result.heading}",
            file=output,
        )
        print(f"    {_preview(result.content)}", file=output)
    return 0


def _configure_output_encoding(output: TextIO) -> None:
    reconfigure = getattr(output, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    _configure_output_encoding(sys.stdout)
    raise SystemExit(cli())

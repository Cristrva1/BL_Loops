"""CLI para construir el indice y conversar con el agente de ventas."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from sales_agent.agent import Conversation
from sales_agent.config import ConfigurationError, Settings
from sales_agent.embeddings import EMBEDDING_PROFILE, EmbeddingClient, EmbeddingError
from sales_agent.index import HybridSalesIndex, IndexingError, SearchError
from sales_agent.ollama_client import OllamaChatClient, OllamaError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sales-agent")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Crear el indice privado del agente.")
    index.add_argument("--source", required=True, type=Path)
    ask = commands.add_parser("ask", help="Ejecutar un turno del agente.")
    ask.add_argument("question", nargs="*")
    commands.add_parser("chat", help="Abrir una conversacion con memoria en RAM.")
    commands.add_parser("stats", help="Inspeccionar el indice compatible.")
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
    embedder = EmbeddingClient(
        settings.base_url,
        settings.embedding_model,
        settings.embedding_dimensions,
        settings.timeout_seconds,
    )
    index = HybridSalesIndex(
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

        client = OllamaChatClient(settings.base_url, settings.chat_model, settings.timeout_seconds)
        conversation = Conversation(
            settings,
            index=index,
            embedder=embedder,
            client=client,
            output=output,
        )
        if args.command == "ask":
            question = " ".join(args.question).strip()
            if not question:
                question = input("Pregunta > ").strip()
            conversation.ask(question)
            return 0

        print(
            "Agente listo. La memoria vive solo en RAM. Usa /estado, /limpiar o /salir.",
            file=output,
        )
        while True:
            question = input("Tu > ").strip()
            if question.casefold() == "/salir":
                print("Sesion cerrada; la memoria en RAM fue descartada.", file=output)
                return 0
            if question.casefold() == "/estado":
                print(
                    f"Mensajes en RAM: {len(conversation.history)} | "
                    f"limite: {settings.history_turns * 2}",
                    file=output,
                )
                continue
            if question.casefold() == "/limpiar":
                conversation.clear()
                print("Memoria de la conversacion vaciada.", file=output)
                continue
            if not question:
                continue
            conversation.ask(question)
    except (IndexingError, SearchError, EmbeddingError, OllamaError, ValueError) as exc:
        print(f"Operacion fallida: {exc}", file=error_output)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSesion cancelada; la memoria en RAM fue descartada.", file=output)
        return 130


def main() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(cli())

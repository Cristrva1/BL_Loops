"""Línea de comandos (CLI) para procesar transcripciones desde la terminal."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .config import Settings
from .contracts import SummarizeRequest
from .ollama_client import OllamaClient
from .storage import Storage
from .summarizer import MeetingSummarizerEngine


async def _run_summarize(file_path: Path, title: str | None, model: str | None, mode: str) -> None:
    if not file_path.exists():
        print(f"Error: El archivo '{file_path}' no existe.", file=sys.stderr)
        sys.exit(1)

    text = file_path.read_text(encoding="utf-8")
    settings = Settings()
    storage = Storage(settings.get_db_path())
    ollama = OllamaClient(
        base_url=settings.ollama_base_url,
        default_model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
        num_ctx=settings.ollama_num_ctx,
    )
    engine = MeetingSummarizerEngine(ollama, storage)

    req = SummarizeRequest(
        transcript_text=text,
        title=title or file_path.stem.replace("_", " ").title(),
        model=model or settings.ollama_model,
        mode=mode,  # type: ignore[arg-type]
    )

    print(f"\nProcesando '{req.title}' con modelo {req.model}...")
    print("=" * 60)

    last_report = None
    async for event in engine.summarize_stream(req):
        bar = "#" * (event.progress // 5)
        print(f"[{event.progress:3d}%] [{bar:<20}] {event.message}")
        if event.stage == "completed" and event.payload:
            last_report = event.payload.get("report")

    if last_report:
        print("\n" + "=" * 60)
        print(f"TITULO: {last_report['title']}")
        print(f"DURACION: {last_report['metadata']['duration_seconds']}s · PALABRAS: {last_report['metadata']['total_words']}")
        print(f"PARTICIPANTES: {', '.join(last_report['metadata']['participants'])}")
        print("\nRESUMEN EJECUTIVO:")
        print(last_report["executive_summary"])

        print("\nDECISIONES CLAVE:")
        for d in last_report.get("decisions", []):
            print(f"  • {d['decision']}")

        print("\nCOMPROMISOS / TAREAS:")
        for a in last_report.get("action_items", []):
            print(f"  [{a['priority'].upper()}] {a['assignee']}: {a['task']} (Plazo: {a.get('deadline') or 'N/A'})")

        print("\n" + "=" * 60)
        print(f"Minuta guardada en SQLite local. ID: {last_report['meeting_id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Procesador CLI de transcripciones de reuniones.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sum_parser = subparsers.add_parser("summarize", help="Procesar y resumir una transcripción.")
    sum_parser.add_argument("file", type=Path, help="Ruta al archivo de transcripción (.txt, .vtt, .srt)")
    sum_parser.add_argument("--title", type=str, default=None, help="Título de la reunión")
    sum_parser.add_argument("--model", type=str, default=None, help="Modelo Ollama a utilizar")
    sum_parser.add_argument("--mode", type=str, default="completo", choices=["completo", "ejecutivo", "tareas", "tecnico"])

    subparsers.add_parser("list", help="Listar reuniones guardadas en SQLite local.")

    args = parser.parse_args()

    if args.command == "summarize":
        asyncio.run(_run_summarize(args.file, args.title, args.model, args.mode))
    elif args.command == "list":
        settings = Settings()
        storage = Storage(settings.get_db_path())
        meetings = storage.list_meetings()
        if not meetings:
            print("No hay reuniones guardadas.")
            return
        print(f"\n{'ID':<38} {'FORMATO':<10} {'PALABRAS':<10} {'TITULO'}")
        print("-" * 80)
        for m in meetings:
            print(f"{m.meeting_id:<38} {m.format:<10} {m.total_words:<10} {m.title}")


if __name__ == "__main__":
    main()

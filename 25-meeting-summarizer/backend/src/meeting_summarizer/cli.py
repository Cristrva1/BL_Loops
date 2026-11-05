"""Línea de comandos (CLI) para procesar transcripciones desde la terminal."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from .chunker import SUMMARY_MAX_WORDS_PER_CHUNK, SUMMARY_OVERLAP_WORDS, chunk_turns
from .config import Settings
from .contracts import SummarizeRequest
from .ollama_client import OllamaClient
from .parser import parse_transcript
from .storage import Storage
from .summarizer import MeetingSummarizerEngine

PREVIEW_TURNS = 3
PREVIEW_CHARS = 90


def load_settings() -> Settings:
    """Carga la configuración y convierte un error de validación en un mensaje claro."""

    try:
        return Settings()
    except ValidationError as exc:
        reasons = "; ".join(
            str(error["msg"]).removeprefix("Value error, ") for error in exc.errors()
        )
        print(f"Configuracion invalida: {reasons}", file=sys.stderr)
        raise SystemExit(2) from exc


def _format_duration(seconds: int) -> str:
    minutes, rest = divmod(seconds, 60)
    return f"{minutes} min {rest} s" if minutes else f"{rest} s"


def _preview(text: str) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= PREVIEW_CHARS else compact[: PREVIEW_CHARS - 1] + "…"


def run_parse(
    file_path: Path,
    *,
    title: str | None = None,
    max_words: int = SUMMARY_MAX_WORDS_PER_CHUNK,
    overlap_words: int = SUMMARY_OVERLAP_WORDS,
    output: TextIO = sys.stdout,
) -> int:
    """Muestra lo que el resumidor enviaría a Ollama, sin llamarlo ni guardar nada."""

    if not file_path.is_file():
        print(f"Error: El archivo '{file_path}' no existe.", file=output)
        return 1
    if max_words < 20 or not 0 <= overlap_words < max_words:
        print("Error: usa --max-words >= 20 y 0 <= --overlap-words < --max-words.", file=output)
        return 2

    turns, metadata = parse_transcript(file_path.read_text(encoding="utf-8"), title)
    print("Analisis local: Ollama no se invoca y no se guarda nada.", file=output)
    print(f"Archivo: {file_path.name}", file=output)
    print(f"Formato detectado: {metadata.detected_format.value}", file=output)
    print(
        f"Turnos: {metadata.total_turns} | Palabras: {metadata.total_words} | "
        f"Duracion: {_format_duration(metadata.duration_seconds)}",
        file=output,
    )
    print(f"Participantes ({len(metadata.participants)}):", file=output)
    for speaker in metadata.participants:
        print(f"  - {speaker}: {metadata.speaker_turn_counts[speaker]} turnos", file=output)
    print("Primeros turnos normalizados:", file=output)
    for turn in turns[:PREVIEW_TURNS]:
        stamp = f"[{turn.timestamp}] " if turn.timestamp else ""
        print(f"  {turn.turn_index}. {stamp}{turn.speaker}: {_preview(turn.text)}", file=output)

    chunks = chunk_turns(turns, max_words_per_chunk=max_words, overlap_words=overlap_words)
    print(
        f"Plan de analisis (limite {max_words} palabras por bloque, solapamiento "
        f"{overlap_words}):",
        file=output,
    )
    if len(chunks) <= 1:
        print("  single-pass: 1 bloque -> 1 llamada a Ollama", file=output)
    else:
        print(
            f"  map-reduce: {len(chunks)} bloques -> {len(chunks)} resumenes parciales "
            "+ 1 consolidacion",
            file=output,
        )
        for chunk in chunks:
            print(
                f"    Bloque {chunk.chunk_index}/{chunk.total_chunks}: turnos "
                f"{chunk.start_turn}-{chunk.end_turn}, {chunk.word_count} palabras",
                file=output,
            )
    return 0


async def _run_summarize(file_path: Path, title: str | None, model: str | None, mode: str) -> None:
    if not file_path.exists():
        print(f"Error: El archivo '{file_path}' no existe.", file=sys.stderr)
        sys.exit(1)

    text = file_path.read_text(encoding="utf-8")
    settings = load_settings()
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

    parse_parser = subparsers.add_parser(
        "parse",
        help="Normalizar una transcripción y mostrar el plan de bloques, sin llamar a Ollama.",
    )
    parse_parser.add_argument("file", type=Path, help="Transcripción (.txt, .vtt, .srt)")
    parse_parser.add_argument("--title", type=str, default=None, help="Título de la reunión")
    parse_parser.add_argument(
        "--max-words",
        type=int,
        default=SUMMARY_MAX_WORDS_PER_CHUNK,
        help="Palabras por bloque antes de pasar a map-reduce (por defecto, el del resumidor).",
    )
    parse_parser.add_argument(
        "--overlap-words",
        type=int,
        default=SUMMARY_OVERLAP_WORDS,
        help="Palabras repetidas entre bloques consecutivos.",
    )

    args = parser.parse_args()

    if args.command == "parse":
        _configure_output_encoding()
        raise SystemExit(
            run_parse(
                args.file,
                title=args.title,
                max_words=args.max_words,
                overlap_words=args.overlap_words,
            )
        )
    if args.command == "summarize":
        asyncio.run(_run_summarize(args.file, args.title, args.model, args.mode))
    elif args.command == "list":
        settings = load_settings()
        storage = Storage(settings.get_db_path())
        meetings = storage.list_meetings()
        if not meetings:
            print("No hay reuniones guardadas.")
            return
        print(f"\n{'ID':<38} {'FORMATO':<10} {'PALABRAS':<10} {'TITULO'}")
        print("-" * 80)
        for m in meetings:
            print(f"{m.meeting_id:<38} {m.format:<10} {m.total_words:<10} {m.title}")


def _configure_output_encoding() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    main()

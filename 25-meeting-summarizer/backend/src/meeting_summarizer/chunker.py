"""Estrategias de partición y gestión de contexto para transcripciones."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import SpeakerTurn


@dataclass(frozen=True, slots=True)
class TranscriptChunk:
    """Segmento acotado de la reunión para procesamiento por bloques."""

    chunk_index: int
    total_chunks: int
    start_turn: int
    end_turn: int
    text_content: str
    word_count: int


def format_turns_to_text(turns: list[SpeakerTurn]) -> str:
    """Convierte una lista de turnos a un bloque de texto formateado para el modelo."""
    lines: list[str] = []
    for t in turns:
        ts_part = f"[{t.timestamp}] " if t.timestamp else ""
        lines.append(f"{ts_part}{t.speaker}: {t.text}")
    return "\n".join(lines)


# Límites usados por el resumidor. `meeting-summarizer parse` los muestra sin llamar a Ollama.
SUMMARY_MAX_WORDS_PER_CHUNK = 3200
SUMMARY_OVERLAP_WORDS = 250


def chunk_turns(
    turns: list[SpeakerTurn],
    max_words_per_chunk: int = 2500,
    overlap_words: int = 250,
) -> list[TranscriptChunk]:
    """Divide una secuencia de turnos en fragmentos lógicos con solapamiento."""
    if not turns:
        return []

    total_words = sum(len(t.text.split()) for t in turns)
    # Si cabe cómodamente en un solo bloque, devolver un único fragmento
    if total_words <= max_words_per_chunk:
        full_text = format_turns_to_text(turns)
        return [
            TranscriptChunk(
                chunk_index=1,
                total_chunks=1,
                start_turn=turns[0].turn_index,
                end_turn=turns[-1].turn_index,
                text_content=full_text,
                word_count=total_words,
            )
        ]

    chunks: list[TranscriptChunk] = []
    current_turns: list[SpeakerTurn] = []
    current_words = 0
    i = 0

    while i < len(turns):
        turn = turns[i]
        turn_words = len(turn.text.split())

        current_turns.append(turn)
        current_words += turn_words

        if current_words >= max_words_per_chunk or i == len(turns) - 1:
            chunk_text = format_turns_to_text(current_turns)
            chunks.append(
                TranscriptChunk(
                    chunk_index=len(chunks) + 1,
                    total_chunks=0,  # Se ajustará al final
                    start_turn=current_turns[0].turn_index,
                    end_turn=current_turns[-1].turn_index,
                    text_content=chunk_text,
                    word_count=current_words,
                )
            )

            if i == len(turns) - 1:
                break

            # Calcular solapamiento para el siguiente bloque
            overlap_accum = 0
            backtrack_turns: list[SpeakerTurn] = []
            for t in reversed(current_turns):
                t_w = len(t.text.split())
                if overlap_accum + t_w <= overlap_words:
                    backtrack_turns.insert(0, t)
                    overlap_accum += t_w
                else:
                    break

            current_turns = list(backtrack_turns)
            current_words = overlap_accum

        i += 1

    # Ajustar el conteo total en todos los chunks
    total_chunks = len(chunks)
    final_chunks = [
        TranscriptChunk(
            chunk_index=c.chunk_index,
            total_chunks=total_chunks,
            start_turn=c.start_turn,
            end_turn=c.end_turn,
            text_content=c.text_content,
            word_count=c.word_count,
        )
        for c in chunks
    ]
    return final_chunks

from meeting_summarizer.chunker import chunk_turns, format_turns_to_text
from meeting_summarizer.contracts import SpeakerTurn


def test_format_turns_to_text():
    turns = [
        SpeakerTurn(turn_index=1, speaker="Ana", timestamp="00:01", text="Hola"),
        SpeakerTurn(turn_index=2, speaker="Beto", timestamp="00:05", text="¿Qué tal?"),
    ]
    formatted = format_turns_to_text(turns)
    assert "[00:01] Ana: Hola" in formatted
    assert "[00:05] Beto: ¿Qué tal?" in formatted


def test_chunk_turns_single_chunk():
    turns = [
        SpeakerTurn(turn_index=1, speaker="Ana", timestamp="00:01", text="Hola equipo."),
        SpeakerTurn(turn_index=2, speaker="Beto", timestamp="00:05", text="Todo listo."),
    ]
    chunks = chunk_turns(turns, max_words_per_chunk=100)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 1
    assert chunks[0].total_chunks == 1
    assert chunks[0].start_turn == 1
    assert chunks[0].end_turn == 2


def test_chunk_turns_multiple_chunks():
    # Crear muchos turnos para forzar partición
    turns = [
        SpeakerTurn(
            turn_index=i + 1,
            speaker=f"Persona_{i % 3}",
            timestamp=f"00:{i:02d}",
            text="Esta es una frase con diez palabras para probar la segmentación.",
        )
        for i in range(30)
    ]
    # 30 turnos * 10 palabras = 300 palabras
    chunks = chunk_turns(turns, max_words_per_chunk=100, overlap_words=20)
    assert len(chunks) >= 3
    for c in chunks:
        assert c.total_chunks == len(chunks)
        assert c.word_count > 0

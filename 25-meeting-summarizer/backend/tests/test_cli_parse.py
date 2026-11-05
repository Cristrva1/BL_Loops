import io
from pathlib import Path

from meeting_summarizer.cli import run_parse

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_parse_shows_format_participants_and_single_pass_plan() -> None:
    output = io.StringIO()

    assert run_parse(FIXTURES / "zoom_standup.vtt", output=output) == 0

    text = output.getvalue()
    assert "Ollama no se invoca" in text
    assert "Formato detectado: zoom_vtt" in text
    assert "Elena Gómez" in text
    assert "single-pass: 1 bloque -> 1 llamada a Ollama" in text


def test_small_word_limit_reveals_the_map_reduce_plan_with_overlap() -> None:
    output = io.StringIO()

    exit_code = run_parse(
        FIXTURES / "meet_sprint_planning.txt", max_words=120, overlap_words=30, output=output
    )

    text = output.getvalue()
    assert exit_code == 0
    assert "map-reduce: 2 bloques -> 2 resumenes parciales + 1 consolidacion" in text
    assert "Bloque 1/2: turnos 1-6" in text
    assert "Bloque 2/2: turnos 6-13" in text


def test_plain_notes_without_speakers_fall_back_to_plain_text() -> None:
    output = io.StringIO()

    run_parse(FIXTURES / "notas_lluvia_de_ideas.txt", output=output)

    assert "Formato detectado: plain_text" in output.getvalue()


def test_parse_rejects_missing_files_and_invalid_limits(tmp_path: Path) -> None:
    assert run_parse(tmp_path / "no-existe.txt", output=io.StringIO()) == 1
    assert run_parse(FIXTURES / "zoom_standup.vtt", max_words=10, output=io.StringIO()) == 2
    assert (
        run_parse(
            FIXTURES / "zoom_standup.vtt", max_words=100, overlap_words=100, output=io.StringIO()
        )
        == 2
    )

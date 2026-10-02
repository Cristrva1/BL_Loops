from meeting_summarizer.contracts import TranscriptFormat
from meeting_summarizer.parser import parse_transcript


def test_parse_meet_format():
    sample = """
[00:00:10] Carlos Mendoza: Buenos días equipo.
[00:00:25] Valeria Rios: Hola Carlos, lista para revisar el backlog.
[00:01:05] Carlos Mendoza: Revisemos las fechas de entrega.
    """
    turns, meta = parse_transcript(sample, custom_title="Planificación")
    assert len(turns) == 3
    assert meta.detected_format == TranscriptFormat.MEET
    assert "Carlos Mendoza" in meta.participants
    assert "Valeria Rios" in meta.participants
    assert meta.total_words > 10
    assert meta.duration_seconds >= 55  # 00:01:05 - 00:00:10 = 55s


def test_parse_vtt_format():
    vtt = """WEBVTT

1
00:00:01.000 --> 00:00:04.000
Elena Gómez: Inicio de la llamada.

2
00:00:05.000 --> 00:00:10.000
Marcos Peña: Todo listo por acá.
"""
    turns, meta = parse_transcript(vtt)
    assert len(turns) == 2
    assert meta.detected_format == TranscriptFormat.ZOOM_VTT
    assert "Elena Gómez" in meta.participants
    assert "Marcos Peña" in meta.participants


def test_parse_teams_format():
    teams = """Daniela Castro  00:10
Hola a todos los presentes.

Andrés Morales  00:30
Hola Daniela, listos para coordinar.
"""
    turns, meta = parse_transcript(teams)
    assert len(turns) == 2
    assert meta.detected_format == TranscriptFormat.TEAMS
    assert "Daniela Castro" in meta.participants
    assert "Andrés Morales" in meta.participants


def test_parse_plain_text_fallback():
    raw = """Hoy nos reunimos para hablar del presupuesto del Q3.
Decidimos asignar un 20% adicional a infraestructura local.
Ana coordinará la compra de servidores."""
    turns, meta = parse_transcript(raw)
    assert len(turns) == 3
    assert meta.detected_format == TranscriptFormat.PLAIN_TEXT
    assert meta.total_words > 15

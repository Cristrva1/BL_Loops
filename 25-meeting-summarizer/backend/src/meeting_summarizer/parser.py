"""Parser multi-formato para transcripciones de videollamadas."""

from __future__ import annotations

import re

from .contracts import MeetingMetadata, SpeakerTurn, TranscriptFormat

# Patrones de coincidencia
# 1. Zoom WebVTT timestamp: 00:01:05.120 --> 00:01:08.500
_RE_VTT_ARROW = re.compile(
    r"(\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{3})?)\s*-->\s*(\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{3})?)"
)

# 2. Timestamp al inicio con corchetes o paréntesis: [00:01:23] Carlos: Hola o (00:01:23) Carlos: Hola
_RE_BRACKET_TIMESTAMP_SPEAKER = re.compile(
    r"^[\[\(](\d{1,2}:\d{2}(?::\d{2})?)[\]\)]\s*([^:\n]+)[:\-]\s*(.*)$"
)

# 3. Timestamp directo al inicio: 00:01:23 Carlos: Hola o 01:23 Carlos: Hola
_RE_DIRECT_TIMESTAMP_SPEAKER = re.compile(
    r"^(\d{1,2}:\d{2}(?::\d{2})?)\s+([^:\n]+)[:\-]\s*(.*)$"
)

# 4. Hablante con timestamp al final o intermedio: Carlos [00:01:23]: Hola o Carlos (00:01:23): Hola
_RE_SPEAKER_TIMESTAMP_TEXT = re.compile(
    r"^([^:\n\[\(]+)\s*[\[\(](\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)[\]\)]\s*[:\-]?\s*(.*)$"
)

# 5. Hablante clásico sin timestamp: **Carlos**: Hola o Carlos: Hola
_RE_SPEAKER_ONLY = re.compile(
    r"^(?:\*\*)?([A-Za-zÀ-ÿ0-9_\.\s]{2,40})(?:\*\*)?\s*:\s*(.+)$"
)

# 6. Formato de dos líneas tipo Teams: Línea 1 = "Juan Pérez  00:15", Línea 2 = "Hola equipo"
_RE_TEAMS_HEADER = re.compile(
    r"^([A-Za-zÀ-ÿ\s]{2,40})\s+(\d{1,2}:\d{2}(?::\d{2})?)$"
)


def _timestamp_to_seconds(ts: str) -> int:
    """Convierte HH:MM:SS o MM:SS a segundos enteros."""
    clean = re.sub(r"[.,]\d+", "", ts.strip())
    # Manejo de AM/PM si está presente
    clean = re.sub(r"\s*[APap][Mm]", "", clean)
    parts = clean.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 1:
            return int(parts[0])
    except ValueError:
        return 0
    return 0


def _clean_text_line(line: str) -> str:
    """Limpia etiquetas HTML y espacios redundantes."""
    no_html = re.sub(r"<[^>]+>", "", line)
    return " ".join(no_html.split()).strip()


def parse_transcript(raw_text: str, custom_title: str | None = None) -> tuple[list[SpeakerTurn], MeetingMetadata]:
    """Analiza una transcripción en texto plano y extrae turnos estructurados y metadatos."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        empty_meta = MeetingMetadata(title=custom_title or "Reunión vacía")
        return [], empty_meta

    detected_format = TranscriptFormat.GENERIC
    turns: list[SpeakerTurn] = []

    # Comprobación de formato WebVTT
    if any("WEBVTT" in line.upper() for line in lines[:5]) or any("-->" in line for line in lines[:10]):
        detected_format = TranscriptFormat.ZOOM_VTT
        turns = _parse_vtt(lines)
    else:
        # Intento de parseo línea por línea
        turns, detected_format = _parse_standard_lines(lines)

    # Si no se detectaron turnos con hablante, fallback a texto plano continuo
    if not turns:
        detected_format = TranscriptFormat.PLAIN_TEXT
        turns = _parse_plain_text_fallback(lines)

    # Cálculo de metadatos cuantitativos
    total_words = sum(len(t.text.split()) for t in turns)
    participants_map: dict[str, int] = {}
    for t in turns:
        speaker = t.speaker.strip()
        participants_map[speaker] = participants_map.get(speaker, 0) + 1

    # Estimación de duración
    duration_seconds = _estimate_duration(turns, total_words)

    title = custom_title.strip() if custom_title and custom_title.strip() else "Sincronización de equipo"

    metadata = MeetingMetadata(
        title=title,
        detected_format=detected_format,
        total_words=total_words,
        total_turns=len(turns),
        duration_seconds=duration_seconds,
        participants=sorted(participants_map.keys()),
        speaker_turn_counts=participants_map,
    )

    return turns, metadata


def _parse_vtt(lines: list[str]) -> list[SpeakerTurn]:
    turns: list[SpeakerTurn] = []
    idx = 1
    current_ts: str | None = None

    for line in lines:
        if "WEBVTT" in line.upper() or line.isdigit():
            continue
        arrow_match = _RE_VTT_ARROW.search(line)
        if arrow_match:
            current_ts = arrow_match.group(1)
            continue

        clean = _clean_text_line(line)
        if not clean:
            continue

        # Intentar extraer hablante si viene tipo "Juan: texto"
        speaker_match = _RE_SPEAKER_ONLY.match(clean)
        if speaker_match:
            speaker = speaker_match.group(1).strip()
            text = speaker_match.group(2).strip()
        else:
            speaker = "Participante"
            text = clean

        turns.append(
            SpeakerTurn(
                turn_index=idx,
                speaker=speaker,
                timestamp=current_ts,
                text=text,
            )
        )
        idx += 1

    return turns


def _parse_standard_lines(lines: list[str]) -> tuple[list[SpeakerTurn], TranscriptFormat]:
    turns: list[SpeakerTurn] = []
    idx = 1
    detected_format = TranscriptFormat.GENERIC

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1. Comprobar formato Teams de dos líneas
        teams_match = _RE_TEAMS_HEADER.match(line)
        if teams_match and i + 1 < len(lines):
            speaker = teams_match.group(1).strip()
            ts = teams_match.group(2).strip()
            i += 1
            text = _clean_text_line(lines[i])
            turns.append(SpeakerTurn(turn_index=idx, speaker=speaker, timestamp=ts, text=text))
            idx += 1
            detected_format = TranscriptFormat.TEAMS
            i += 1
            continue

        # 2. Bracket timestamp speaker: [00:01:23] Juan: Texto
        b_match = _RE_BRACKET_TIMESTAMP_SPEAKER.match(line)
        if b_match:
            ts = b_match.group(1).strip()
            speaker = b_match.group(2).strip()
            text = _clean_text_line(b_match.group(3))
            turns.append(SpeakerTurn(turn_index=idx, speaker=speaker, timestamp=ts, text=text))
            idx += 1
            detected_format = TranscriptFormat.MEET
            i += 1
            continue

        # 3. Direct timestamp speaker: 00:01:23 Juan: Texto
        d_match = _RE_DIRECT_TIMESTAMP_SPEAKER.match(line)
        if d_match:
            ts = d_match.group(1).strip()
            speaker = d_match.group(2).strip()
            text = _clean_text_line(d_match.group(3))
            turns.append(SpeakerTurn(turn_index=idx, speaker=speaker, timestamp=ts, text=text))
            idx += 1
            detected_format = TranscriptFormat.MEET
            i += 1
            continue

        # 4. Speaker timestamp text: Juan [00:01:23]: Texto
        s_match = _RE_SPEAKER_TIMESTAMP_TEXT.match(line)
        if s_match:
            speaker = s_match.group(1).strip()
            ts = s_match.group(2).strip()
            text = _clean_text_line(s_match.group(3))
            turns.append(SpeakerTurn(turn_index=idx, speaker=speaker, timestamp=ts, text=text))
            idx += 1
            detected_format = TranscriptFormat.MEET
            i += 1
            continue

        # 5. Speaker only: Juan: Texto
        so_match = _RE_SPEAKER_ONLY.match(line)
        if so_match:
            speaker = so_match.group(1).strip()
            text = _clean_text_line(so_match.group(2))
            turns.append(SpeakerTurn(turn_index=idx, speaker=speaker, timestamp=None, text=text))
            idx += 1
            if detected_format == TranscriptFormat.GENERIC:
                detected_format = TranscriptFormat.GENERIC
            i += 1
            continue

        # Si una línea no coincide con hablante pero tenemos turnos previos, puede ser continuación del turno
        if turns and line:
            clean = _clean_text_line(line)
            turns[-1].text += f" {clean}"

        i += 1

    return turns, detected_format


def _parse_plain_text_fallback(lines: list[str]) -> list[SpeakerTurn]:
    """Genera turnos a partir de párrafos de texto continuo sin formato de hablantes."""
    turns: list[SpeakerTurn] = []
    idx = 1
    for line in lines:
        clean = _clean_text_line(line)
        if clean:
            turns.append(
                SpeakerTurn(
                    turn_index=idx,
                    speaker="Transcripción",
                    timestamp=None,
                    text=clean,
                )
            )
            idx += 1
    return turns


def _estimate_duration(turns: list[SpeakerTurn], total_words: int) -> int:
    """Calcula la duración en segundos a partir de timestamps o tasa de palabras por minuto."""
    timestamps = [t.timestamp for t in turns if t.timestamp]
    if len(timestamps) >= 2:
        start_sec = _timestamp_to_seconds(timestamps[0])
        end_sec = _timestamp_to_seconds(timestamps[-1])
        diff = end_sec - start_sec
        if diff > 10:
            return diff

    # Estimación promedio: 130 palabras por minuto
    wpm = 130
    minutes = max(1.0, total_words / wpm)
    return int(minutes * 60)

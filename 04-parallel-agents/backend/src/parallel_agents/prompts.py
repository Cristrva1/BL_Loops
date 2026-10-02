"""Instrucciones cortas para cada extractor. No se exportan en el JSONL."""

from __future__ import annotations

from .sources import SourceDoc

CASE_ID = "I-PARALLEL-002@0.1.0"

DEFAULT_TASK = (
    "Extrae los hechos verificables de tres documentos independientes sobre el Taller Norte "
    "y construye una tabla consolidada. Cada hecho debe conservar la procedencia de su fuente. "
    "Una rama fallida no puede aparecer como completa."
)

EXTRACTOR_SYSTEM = (
    "Eres un extractor de hechos. Lees un solo documento y respondes unicamente con JSON. "
    "El objeto tiene source_id y facts. Cada fact tiene fact_id, topic, value y evidence. "
    "Usa exactamente los fact_id de la lista recibida. value copia el dato literal, "
    "incluyendo horas con formato 09:00 o 18:00. "
    "evidence es una cita corta del mismo documento. No inventes hechos ausentes. "
    "No uses datos de otras fuentes. No nombres proveedores cloud."
)


def extractor_user(task: str, source: SourceDoc) -> str:
    required = ", ".join(source.required_ids)
    return (
        f"Tarea global:\n{task}\n\n"
        f"source_id obligatorio: {source.source_id}\n"
        f"fact_id obligatorios: {required}\n\n"
        f"Documento {source.filename}:\n{source.text}\n\n"
        "Devuelve solo JSON con source_id y facts."
    )

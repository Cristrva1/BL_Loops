"""Utilidades para leer la salida de un modelo local sin confiar en ella.

El modelo devuelve texto. Antes de convertirlo en planos o prompts hay que quitar el envoltorio
Markdown, interpretar el JSON y explicar con una frase corta por qué se rechaza cuando falla.
"""

import json
from typing import Any


def strip_code_fence(text: str) -> str:
    """Quita la valla ```json ... ``` que algunos modelos añaden alrededor del JSON."""

    cleaned = text.strip()
    if "```" not in cleaned:
        return cleaned
    inner = cleaned.split("```", 2)[1]
    if inner[:4].lower() == "json":
        inner = inner[4:]
    return inner.strip()


def load_json(text: str) -> Any:
    """Interpreta el JSON de la respuesta; lanza ValueError si no es JSON válido."""

    return json.loads(strip_code_fence(text))


def short_reason(exc: Exception, limit: int = 160) -> str:
    """Resume un error en una sola línea apta para un evento SSE o la terminal."""

    message = " ".join(str(exc).split()) or type(exc).__name__
    return message if len(message) <= limit else message[: limit - 1] + "…"

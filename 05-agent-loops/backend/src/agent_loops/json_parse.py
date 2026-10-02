"""Extraccion estricta de un objeto JSON desde una respuesta de modelo."""

from __future__ import annotations

import json
import re
from typing import Any


class JsonParseError(ValueError):
    """La respuesta no contiene un objeto JSON utilizable."""


_FENCE_PREFIX = re.compile(r"^```(?:json)?\s*", re.IGNORECASE)
_FENCE_SUFFIX = re.compile(r"\s*```$")


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise JsonParseError("La respuesta esta vacia.")
    if stripped.startswith("```"):
        stripped = _FENCE_PREFIX.sub("", stripped)
        stripped = _FENCE_SUFFIX.sub("", stripped).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        raise JsonParseError("No hay un objeto JSON en la respuesta.")

    try:
        value = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError as exc:
        raise JsonParseError("El objeto JSON esta mal formado.") from exc
    if not isinstance(value, dict):
        raise JsonParseError("El JSON debe ser un objeto, no una lista ni un escalar.")
    return value

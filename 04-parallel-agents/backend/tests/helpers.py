from __future__ import annotations

import json
import threading
import time

from parallel_agents.ollama_client import ChatResult, OllamaError
from parallel_agents.sources import SourceDoc, load_sources

TASK = (
    "Extrae los hechos verificables de tres documentos independientes sobre el Taller Norte "
    "y construye una tabla consolidada."
)

BUNDLES = {
    "source-a": {
        "source_id": "source-a",
        "facts": [
            {
                "fact_id": "precio_basico",
                "topic": "precio",
                "value": "29 EUR",
                "evidence": "El plan basico cuesta 29 EUR al mes.",
            },
            {
                "fact_id": "plan_taller",
                "topic": "precio",
                "value": "49 EUR",
                "evidence": "El plan taller cuesta 49 EUR al mes.",
            },
        ],
    },
    "source-b": {
        "source_id": "source-b",
        "facts": [
            {
                "fact_id": "apertura_semana",
                "topic": "horario",
                "value": "09:00",
                "evidence": "abre a las 09:00",
            },
            {
                "fact_id": "cierre_semana",
                "topic": "horario",
                "value": "18:00",
                "evidence": "cierra a las 18:00",
            },
        ],
    },
    "source-c": {
        "source_id": "source-c",
        "facts": [
            {
                "fact_id": "garantia_meses",
                "topic": "garantia",
                "value": "24 meses",
                "evidence": "garantia de reparacion es de 24 meses",
            },
            {
                "fact_id": "recambios",
                "topic": "garantia",
                "value": "locales",
                "evidence": "Los recambios son locales.",
            },
        ],
    },
}


def passing_json(source_id: str) -> str:
    return json.dumps(BUNDLES[source_id], ensure_ascii=False)


def fixture_sources() -> tuple[SourceDoc, ...]:
    return load_sources()


class ScriptedClient:
    def __init__(
        self,
        responses: dict[str, str] | None = None,
        *,
        delay: float = 0.0,
        hang_source: str | None = None,
        invalid_source: str | None = None,
    ) -> None:
        self.responses = responses or {key: passing_json(key) for key in BUNDLES}
        self.delay = delay
        self.hang_source = hang_source
        self.invalid_source = invalid_source
        self.calls: list[list[dict[str, str]]] = []
        self._lock = threading.Lock()
        self.peak_in_flight = 0
        self._in_flight = 0

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        response_format: str | None = None,
    ) -> ChatResult:
        _ = response_format
        with self._lock:
            self.calls.append(messages)
            self._in_flight += 1
            self.peak_in_flight = max(self.peak_in_flight, self._in_flight)
        try:
            blob = "\n".join(message["content"] for message in messages)
            source_id = next(
                (key for key in ("source-a", "source-b", "source-c") if key in blob),
                None,
            )
            if source_id is None:
                raise OllamaError("No hay source_id en el prompt scriptado.")
            if self.hang_source == source_id:
                time.sleep(1.5)
            elif self.delay:
                time.sleep(self.delay)
            if self.invalid_source == source_id:
                return ChatResult(
                    content="esto no es un bundle",
                    model="qwen3.5:4b",
                    total_duration_ms=8.0,
                    prompt_tokens=11,
                    output_tokens=17,
                )
            content = self.responses.get(source_id)
            if content is None:
                raise OllamaError(f"No hay respuesta scriptada para {source_id}.")
            return ChatResult(
                content=content,
                model="qwen3.5:4b",
                total_duration_ms=8.0,
                prompt_tokens=11,
                output_tokens=17,
            )
        finally:
            with self._lock:
                self._in_flight -= 1

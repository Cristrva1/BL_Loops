"""Cliente HTTP minimo para el endpoint local de chat de Ollama."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class OllamaError(RuntimeError):
    """Error seguro y explicable al generar una respuesta."""


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    model: str
    total_duration_ms: float | None
    prompt_tokens: int | None
    output_tokens: int | None


OpenUrl = Callable[..., Any]


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        return None


class OllamaClient:
    """Envia contexto recuperado y devuelve solo la respuesta final."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
        opener: OpenUrl | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler()).open

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.2, "top_p": 0.9},
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "BL-Loops-Naive-RAG/0.1",
            },
            method="POST",
        )

        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw_response = response.read()
        except HTTPError as exc:
            detail = _read_error_detail(exc)
            if exc.code == 404:
                raise OllamaError(
                    f"Ollama no encontro el modelo '{self.model}'. Compruebalo con: ollama list"
                ) from exc
            raise OllamaError(f"Ollama respondio HTTP {exc.code}: {detail}") from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama tardo mas de {self.timeout_seconds:g} segundos en responder."
            ) from exc
        except URLError as exc:
            raise OllamaError(
                "No se pudo conectar con Ollama local. Comprueba que Ollama este iniciado."
            ) from exc

        try:
            decoded = json.loads(raw_response.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OllamaError("Ollama devolvio una respuesta que no es JSON valido.") from exc
        if not isinstance(decoded, dict):
            raise OllamaError("Ollama devolvio un contrato inesperado.")
        if isinstance(decoded.get("error"), str):
            raise OllamaError(f"Ollama informo un error: {decoded['error'][:240]}")

        message = decoded.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise OllamaError("Ollama no devolvio contenido final para mostrar.")

        return ChatResult(
            content=content.strip(),
            model=str(decoded.get("model") or self.model),
            total_duration_ms=_nanoseconds_to_milliseconds(decoded.get("total_duration")),
            prompt_tokens=_optional_int(decoded.get("prompt_eval_count")),
            output_tokens=_optional_int(decoded.get("eval_count")),
        )


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _nanoseconds_to_milliseconds(value: object) -> float | None:
    nanoseconds = _optional_int(value)
    return round(nanoseconds / 1_000_000, 3) if nanoseconds is not None else None


def _read_error_detail(error: HTTPError) -> str:
    try:
        decoded = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "error local sin detalle util"
    detail = decoded.get("error") if isinstance(decoded, dict) else None
    return detail[:240] if isinstance(detail, str) else "error local sin detalle util"

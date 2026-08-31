"""Cliente de generacion local compatible con la API de chat de Ollama."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class OllamaError(RuntimeError):
    pass


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
    def __init__(
        self, base_url: str, model: str, timeout_seconds: float, opener: OpenUrl | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler()).open

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0.2, "top_p": 0.9},
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "BL-Loops-Vector-RAG/0.1"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            if exc.code == 404:
                raise OllamaError(
                    f"Ollama no encontro '{self.model}'. Compruebalo con: ollama list"
                ) from exc
            raise OllamaError(f"Ollama respondio HTTP {exc.code}.") from exc
        except TimeoutError as exc:
            raise OllamaError("Ollama excedio el timeout sin un resultado confirmado.") from exc
        except URLError as exc:
            raise OllamaError("No se pudo conectar con Ollama local.") from exc
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OllamaError("Ollama devolvio JSON invalido.") from exc
        message = decoded.get("message") if isinstance(decoded, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise OllamaError("Ollama no devolvio contenido final.")
        return ChatResult(
            content.strip(),
            str(decoded.get("model") or self.model),
            _milliseconds(decoded.get("total_duration")),
            _integer(decoded.get("prompt_eval_count")),
            _integer(decoded.get("eval_count")),
        )


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _milliseconds(value: object) -> float | None:
    number = _integer(value)
    return round(number / 1_000_000, 3) if number is not None else None

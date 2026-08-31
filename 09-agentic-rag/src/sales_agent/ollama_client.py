"""Cliente local de /api/chat con soporte minimo de tool calling."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class OllamaError(RuntimeError):
    """Ollama no completo el contrato de chat esperado."""


@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, object]


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    model: str
    tool_calls: tuple[ToolCall, ...]
    total_duration_ms: float | None
    prompt_tokens: int | None
    output_tokens: int | None


OpenUrl = Callable[..., Any]


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        return None


class OllamaChatClient:
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

    def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[dict[str, object]] | None = None,
    ) -> ChatResult:
        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {"temperature": 0},
        }
        if tools is not None:
            payload["tools"] = tools
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "BL-Loops-Sales-Agent/0.1"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = _error_detail(exc)
            if exc.code == 404:
                raise OllamaError(
                    f"Ollama no encontro '{self.model}'. Compruebalo con: ollama list"
                ) from exc
            raise OllamaError(f"Ollama respondio HTTP {exc.code}: {detail}") from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama tardo mas de {self.timeout_seconds:g} segundos en responder."
            ) from exc
        except URLError as exc:
            raise OllamaError("No se pudo conectar con Ollama local.") from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OllamaError("Ollama devolvio una respuesta que no es JSON valido.") from exc
        if not isinstance(decoded, dict) or decoded.get("done") is not True:
            raise OllamaError("Ollama no marco la respuesta como terminada.")
        done_reason = decoded.get("done_reason")
        if done_reason not in {None, "stop"}:
            raise OllamaError(f"Ollama termino de forma inesperada: {done_reason}")
        message = decoded.get("message")
        if not isinstance(message, dict):
            raise OllamaError("Ollama no devolvio un mensaje de asistente.")
        content_value = message.get("content", "")
        if not isinstance(content_value, str):
            raise OllamaError("El contenido de Ollama no es texto.")
        tool_calls = _parse_tool_calls(message.get("tool_calls"))
        content = content_value.strip()
        if not content and not tool_calls:
            raise OllamaError("Ollama no devolvio contenido ni una llamada de herramienta.")
        return ChatResult(
            content,
            str(decoded.get("model") or self.model),
            tool_calls,
            _milliseconds(decoded.get("total_duration")),
            _integer(decoded.get("prompt_eval_count")),
            _integer(decoded.get("eval_count")),
        )


def _parse_tool_calls(value: object) -> tuple[ToolCall, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise OllamaError("tool_calls no es una lista valida.")
    parsed: list[ToolCall] = []
    for index, raw_call in enumerate(value):
        if not isinstance(raw_call, dict):
            raise OllamaError("Una llamada de herramienta no es un objeto.")
        function = raw_call.get("function")
        if not isinstance(function, dict):
            raise OllamaError("La llamada no contiene una funcion valida.")
        name = function.get("name")
        arguments = function.get("arguments")
        if not isinstance(name, str) or not name or not isinstance(arguments, dict):
            raise OllamaError("La funcion o sus argumentos no cumplen el contrato.")
        call_id = raw_call.get("id")
        if not isinstance(call_id, str) or not call_id:
            call_id = f"call-{index + 1}"
        parsed.append(ToolCall(call_id, name, arguments))
    return tuple(parsed)


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _milliseconds(value: object) -> float | None:
    number = _integer(value)
    return round(number / 1_000_000, 3) if number is not None else None


def _error_detail(error: HTTPError) -> str:
    try:
        decoded = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "error local sin detalle util"
    detail = decoded.get("error") if isinstance(decoded, dict) else None
    return detail[:240] if isinstance(detail, str) else "error local sin detalle util"

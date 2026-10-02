"""Cliente HTTP para Ollama local con soporte de chat estructurado y catálogo de modelos."""

from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class OllamaError(RuntimeError):
    """Error al comunicarse con la instancia local de Ollama."""


@dataclass(frozen=True, slots=True)
class ChatResponseData:
    content: str
    model: str
    total_duration_ms: float | None
    prompt_tokens: int | None
    output_tokens: int | None


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        return None


class OllamaClient:
    """Cliente HTTP sin dependencias pesadas para Ollama local."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        default_model: str = "qwen3.5:9b",
        timeout_seconds: float = 180.0,
        num_ctx: int = 16384,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.num_ctx = num_ctx
        self._opener = build_opener(ProxyHandler({}), _NoRedirectHandler()).open

    def is_available(self) -> bool:
        """Comprueba si el servidor local de Ollama está accesible."""
        try:
            req = Request(f"{self.base_url}/api/tags", method="GET")
            with self._opener(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Obtiene la lista de nombres de modelos locales instalados."""
        req = Request(f"{self.base_url}/api/tags", method="GET")
        try:
            with self._opener(req, timeout=5.0) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            return [self.default_model, "qwen3.5:4b", "gemma4:e4b"]

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
        json_format: bool = False,
        num_ctx: int | None = None,
    ) -> ChatResponseData:
        """Envía una conversación a Ollama y retorna la respuesta."""
        target_model = model or self.default_model
        ctx = num_ctx or self.num_ctx

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": ctx,
            },
        }
        if json_format:
            payload["format"] = "json"

        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "BL-Loops-Meeting-Summarizer/0.1",
            },
            method="POST",
        )

        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = ""
            with contextlib.suppress(Exception):
                detail = exc.read().decode("utf-8")
            if exc.code == 404:
                raise OllamaError(
                    f"Ollama no encontró el modelo '{target_model}'. Ejecuta en consola: ollama pull {target_model}"
                ) from exc
            raise OllamaError(f"Ollama respondió HTTP {exc.code}: {detail}") from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama superó el límite de tiempo de espera ({self.timeout_seconds:g}s). Prueba con un modelo más liviano como qwen3.5:4b."
            ) from exc
        except URLError as exc:
            raise OllamaError(
                "No se pudo conectar con Ollama en http://127.0.0.1:11434. Asegúrate de tener Ollama iniciado."
            ) from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama devolvió una respuesta que no es JSON válido.") from exc

        if isinstance(decoded.get("error"), str):
            raise OllamaError(f"Ollama reportó un error: {decoded['error']}")

        message = decoded.get("message", {})
        content = message.get("content", "")
        if not content:
            raise OllamaError("Ollama no devolvió texto en el mensaje de respuesta.")

        duration_ns = decoded.get("total_duration")
        duration_ms = float(duration_ns) / 1_000_000.0 if duration_ns else None

        return ChatResponseData(
            content=content.strip(),
            model=decoded.get("model", target_model),
            total_duration_ms=duration_ms,
            prompt_tokens=decoded.get("prompt_eval_count"),
            output_tokens=decoded.get("eval_count"),
        )

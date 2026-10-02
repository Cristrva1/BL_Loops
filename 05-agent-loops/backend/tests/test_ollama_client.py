from __future__ import annotations

import io
import json
from urllib.error import HTTPError, URLError

import pytest

import agent_loops.ollama_client as ollama_client_module
from agent_loops.ollama_client import OllamaClient, OllamaError


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_chat_returns_only_final_content() -> None:
    captured: dict[str, object] = {}

    def opener(request: object, *, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "model": "qwen3.5:4b",
                "message": {
                    "role": "assistant",
                    "thinking": "contenido privado",
                    "content": "Salida lista",
                },
                "total_duration": 2_500_000,
                "prompt_eval_count": 12,
                "eval_count": 5,
            }
        )

    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)
    result = client.chat([{"role": "user", "content": "Hola"}])

    request = captured["request"]
    body = json.loads(request.data.decode("utf-8"))
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert body["think"] is False
    assert body["stream"] is False
    assert "format" not in body
    assert result.content == "Salida lista"


def test_json_format_is_requested_when_needed() -> None:
    captured: dict[str, object] = {}

    def opener(request: object, *, timeout: float) -> FakeResponse:
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "model": "qwen3.5:4b",
                "message": {"role": "assistant", "content": '{"prompt":"Nuevo"}'},
            }
        )

    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)
    client.chat([{"role": "user", "content": "Mejora"}], response_format="json")

    assert captured["body"]["format"] == "json"


def test_missing_model_has_actionable_error() -> None:
    def opener(*_args: object, **_kwargs: object) -> FakeResponse:
        raise HTTPError(
            "http://127.0.0.1:11434/api/chat",
            404,
            "Not Found",
            None,
            io.BytesIO(b'{"error":"model not found"}'),
        )

    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)

    with pytest.raises(OllamaError, match="ollama list"):
        client.chat([{"role": "user", "content": "Hola"}])


def test_connection_failure_does_not_retry() -> None:
    calls = 0

    def opener(*_args: object, **_kwargs: object) -> FakeResponse:
        nonlocal calls
        calls += 1
        raise URLError("connection refused")

    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)

    with pytest.raises(OllamaError, match="conectar con Ollama local"):
        client.chat([{"role": "user", "content": "Hola"}])

    assert calls == 1


def test_default_transport_disables_proxies(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeOpener:
        def open(self, *_args: object, **_kwargs: object) -> FakeResponse:
            raise AssertionError("No debe hacer una solicitud durante la configuracion.")

    def fake_build_opener(*handlers: object) -> FakeOpener:
        captured["handlers"] = handlers
        return FakeOpener()

    monkeypatch.setattr(ollama_client_module, "build_opener", fake_build_opener)
    OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10)

    handlers = captured["handlers"]
    assert handlers[0].proxies == {}
    assert handlers[1].redirect_request(None) is None

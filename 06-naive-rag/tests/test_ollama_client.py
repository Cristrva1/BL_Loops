import io
import json
from urllib.error import HTTPError, URLError

import pytest

import naive_rag.ollama_client as ollama_client_module
from naive_rag.ollama_client import OllamaClient, OllamaError


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_chat_sends_grounded_messages_and_returns_only_final_content() -> None:
    captured: dict[str, object] = {}

    def opener(request: object, *, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "model": "qwen3.5:4b",
                "message": {
                    "role": "assistant",
                    "thinking": "razonamiento privado",
                    "content": "Respuesta respaldada [S1].",
                },
                "total_duration": 3_500_000,
                "prompt_eval_count": 55,
                "eval_count": 9,
            }
        )

    messages = [{"role": "user", "content": "contexto"}]
    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)

    result = client.chat(messages)

    request = captured["request"]
    body = json.loads(request.data.decode("utf-8"))
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert captured["timeout"] == 10
    assert body["model"] == "qwen3.5:4b"
    assert body["messages"] == messages
    assert body["stream"] is False
    assert body["think"] is False
    assert result.content == "Respuesta respaldada [S1]."
    assert result.total_duration_ms == 3.5
    assert result.prompt_tokens == 55
    assert result.output_tokens == 9


def test_connection_failure_is_explained_without_retry() -> None:
    calls = 0

    def opener(*_args: object, **_kwargs: object) -> FakeResponse:
        nonlocal calls
        calls += 1
        raise URLError("connection refused")

    client = OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10, opener=opener)

    with pytest.raises(OllamaError, match="Ollama local"):
        client.chat([{"role": "user", "content": "Hola"}])

    assert calls == 1


def test_missing_model_has_an_actionable_error() -> None:
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


def test_default_transport_disables_environment_proxies_and_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeOpener:
        def open(self, *_args: object, **_kwargs: object) -> FakeResponse:
            raise AssertionError("No debe solicitar durante la configuracion.")

    def fake_build_opener(*handlers: object) -> FakeOpener:
        captured["handlers"] = handlers
        return FakeOpener()

    monkeypatch.setattr(ollama_client_module, "build_opener", fake_build_opener)

    OllamaClient("http://127.0.0.1:11434", "qwen3.5:4b", 10)

    handlers = captured["handlers"]
    assert handlers[0].proxies == {}
    assert handlers[1].redirect_request(None) is None

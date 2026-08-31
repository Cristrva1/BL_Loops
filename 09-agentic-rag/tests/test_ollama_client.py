import io
import json

import pytest

from sales_agent.ollama_client import OllamaChatClient, OllamaError


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


def test_chat_parses_single_tool_call_and_sends_schema() -> None:
    captured: dict[str, object] = {}

    def opener(request, *, timeout):
        captured.update(json.loads(request.data))
        body = {
            "model": "qwen3.5:4b",
            "done": True,
            "done_reason": "stop",
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "function": {
                            "name": "search_sales_library",
                            "arguments": {"query": "venta sin presion"},
                        },
                    }
                ],
            },
        }
        return Response(json.dumps(body).encode())

    client = OllamaChatClient("http://127.0.0.1:11434", "qwen3.5:4b", 7, opener=opener)
    result = client.chat([{"role": "user", "content": "ayudame"}], tools=[{"type": "function"}])

    assert captured["stream"] is False
    assert captured["think"] is False
    assert captured["tools"] == [{"type": "function"}]
    assert result.tool_calls[0].name == "search_sales_library"
    assert result.tool_calls[0].arguments == {"query": "venta sin presion"}


def test_chat_requires_content_or_tool_call() -> None:
    def opener(_request, *, timeout):
        return Response(
            b'{"model":"local","done":true,"done_reason":"stop",'
            b'"message":{"role":"assistant","content":""}}'
        )

    client = OllamaChatClient("http://127.0.0.1:11434", "local", 7, opener=opener)

    with pytest.raises(OllamaError, match="contenido"):
        client.chat([{"role": "user", "content": "hola"}])

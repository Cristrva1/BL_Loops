import json
from urllib.error import URLError

import pytest

import vector_rag.embeddings as embeddings_module
from vector_rag.embeddings import QUERY_INSTRUCTION, EmbeddingClient, EmbeddingError


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_documents_and_query_use_same_model_but_only_query_gets_instruction() -> None:
    requests: list[object] = []

    def opener(request: object, *, timeout: float) -> FakeResponse:
        requests.append(request)
        body = json.loads(request.data.decode("utf-8"))
        count = len(body["input"]) if isinstance(body["input"], list) else 1
        return FakeResponse(
            {
                "model": "qwen3-embedding:latest",
                "embeddings": [[1.0, 0.0, 0.0] for _ in range(count)],
                "total_duration": 2_000_000,
                "prompt_eval_count": 9,
            }
        )

    client = EmbeddingClient(
        "http://127.0.0.1:11434", "qwen3-embedding:latest", 3, 10, opener=opener
    )

    documents = client.embed_documents(["pasaje uno", "pasaje dos"])
    query = client.embed_query("necesidad del cliente")

    document_body = json.loads(requests[0].data.decode("utf-8"))
    query_body = json.loads(requests[1].data.decode("utf-8"))
    assert document_body["input"] == ["pasaje uno", "pasaje dos"]
    assert query_body["input"].startswith(f"Instruct: {QUERY_INSTRUCTION}")
    assert query_body["input"].endswith("Query: necesidad del cliente")
    assert document_body["dimensions"] == 3
    assert document_body["truncate"] is False
    assert len(documents.vectors) == 2
    assert query.vectors[0] == (1.0, 0.0, 0.0)


def test_embedding_vectors_are_validated_and_normalized() -> None:
    def opener(*_args: object, **_kwargs: object) -> FakeResponse:
        return FakeResponse({"model": "qwen3-embedding:latest", "embeddings": [[3.0, 4.0, 0.0]]})

    result = EmbeddingClient(
        "http://127.0.0.1:11434", "qwen3-embedding:latest", 3, 10, opener=opener
    ).embed_documents(["texto"])

    assert result.vectors[0] == pytest.approx((0.6, 0.8, 0.0))


def test_connection_failure_is_not_retried() -> None:
    calls = 0

    def opener(*_args: object, **_kwargs: object) -> FakeResponse:
        nonlocal calls
        calls += 1
        raise URLError("offline")

    client = EmbeddingClient(
        "http://127.0.0.1:11434", "qwen3-embedding:latest", 3, 10, opener=opener
    )

    with pytest.raises(EmbeddingError, match="Ollama local"):
        client.embed_documents(["texto"])
    assert calls == 1


def test_default_transport_disables_proxies_and_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeOpener:
        def open(self, *_args: object, **_kwargs: object) -> FakeResponse:
            raise AssertionError("No debe solicitar durante la configuracion.")

    def fake_build_opener(*handlers: object) -> FakeOpener:
        captured["handlers"] = handlers
        return FakeOpener()

    monkeypatch.setattr(embeddings_module, "build_opener", fake_build_opener)
    EmbeddingClient("http://127.0.0.1:11434", "qwen3-embedding:latest", 3, 10)

    handlers = captured["handlers"]
    assert handlers[0].proxies == {}
    assert handlers[1].redirect_request(None) is None

import io
import json
import math

import pytest

from sales_agent.embeddings import EmbeddingClient, EmbeddingError


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


def test_query_has_instruction_but_documents_do_not() -> None:
    payloads: list[dict[str, object]] = []

    def opener(request, *, timeout):
        assert timeout == 7
        payload = json.loads(request.data)
        payloads.append(payload)
        count = len(payload["input"]) if isinstance(payload["input"], list) else 1
        return Response(json.dumps({"embeddings": [[3.0, 4.0]] * count}).encode())

    client = EmbeddingClient("http://127.0.0.1:11434", "embed", 2, 7, opener=opener)
    documents = client.embed_documents(["texto uno", "texto dos"])
    query = client.embed_query("como escuchar")

    assert payloads[0]["input"] == ["texto uno", "texto dos"]
    assert str(payloads[1]["input"]).startswith("Instruct:")
    assert str(payloads[1]["input"]).endswith("Query: como escuchar")
    assert math.isclose(documents.vectors[0][0], 0.6)
    assert math.isclose(query.vectors[0][1], 0.8)


def test_wrong_dimensions_fail_closed() -> None:
    def opener(_request, *, timeout):
        return Response(b'{"embeddings":[[1.0]]}')

    client = EmbeddingClient("http://127.0.0.1:11434", "embed", 2, 7, opener=opener)

    with pytest.raises(EmbeddingError, match="dimensiones"):
        client.embed_query("consulta")

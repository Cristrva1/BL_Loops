import io
from pathlib import Path

from vector_rag.config import Settings
from vector_rag.embeddings import EmbeddingBatch
from vector_rag.index import HybridIndex
from vector_rag.ollama_client import ChatResult
from vector_rag.pipeline import run_question
from vector_rag.validation import validate_run


class Embedder:
    model = "test-embedding:v1"
    dimensions = 3
    profile = "test-sales-v1"

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
        return EmbeddingBatch(tuple((1.0, 0.0, 0.0) for _ in texts), 1.0, len(texts))

    def embed_query(self, _text: str) -> EmbeddingBatch:
        return EmbeddingBatch(((1.0, 0.0, 0.0),), 1.0, 1)


class ChatClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        self.calls.append(messages)
        return ChatResult("Escucha antes de proponer [S1].", "qwen3.5:4b", 10.0, 20, 8)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        root=tmp_path,
        base_url="http://127.0.0.1:11434",
        chat_model="qwen3.5:4b",
        embedding_model="test-embedding:v1",
        embedding_dimensions=3,
        embedding_batch_size=2,
        timeout_seconds=10,
        index_path=tmp_path / ".local" / "data" / "index.sqlite3",
        runs_dir=tmp_path / ".local" / "runs",
        top_k=3,
        chunk_chars=400,
        retrieval_mode="hybrid",
    )


def test_pipeline_uses_hybrid_sources_and_sanitizes_trace(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    source = tmp_path / "input"
    source.mkdir()
    (source / "manual.md").write_text(
        "# Manual\n\nLa escucha consultiva descubre necesidades.\n", encoding="utf-8"
    )
    embedder = Embedder()
    HybridIndex(
        settings.index_path,
        settings.embedding_model,
        settings.embedding_dimensions,
        embedder.profile,
    ).build(source, chunk_chars=400, batch_size=2, embedder=embedder)
    chat = ChatClient()
    output = io.StringIO()
    question = "¿Cómo comprendo al cliente codigo-ultrasecreto?"

    result = run_question(settings, question, embedder=embedder, client=chat, output=output)

    assert result.citation_valid is True
    assert result.sources[0].source_path == "manual.md"
    assert "hybrid" in output.getvalue()
    assert "vector=" in output.getvalue()
    assert validate_run(result.run_path).terminal_event == "run.completed"
    raw = result.run_path.read_text(encoding="utf-8")
    assert question not in raw
    assert chat.calls[0][1]["content"] not in raw
    assert "codigo-ultrasecreto" not in raw

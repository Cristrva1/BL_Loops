from pathlib import Path

import pytest

from sales_agent.embeddings import EmbeddingBatch
from sales_agent.index import HybridSalesIndex, IndexingError, SearchError


class FakeEmbedder:
    model = "fake-embed"
    dimensions = 3
    profile = "test-profile"

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
        vectors = []
        for text in texts:
            lowered = text.casefold()
            if "escuchar" in lowered or "necesidades" in lowered:
                vectors.append((1.0, 0.0, 0.0))
            elif "perspectiva" in lowered:
                vectors.append((0.0, 1.0, 0.0))
            else:
                vectors.append((0.0, 0.0, 1.0))
        return EmbeddingBatch(tuple(vectors), None, None)

    def embed_query(self, text: str) -> EmbeddingBatch:
        if "prioridades" in text.casefold():
            return EmbeddingBatch(((1.0, 0.0, 0.0),), None, None)
        return EmbeddingBatch(((0.0, 1.0, 0.0),), None, None)


def _index(path: Path) -> HybridSalesIndex:
    return HybridSalesIndex(path, "fake-embed", 3, "test-profile")


def test_build_filters_noise_and_hybrid_finds_semantic_paraphrase(
    tmp_path: Path, fixture_corpus: Path
) -> None:
    index = _index(tmp_path / "index.sqlite3")
    stats = index.build(
        fixture_corpus,
        chunk_chars=500,
        batch_size=2,
        embedder=FakeEmbedder(),
    )

    lexical = index.search(
        "comprender prioridades", top_k=3, mode="lexical", embedder=FakeEmbedder()
    )
    hybrid = index.search("comprender prioridades", top_k=3, mode="hybrid", embedder=FakeEmbedder())

    assert stats.discovered_documents == 3
    assert stats.indexed_documents == 2
    assert stats.excluded_sections == 2
    assert lexical == ()
    assert hybrid[0].source_path == "01-ninja.md"


def test_profile_mismatch_rejects_old_index(tmp_path: Path, fixture_corpus: Path) -> None:
    index = _index(tmp_path / "index.sqlite3")
    index.build(fixture_corpus, chunk_chars=500, batch_size=4, embedder=FakeEmbedder())

    incompatible = HybridSalesIndex(index.index_path, "fake-embed", 3, "other-profile")
    with pytest.raises(SearchError, match="perfil"):
        incompatible.current_stats()


def test_failed_rebuild_preserves_previous_index(tmp_path: Path, fixture_corpus: Path) -> None:
    index = _index(tmp_path / "index.sqlite3")
    index.build(fixture_corpus, chunk_chars=500, batch_size=4, embedder=FakeEmbedder())

    class BrokenEmbedder(FakeEmbedder):
        def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
            raise RuntimeError("fallo intencional")

    with pytest.raises(RuntimeError, match="intencional"):
        index.build(fixture_corpus, chunk_chars=500, batch_size=4, embedder=BrokenEmbedder())

    assert index.current_stats().indexed_documents == 2


def test_empty_source_cannot_leave_stale_projection(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.mkdir()

    with pytest.raises(IndexingError, match="Markdown"):
        _index(tmp_path / "index.sqlite3").build(
            source, chunk_chars=500, batch_size=2, embedder=FakeEmbedder()
        )


@pytest.fixture
def fixture_corpus() -> Path:
    return Path(__file__).parents[1] / "fixtures/evaluation-corpus"

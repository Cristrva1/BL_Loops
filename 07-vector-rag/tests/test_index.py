from pathlib import Path

import pytest

from vector_rag.embeddings import EmbeddingBatch
from vector_rag.index import HybridIndex, IndexingError, SearchError


class SemanticEmbedder:
    model = "test-embedding:v1"
    dimensions = 3
    profile = "test-sales-v1"

    @staticmethod
    def _vector(text: str) -> tuple[float, float, float]:
        lowered = text.casefold()
        if "escucha diagnostica" in lowered or "necesidad real" in lowered:
            return (1.0, 0.0, 0.0)
        if "futbol" in lowered or "quarterback" in lowered:
            return (0.0, 1.0, 0.0)
        return (0.0, 0.0, 1.0)

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
        return EmbeddingBatch(tuple(self._vector(text) for text in texts), 1.0, len(texts))

    def embed_query(self, text: str) -> EmbeddingBatch:
        return EmbeddingBatch((self._vector(text),), 1.0, 1)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _index(tmp_path: Path) -> tuple[HybridIndex, SemanticEmbedder, Path]:
    source = tmp_path / "books"
    _write(
        source / "ventas.md",
        "# Venta consultiva\n\n## Descripción Editorial\n"
        "La escucha diagnostica permite formular soluciones sin presión.\n",
    )
    _write(
        source / "ruido.md",
        "# Ficha dudosa\n\n## Contexto (Wikipedia)\n"
        "Un quarterback de futbol ganó muchos campeonatos.\n\n"
        "## Temas (Open Library)\n- Selling\n",
    )
    embedder = SemanticEmbedder()
    index = HybridIndex(
        tmp_path / "index.sqlite3", embedder.model, embedder.dimensions, embedder.profile
    )
    return index, embedder, source


def test_build_filters_noise_and_stores_versioned_vectors(tmp_path: Path) -> None:
    index, embedder, source = _index(tmp_path)

    stats = index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)

    assert stats.discovered_documents == 2
    assert stats.indexed_documents == 1
    assert stats.excluded_sections == 2
    assert stats.embedded_chunks == stats.chunks
    assert stats.embedding_model == "test-embedding:v1"
    assert index.search("quarterback", top_k=3, mode="lexical", embedder=embedder) == []


def test_vector_and_hybrid_recover_a_paraphrase_that_lexical_misses(tmp_path: Path) -> None:
    index, embedder, source = _index(tmp_path)
    index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)

    lexical = index.search("necesidad real", top_k=2, mode="lexical", embedder=embedder)
    vector = index.search("necesidad real", top_k=2, mode="vector", embedder=embedder)
    hybrid = index.search("necesidad real", top_k=2, mode="hybrid", embedder=embedder)

    assert lexical == []
    assert vector[0].source_path == "ventas.md"
    assert vector[0].vector_score == pytest.approx(1.0)
    assert hybrid[0].source_path == "ventas.md"
    assert hybrid[0].vector_rank == 1


def test_rebuild_removes_deleted_content_and_empty_source_preserves_index(tmp_path: Path) -> None:
    index, embedder, source = _index(tmp_path)
    index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)
    (source / "ventas.md").write_text("# Nuevo\n\nContenido neutral.\n", encoding="utf-8")
    index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)
    assert index.search("escucha diagnostica", top_k=2, mode="lexical", embedder=embedder) == []

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(IndexingError, match="ningun archivo Markdown"):
        index.build(empty, chunk_chars=400, batch_size=2, embedder=embedder)
    assert index.current_stats().indexed_documents == 1


def test_index_profile_mismatch_fails_closed(tmp_path: Path) -> None:
    index, embedder, source = _index(tmp_path)
    index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)
    incompatible = HybridIndex(tmp_path / "index.sqlite3", "other:v2", 3, "other-profile")

    with pytest.raises(SearchError, match="perfil de embeddings"):
        incompatible.search("necesidad real", top_k=2, mode="vector", embedder=embedder)


def test_missing_index_and_invalid_mode_are_explained(tmp_path: Path) -> None:
    embedder = SemanticEmbedder()
    missing = HybridIndex(tmp_path / "missing.sqlite3", embedder.model, 3, embedder.profile)

    with pytest.raises(SearchError, match="no existe"):
        missing.search("consulta", top_k=2, mode="hybrid", embedder=embedder)
    index, embedder, source = _index(tmp_path)
    index.build(source, chunk_chars=400, batch_size=2, embedder=embedder)
    with pytest.raises(SearchError, match="Modo"):
        index.search("consulta", top_k=2, mode="magic", embedder=embedder)

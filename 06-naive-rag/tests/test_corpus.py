from pathlib import Path

import pytest

from naive_rag.corpus import CorpusIndex, IndexingError, SearchError


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_build_indexes_markdown_and_returns_line_level_citations(tmp_path: Path) -> None:
    source = tmp_path / "books"
    _write(
        source / "ventas" / "actual.md",
        "# Manual actual\n\n## Seguimiento\n\n"
        "La version vigente exige seguimiento alfa en 24 horas.\n",
    )
    _write(
        source / "ventas" / "otro.md",
        "# Manual complementario\n\nLa propuesta beta confirma el presupuesto antes del envio.\n",
    )
    index = CorpusIndex(tmp_path / "lab" / ".local" / "books.sqlite3")

    stats = index.build(source, chunk_chars=400)
    results = index.search("¿Cuál es el seguimiento alfa vigente?", top_k=3)

    assert stats.discovered_documents == 2
    assert stats.indexed_documents == 2
    assert stats.duplicate_documents == 0
    assert stats.chunks >= 2
    assert results
    assert results[0].source_path == "ventas/actual.md"
    assert results[0].start_line <= 5 <= results[0].end_line
    assert "seguimiento alfa" in results[0].content


def test_exact_duplicate_documents_are_indexed_once(tmp_path: Path) -> None:
    source = tmp_path / "books"
    content = "# Duplicado\n\nLa regla gamma permanece vigente.\n"
    _write(source / "a.md", content)
    _write(source / "sub" / "b.md", content)
    index = CorpusIndex(tmp_path / "index.sqlite3")

    stats = index.build(source, chunk_chars=400)

    assert stats.discovered_documents == 2
    assert stats.indexed_documents == 1
    assert stats.duplicate_documents == 1
    assert len(index.search("regla gamma", top_k=5)) == 1


def test_rebuild_is_an_exact_projection_and_removes_deleted_content(tmp_path: Path) -> None:
    source = tmp_path / "books"
    path = source / "manual.md"
    _write(path, "# Primera\n\nLa palabra antigua es orquidea.\n")
    index = CorpusIndex(tmp_path / "index.sqlite3")
    index.build(source, chunk_chars=400)
    assert index.search("orquidea", top_k=2)

    _write(path, "# Segunda\n\nLa palabra nueva es magnolia.\n")
    index.build(source, chunk_chars=400)

    assert index.search("orquidea", top_k=2) == []
    assert index.search("magnolia", top_k=2)


def test_empty_rebuild_fails_without_destroying_previous_index(tmp_path: Path) -> None:
    source = tmp_path / "books"
    _write(source / "manual.md", "# Manual\n\nExiste la evidencia delta.\n")
    index = CorpusIndex(tmp_path / "index.sqlite3")
    index.build(source, chunk_chars=400)
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(IndexingError, match="ningun archivo Markdown"):
        index.build(empty, chunk_chars=400)

    assert index.search("evidencia delta", top_k=2)


def test_query_punctuation_is_not_interpreted_as_fts_syntax(tmp_path: Path) -> None:
    source = tmp_path / "books"
    _write(source / "manual.md", "# Manual\n\nLa tecnica zeta responde preguntas complejas.\n")
    index = CorpusIndex(tmp_path / "index.sqlite3")
    index.build(source, chunk_chars=400)

    results = index.search('¿"técnica" zeta: preguntas?', top_k=2)

    assert results
    assert "tecnica zeta" in results[0].content


def test_search_rejects_empty_or_missing_index(tmp_path: Path) -> None:
    missing = CorpusIndex(tmp_path / "missing.sqlite3")
    with pytest.raises(SearchError, match="no existe"):
        missing.search("algo", top_k=2)

    source = tmp_path / "books"
    _write(source / "manual.md", "# Manual\n\nContenido util.\n")
    index = CorpusIndex(tmp_path / "index.sqlite3")
    index.build(source, chunk_chars=400)
    with pytest.raises(SearchError, match="palabras buscables"):
        index.search("¿? --", top_k=2)


def test_symlinked_markdown_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "books"
    source.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Externo\n\nNo debe leerse.\n", encoding="utf-8")
    link = source / "link.md"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Este entorno de Windows no permite crear symlinks sin privilegios.")

    with pytest.raises(IndexingError, match="enlace simbolico"):
        CorpusIndex(tmp_path / "index.sqlite3").build(source, chunk_chars=400)

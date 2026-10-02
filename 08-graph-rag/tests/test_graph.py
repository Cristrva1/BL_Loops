from pathlib import Path

import pytest

from graph_rag.graph import GraphIndex, IndexingError, SearchError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "evaluation-corpus"
MULTI_HOP_QUESTION = "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _tiny_corpus(root: Path) -> Path:
    source = root / "corpus"
    _write(
        source / "manual.md",
        "# Manual\n\n"
        "- `Ana Ruiz` --owns--> `AtlasCRM`\n"
        "- `AtlasCRM` --depends_on--> `NortePay`\n"
        "- `NortePay` --freeze_date--> `2026-03-01`\n",
    )
    return source


def test_build_stores_extracted_edges_not_inferred_ones(tmp_path: Path) -> None:
    index = GraphIndex(tmp_path / "graph.sqlite3")
    stats = index.build(_tiny_corpus(tmp_path), chunk_chars=400)

    assert stats.indexed_documents == 1
    assert stats.extracted_edges == 3
    assert stats.nodes == 4
    assert index.stored_origins() == ("extracted",)


def test_multihop_path_marks_extracted_hops_and_one_inferred_edge(tmp_path: Path) -> None:
    index = GraphIndex(tmp_path / "graph.sqlite3")
    index.build(_tiny_corpus(tmp_path), chunk_chars=400)

    retrieval = index.search_graph(MULTI_HOP_QUESTION, max_hops=3)
    longest = max(retrieval.paths, key=lambda item: len(item.hops))

    assert retrieval.seeds == ("Ana Ruiz",)
    assert [hop.object for hop in longest.hops] == ["AtlasCRM", "NortePay", "2026-03-01"]
    assert all(hop.origin == "extracted" for hop in longest.hops)
    assert longest.inferred is not None
    assert longest.inferred.origin == "inferred"
    assert longest.inferred.subject == "Ana Ruiz"
    assert longest.inferred.object == "2026-03-01"
    assert longest.inferred.hops == 3
    assert longest.inferred.predicate == "owns/depends_on/freeze_date"


def test_evaluation_fixture_connects_documents_that_lexical_search_misses(
    tmp_path: Path,
) -> None:
    index = GraphIndex(tmp_path / "graph.sqlite3")
    index.build(FIXTURES, chunk_chars=400)
    bundle = index.search(MULTI_HOP_QUESTION, top_k=4, mode="compare", max_hops=3)

    assert bundle.graph is not None
    longest = max(bundle.graph.paths, key=lambda item: len(item.hops))
    graph_docs = {hop.source_path for hop in longest.hops}
    lexical_docs = {hit.source_path for hit in bundle.lexical}

    assert graph_docs == {"01-personas.md", "02-proyectos.md", "03-proveedores.md"}
    assert longest.hops[-1].object == "2026-03-01"
    assert "02-proyectos.md" not in lexical_docs
    assert any(hop.origin == "extracted" for hop in longest.hops)
    assert longest.inferred is not None
    assert longest.inferred.origin == "inferred"


def test_reverse_traversal_answers_who_owns_a_seed_object(tmp_path: Path) -> None:
    index = GraphIndex(tmp_path / "graph.sqlite3")
    index.build(_tiny_corpus(tmp_path), chunk_chars=400)

    retrieval = index.search_graph("¿Quién es responsable de AtlasCRM?", max_hops=1)
    hops = [hop for path in retrieval.paths for hop in path.hops]

    assert retrieval.seeds == ("AtlasCRM",)
    assert any(
        hop.direction == "reverse" and hop.object == "Ana Ruiz" and hop.predicate == "owns"
        for hop in hops
    )


def test_empty_rebuild_fails_without_destroying_previous_index(tmp_path: Path) -> None:
    index = GraphIndex(tmp_path / "graph.sqlite3")
    index.build(_tiny_corpus(tmp_path), chunk_chars=400)
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(IndexingError, match="ningun archivo Markdown"):
        index.build(empty, chunk_chars=400)

    assert index.search_graph("Ana Ruiz", max_hops=1).paths


def test_corpus_without_triples_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "plain"
    _write(source / "nota.md", "# Nota\n\nSolo prosa, ninguna arista visible.\n")
    index = GraphIndex(tmp_path / "graph.sqlite3")

    with pytest.raises(IndexingError, match="ninguna arista"):
        index.build(source, chunk_chars=400)


def test_symlink_corpus_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    source.mkdir()
    real = tmp_path / "real.md"
    real.write_text("# Real\n\n- `A` --owns--> `B`\n", encoding="utf-8")
    link = source / "link.md"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("El sistema no permite crear enlaces simbolicos.")
    index = GraphIndex(tmp_path / "graph.sqlite3")

    with pytest.raises(IndexingError, match="enlace simbolico"):
        index.build(source, chunk_chars=400)


def test_missing_index_explains_the_index_command(tmp_path: Path) -> None:
    index = GraphIndex(tmp_path / "missing.sqlite3")

    with pytest.raises(SearchError, match="graph-rag index"):
        index.search_graph("Ana Ruiz", max_hops=2)

import io
from pathlib import Path

import pytest

from naive_rag import cli as cli_module
from naive_rag.config import Settings
from naive_rag.corpus import CorpusIndex


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        root=tmp_path,
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        timeout_seconds=10,
        index_path=tmp_path / ".local" / "data" / "books.sqlite3",
        runs_dir=tmp_path / ".local" / "runs",
        top_k=3,
        chunk_chars=400,
    )


@pytest.fixture
def indexed_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    settings = _settings(tmp_path)
    source = tmp_path / "input"
    source.mkdir()
    (source / "manual.md").write_text(
        "# Manual\n\nLa regla omega exige confirmar presupuesto antes de proponer.\n",
        encoding="utf-8",
    )
    CorpusIndex(settings.index_path).build(source, chunk_chars=400)
    monkeypatch.setattr(cli_module.Settings, "load", classmethod(lambda cls: settings))
    return settings


def test_search_shows_citable_context_without_calling_ollama(
    indexed_settings: Settings,
) -> None:
    output = io.StringIO()

    exit_code = cli_module.cli(["search", "regla", "omega"], output=output)

    text = output.getvalue()
    assert exit_code == 0
    assert "Ollama no se invoca" in text
    assert "[S1] manual.md:L3-L3" in text
    assert "La regla omega exige confirmar presupuesto" in text
    assert not indexed_settings.runs_dir.exists()


def test_search_without_lexical_matches_explains_the_abstention(
    indexed_settings: Settings,
) -> None:
    output = io.StringIO()

    exit_code = cli_module.cli(["search", "zzzz"], output=output)

    assert exit_code == 0
    assert "se abstendria sin llamar al modelo" in output.getvalue()


def test_search_requires_an_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(tmp_path)
    monkeypatch.setattr(cli_module.Settings, "load", classmethod(lambda cls: settings))
    errors = io.StringIO()

    exit_code = cli_module.cli(["search", "regla"], output=io.StringIO(), error_output=errors)

    assert exit_code == 1
    assert "naive-rag index --source" in errors.getvalue()

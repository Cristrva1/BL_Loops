import io
from pathlib import Path

from naive_rag.config import Settings
from naive_rag.corpus import CorpusIndex
from naive_rag.ollama_client import ChatResult
from naive_rag.pipeline import run_question
from naive_rag.validation import validate_run


class CitingClient:
    def __init__(self, answer: str = "La regla exige confirmar presupuesto [S1].") -> None:
        self.answer = answer
        self.calls: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        self.calls.append(messages)
        return ChatResult(
            content=self.answer,
            model="qwen3.5:4b",
            total_duration_ms=20.0,
            prompt_tokens=90,
            output_tokens=12,
        )


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


def _build_index(settings: Settings) -> None:
    source = settings.root / "input"
    source.mkdir()
    (source / "manual.md").write_text(
        "# Manual\n\nLa regla omega exige confirmar presupuesto antes de proponer.\n",
        encoding="utf-8",
    )
    CorpusIndex(settings.index_path).build(source, chunk_chars=400)


def test_pipeline_shows_real_nodes_cites_sources_and_sanitizes_jsonl(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    client = CitingClient()
    output = io.StringIO()
    secret_question = "¿Qué exige la regla omega codigo-secreto-123?"

    result = run_question(settings, secret_question, client=client, output=output)

    assert len(client.calls) == 1
    assert result.abstained is False
    assert result.citation_check.valid is True
    assert result.sources[0].source_path == "manual.md"
    rendered = output.getvalue()
    assert "[1/3 buscar] queued -> running -> done" in rendered
    assert "[2/3 aumentar] running -> done" in rendered
    assert "[3/3 generar] waiting -> done" in rendered
    assert "manual.md:L" in rendered

    summary = validate_run(result.run_path)
    raw_log = result.run_path.read_text(encoding="utf-8")
    assert summary.terminal_event == "run.completed"
    assert secret_question not in raw_log
    assert client.answer not in raw_log
    assert "codigo-secreto-123" not in raw_log


def test_pipeline_abstains_without_calling_ollama_when_fts_has_no_match(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    client = CitingClient()
    output = io.StringIO()

    result = run_question(settings, "xilofono", client=client, output=output)

    assert client.calls == []
    assert result.abstained is True
    assert "No encontre fragmentos" in result.answer
    assert "[3/3 generar] skipped" in output.getvalue()
    assert validate_run(result.run_path).terminal_event == "run.completed"


def test_pipeline_reports_missing_citations_without_inventing_them(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    output = io.StringIO()

    result = run_question(
        settings,
        "regla omega",
        client=CitingClient("La regla exige confirmar presupuesto."),
        output=output,
    )

    assert result.citation_check.valid is False
    assert "ADVERTENCIA: la respuesta no uso citas validas" in output.getvalue()

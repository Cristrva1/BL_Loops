import io
from pathlib import Path

from graph_rag.config import Settings
from graph_rag.graph import GraphIndex
from graph_rag.ollama_client import ChatResult
from graph_rag.pipeline import run_question
from graph_rag.validation import validate_run


class CitingClient:
    def __init__(self, answer: str = "La congelacion de NortePay es 2026-03-01 [S1].") -> None:
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


def _settings(tmp_path: Path, mode: str = "graph") -> Settings:
    return Settings(
        root=tmp_path,
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        timeout_seconds=10,
        index_path=tmp_path / ".local" / "data" / "graph.sqlite3",
        runs_dir=tmp_path / ".local" / "runs",
        top_k=4,
        chunk_chars=400,
        max_hops=3,
        retrieval_mode=mode,
    )


def _build_index(settings: Settings) -> None:
    source = settings.root / "input"
    source.mkdir()
    (source / "manual.md").write_text(
        "# Manual\n\n"
        "- `Ana Ruiz` --owns--> `AtlasCRM`\n"
        "- `AtlasCRM` --depends_on--> `NortePay`\n"
        "- `NortePay` --freeze_date--> `2026-03-01`\n",
        encoding="utf-8",
    )
    GraphIndex(settings.index_path).build(source, chunk_chars=400)


def test_pipeline_shows_path_distinguishes_origins_and_sanitizes_jsonl(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    client = CitingClient()
    output = io.StringIO()
    secret_question = "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz codigo-secreto-123?"

    result = run_question(settings, secret_question, client=client, output=output)

    assert len(client.calls) == 1
    assert result.citation_valid is True
    assert result.abstained is False
    rendered = output.getvalue()
    assert "[1/3 recorrer]" in rendered
    assert "Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01" in (
        rendered
    )
    assert "extracted" in rendered
    assert "inferred" in rendered
    assert "graph LR" in rendered

    summary = validate_run(result.run_path)
    raw_log = result.run_path.read_text(encoding="utf-8")
    assert summary.terminal_event == "run.completed"
    assert secret_question not in raw_log
    assert client.answer not in raw_log
    assert "codigo-secreto-123" not in raw_log
    assert "Ana Ruiz" not in raw_log


def test_pipeline_abstains_without_calling_ollama_when_graph_has_no_seed(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    client = CitingClient()
    output = io.StringIO()

    result = run_question(settings, "xilofono", client=client, output=output)

    assert client.calls == []
    assert result.abstained is True
    assert "No encontre una ruta" in result.answer
    assert "[3/3 generar] skipped" in output.getvalue()
    assert validate_run(result.run_path).terminal_event == "run.completed"


def test_pipeline_reports_missing_citations_without_inventing_them(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _build_index(settings)
    output = io.StringIO()

    result = run_question(
        settings,
        "proyecto de Ana Ruiz",
        client=CitingClient("La fecha es 2026-03-01."),
        output=output,
    )

    assert result.citation_valid is False
    assert "ADVERTENCIA: la respuesta no uso citas validas" in output.getvalue()


def test_compare_mode_prints_lexical_contrast_but_answers_from_the_graph(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path, mode="compare")
    _build_index(settings)
    client = CitingClient()
    output = io.StringIO()

    result = run_question(
        settings,
        "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?",
        client=client,
        output=output,
    )

    rendered = output.getvalue()
    assert result.abstained is False
    assert "comparacion lexica" in rendered.casefold() or "lexical" in rendered
    assert "extracted" in rendered
    assert len(client.calls) == 1

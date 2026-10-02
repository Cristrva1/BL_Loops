import json
from pathlib import Path


def test_runtime_is_autonomous_and_not_driven_by_human_docs() -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((root / "src").rglob("*.py"))
    ).replace("\\", "/")

    assert "docs/humano" not in runtime
    assert "06-naive-rag" not in runtime
    assert "07-vector-rag" not in runtime
    assert "09-agentic-rag" not in runtime
    assert "02-single-agent" not in runtime
    assert "neo4j" not in runtime.casefold()
    assert "microsoft" not in runtime.casefold()


def test_required_documents_contract_and_fixture_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = {
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "METHODOLOGY.md",
        "EXERCISES.md",
        "TROUBLESHOOTING.md",
        "EVALUATION.md",
    }
    actual = {path.name for path in (root / "docs" / "humano").glob("*.md")}
    schema = json.loads((root / "contracts" / "run-event.schema.json").read_text(encoding="utf-8"))

    assert expected.issubset(actual)
    assert schema["properties"]["lab_id"]["const"] == "08-graph-rag"
    assert schema["properties"]["case_id"]["const"] == "A-RAG-GRAPH-001@0.1.0"
    assert len(list((root / "fixtures" / "evaluation-corpus").glob("*.md"))) == 5

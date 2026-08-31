import json
from pathlib import Path


def test_runtime_does_not_depend_on_human_docs_or_another_lab() -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((root / "src").rglob("*.py"))
    )
    normalized = runtime.replace("\\", "/")

    assert "docs/humano" not in normalized
    assert "02-single-agent" not in runtime
    assert "01-prompt-agent-factory" not in runtime


def test_required_human_documents_contract_and_fixture_are_present() -> None:
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
    fixture_documents = list((root / "fixtures" / "evaluation-corpus").glob("*.md"))

    assert expected.issubset(actual)
    assert schema["properties"]["lab_id"]["const"] == "06-naive-rag"
    assert len(fixture_documents) == 5

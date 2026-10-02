from __future__ import annotations

import json
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[2]
HUMAN_DOCS = {
    "README.md",
    "QUICKSTART.md",
    "ARCHITECTURE.md",
    "METHODOLOGY.md",
    "EXERCISES.md",
    "TROUBLESHOOTING.md",
    "EVALUATION.md",
}
OTHER_LABS = (
    "01-prompt-agent-factory",
    "02-single-agent",
    "03-orchestration",
    "06-naive-rag",
    "07-vector-rag",
    "09-agentic-rag",
    "13-sales-knowledge-curator",
    "14-local-code-hermes",
)


def test_human_documentation_has_its_own_folder() -> None:
    docs_dir = LAB_ROOT / "docs" / "humano"

    assert docs_dir.is_dir()
    assert {path.name for path in docs_dir.glob("*.md")} >= HUMAN_DOCS


def test_runtime_does_not_depend_on_human_docs_or_another_lab() -> None:
    runtime_files = [
        *list((LAB_ROOT / "backend" / "src").rglob("*.py")),
        *list((LAB_ROOT / "frontend" / "src").rglob("*.ts")),
        *list((LAB_ROOT / "frontend" / "src").rglob("*.tsx")),
    ]

    for path in runtime_files:
        content = path.read_text(encoding="utf-8").replace("\\", "/").casefold()
        assert "docs/humano" not in content, f"El runtime depende de documentacion: {path}"
        for lab in OTHER_LABS:
            assert lab not in content, f"El runtime menciona otro laboratorio: {path}"


def test_run_event_schema_belongs_to_this_lab() -> None:
    schema_path = LAB_ROOT / "contracts" / "run-event.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["properties"]["lab_id"]["const"] == "04-parallel-agents"

from __future__ import annotations

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
    "CONTRACTS.md",
}


def test_human_documentation_has_its_own_folder() -> None:
    docs_dir = LAB_ROOT / "docs" / "humano"

    assert docs_dir.is_dir()
    assert {path.name for path in docs_dir.glob("*.md")} >= HUMAN_DOCS


def test_runtime_does_not_depend_on_human_documentation() -> None:
    runtime_files = [
        *list((LAB_ROOT / "backend" / "src").rglob("*.py")),
        *list((LAB_ROOT / "frontend" / "src").rglob("*.ts")),
        *list((LAB_ROOT / "frontend" / "src").rglob("*.tsx")),
    ]

    for path in runtime_files:
        content = path.read_text(encoding="utf-8").replace("\\", "/").casefold()
        assert "docs/humano" not in content, f"El runtime depende de documentación: {path}"

from pathlib import Path


def test_runtime_does_not_import_other_labs_or_human_docs() -> None:
    root = Path(__file__).parents[1]
    runtime = "\n".join(
        path.read_text(encoding="utf-8") for path in (root / "src/sales_agent").glob("*.py")
    )

    assert "vector_rag" not in runtime
    assert "06-naive-rag" not in runtime
    assert "07-vector-rag" not in runtime
    assert "docs/humano" not in runtime


def test_portable_human_contract_is_complete() -> None:
    root = Path(__file__).parents[1]
    required = {
        root / "README.md",
        root / "AGENTS.md",
        root / "docs/humano/README.md",
        root / "docs/humano/QUICKSTART.md",
        root / "docs/humano/ARCHITECTURE.md",
        root / "docs/humano/METHODOLOGY.md",
        root / "docs/humano/EXERCISES.md",
        root / "docs/humano/TROUBLESHOOTING.md",
        root / "docs/humano/EVALUATION.md",
        root / "contracts/run-event.schema.json",
    }

    assert all(path.is_file() for path in required)

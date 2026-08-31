from __future__ import annotations

import ast
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_autonomous_lab_files_are_present() -> None:
    required = {
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / ".env.example",
        ROOT / ".gitignore",
        ROOT / "Modelfile",
        ROOT / "pyproject.toml",
        ROOT / "contracts" / "run-event.schema.json",
        ROOT / "cases" / "B-CODE-003" / "manifest.json",
    }
    assert not {path.relative_to(ROOT).as_posix() for path in required if not path.is_file()}


def test_full_human_document_contract_is_present() -> None:
    expected = {
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "METHODOLOGY.md",
        "EXERCISES.md",
        "TROUBLESHOOTING.md",
        "EVALUATION.md",
    }
    actual = {path.name for path in (ROOT / "docs" / "humano").glob("*.md")}

    assert expected <= actual


def test_runtime_uses_only_stdlib_and_its_own_package() -> None:
    unexpected: set[str] = set()
    allowed = set(sys.stdlib_module_names) | {"__future__", "local_code_hermes"}
    for path in (ROOT / "src" / "local_code_hermes").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = (alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = (node.module.split(".", 1)[0],)
            else:
                continue
            unexpected.update(name for name in names if name not in allowed)

    assert unexpected == set()


def test_runtime_does_not_import_docs_or_other_laboratories() -> None:
    runtime = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "src" / "local_code_hermes").glob("*.py"))
    ).replace("\\", "/")

    assert "docs/humano" not in runtime
    assert "02-single-agent" not in runtime
    assert "01-prompt-agent-factory" not in runtime
    assert "06-naive-rag" not in runtime
    assert "07-vector-rag" not in runtime
    assert "09-agentic-rag" not in runtime


def test_pyproject_is_python_312_stdlib_runtime_with_dev_only_tools() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["requires-python"] == ">=3.12,<3.13"
    assert project["project"]["dependencies"] == []
    assert {item.split(">", 1)[0] for item in project["dependency-groups"]["dev"]} == {
        "pytest",
        "ruff",
    }


def test_modelfile_is_the_exact_small_profile_requested() -> None:
    lines = [
        line.strip()
        for line in (ROOT / "Modelfile").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert lines == ["FROM qwen3.5:9b", "PARAMETER num_ctx 65536"]


def test_json_schema_is_local_1_1_extension_with_blocked_terminal() -> None:
    schema = json.loads((ROOT / "contracts" / "run-event.schema.json").read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema_version"]["const"] == "1.1"
    assert schema["properties"]["lab_id"]["const"] == "14-local-code-hermes"
    assert schema["properties"]["case_id"]["const"] == "F-LOCAL-CODE-004@0.1.0"
    assert {"run.completed", "run.blocked", "run.failed"} <= set(
        schema["properties"]["event_type"]["enum"]
    )


def test_no_automated_hermes_agent_launch_exists_in_runtime() -> None:
    preflight = (ROOT / "src" / "local_code_hermes" / "preflight.py").read_text(encoding="utf-8")

    assert '("hermes", "--version")' in preflight
    assert "hermes run" not in preflight.lower()
    assert "--yes" not in preflight.lower()
    assert "--non-interactive" not in preflight.lower()


def test_example_environment_contains_no_secret_values() -> None:
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assignments = [
        line.split("=", 1)
        for line in text.splitlines()
        if line and not line.startswith("#") and "=" in line
    ]

    assert all(not value or "replace" not in value.lower() for _, value in assignments)
    assert not any(
        name.upper() in {"API_KEY", "TOKEN", "PASSWORD", "SECRET"} for name, _ in assignments
    )


def test_fixture_sources_are_synthetic_and_free_of_contact_data() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "cases" / "B-CODE-003" / "project").rglob("*"))
        if path.is_file() and path.suffix in {".md", ".py"}
    )

    assert "@example.com" not in text.lower()
    assert "+52" not in text
    assert "api_key" not in text.lower()
    assert "bearer " not in text.lower()

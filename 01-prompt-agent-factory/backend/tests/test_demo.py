from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from prompt_agent_factory import demo


@pytest.fixture(autouse=True)
def isolated_exports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirige la exportación para que la prueba no escriba en `.local/exports`."""

    exports = tmp_path / "exports"
    real_export = demo.export_artifact
    monkeypatch.setattr(demo, "export_artifact", lambda artifact: real_export(artifact, exports))
    return exports


def test_every_example_intake_is_valid_json_and_listed() -> None:
    output = io.StringIO()

    assert demo.cli(["--list"], output=output) == 0

    listed = output.getvalue()
    for path in sorted(demo.examples_dir().glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        assert path.name in listed


def test_default_demo_keeps_the_original_prompt_example(isolated_exports: Path) -> None:
    output = io.StringIO()

    assert demo.cli([], output=output) == 0

    text = output.getvalue()
    assert "Briefing: prompt_duplicate_finder.json" in text
    assert "Tipo: prompt" in text
    assert len(list(isolated_exports.glob("prompt_*.json"))) == 1


def test_skill_example_builds_a_skill(isolated_exports: Path) -> None:
    output = io.StringIO()

    assert demo.cli(["--intake", "skill_meeting_minutes.json"], output=output) == 0

    assert "Tipo: skill" in output.getvalue()
    assert len(list(isolated_exports.glob("skill_*.json"))) == 1


def test_incomplete_example_shows_guided_questions_without_exporting(
    isolated_exports: Path,
) -> None:
    output = io.StringIO()

    assert demo.cli(["--intake", "incomplete_agent_brief.json"], output=output) == 1

    text = output.getvalue()
    assert "Briefing incompleto" in text
    assert "[tools_confirmed]" in text
    assert "No se construyó ni exportó ningún artefacto." in text
    assert not isolated_exports.exists()


def test_all_examples_report_one_expected_incomplete_brief(isolated_exports: Path) -> None:
    output = io.StringIO()

    assert demo.cli(["--all"], output=output) == 0

    assert "1 incompleto" in output.getvalue()
    assert "0 inválidos" in output.getvalue()


def test_invalid_brief_explains_each_validation_error(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text('{"artifact_type": "prompt", "idea": "corta"}', encoding="utf-8")
    output = io.StringIO()

    assert demo.cli(["--intake", str(broken)], output=output) == 2

    assert "Briefing inválido" in output.getvalue()
    assert "idea" in output.getvalue()

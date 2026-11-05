from __future__ import annotations

import io
from pathlib import Path

from orchestration.score_cli import cli

LAB_ROOT = Path(__file__).resolve().parents[2]
GUIDES = LAB_ROOT / "examples" / "guides"


def test_example_guides_cover_pass_and_fail_cases() -> None:
    output = io.StringIO()

    exit_code = cli([str(GUIDES / "*.md")], output=output)

    text = output.getvalue()
    assert exit_code == 1
    assert "guia-aprobada.md: passed=True checks=9/9" in text
    assert "guia-con-fallos.md: passed=False checks=7/9" in text
    assert "NO  no_cloud_fallback    Aparece 'openai'." in text
    assert "poema-fuera-de-caso.md: passed=False checks=1/9" in text


def test_a_passing_guide_returns_zero() -> None:
    assert cli([str(GUIDES / "guia-aprobada.md")], output=io.StringIO()) == 0


def test_missing_file_is_reported(tmp_path: Path) -> None:
    errors = io.StringIO()

    exit_code = cli([str(tmp_path / "no-existe.md")], output=io.StringIO(), error_output=errors)

    assert exit_code == 2
    assert "No existe el archivo" in errors.getvalue()

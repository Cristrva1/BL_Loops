from __future__ import annotations

import io
from pathlib import Path

from agent_loops.score_cli import cli

LAB_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = LAB_ROOT / "examples" / "outputs"


def test_example_outputs_show_the_score_ladder() -> None:
    output = io.StringIO()

    exit_code = cli([str(OUTPUTS / "*")], output=output)

    text = output.getvalue()
    assert exit_code == 1
    assert "salida-debil.txt: passed=False checks=0/5" in text
    assert "salida-parcial.json: passed=False checks=2/5" in text
    assert "salida-completa.json: passed=True checks=5/5" in text


def test_a_complete_output_returns_zero() -> None:
    assert cli([str(OUTPUTS / "salida-completa.json")], output=io.StringIO()) == 0


def test_missing_file_is_reported(tmp_path: Path) -> None:
    errors = io.StringIO()

    exit_code = cli([str(tmp_path / "no-existe.txt")], output=io.StringIO(), error_output=errors)

    assert exit_code == 2
    assert "No existe el archivo" in errors.getvalue()

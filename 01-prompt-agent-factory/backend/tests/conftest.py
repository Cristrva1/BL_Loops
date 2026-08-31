from __future__ import annotations

from pathlib import Path

import pytest
from prompt_agent_factory.api_models import FactoryIntake

LAB_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def prompt_intake() -> FactoryIntake:
    path = LAB_ROOT / "examples" / "intakes" / "prompt_duplicate_finder.json"
    return FactoryIntake.model_validate_json(path.read_text(encoding="utf-8"))


@pytest.fixture
def agent_intake() -> FactoryIntake:
    path = LAB_ROOT / "examples" / "intakes" / "agent_local_reader.json"
    return FactoryIntake.model_validate_json(path.read_text(encoding="utf-8"))

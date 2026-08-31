from __future__ import annotations

from pathlib import Path

import pytest

from sales_curator.config import Settings, lab_root
from sales_curator.orchestration.service import CuratorService

LAB_ROOT = Path(__file__).resolve().parents[2]
CORPUS = LAB_ROOT / "fixtures" / "corpus"


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    base = Settings()
    data = tmp_path / "data"
    runs = tmp_path / "runs"
    data.mkdir()
    runs.mkdir()
    return base.with_isolated_dirs(data, runs)


@pytest.fixture
def service(settings: Settings) -> CuratorService:
    curator = CuratorService(settings)
    yield curator
    curator.close()


@pytest.fixture
def corpus() -> Path:
    return CORPUS


def test_lab_root_matches() -> None:
    assert lab_root() == LAB_ROOT

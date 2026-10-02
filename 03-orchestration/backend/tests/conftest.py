from __future__ import annotations

from pathlib import Path

import pytest

from orchestration.config import Settings
from orchestration.store import STORE


@pytest.fixture
def lab_settings(tmp_path: Path) -> Settings:
    root = tmp_path / "lab"
    root.mkdir()
    return Settings(
        root=root,
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        timeout_seconds=5,
        runs_dir=root / ".local" / "runs",
        artifacts_dir=root / ".local" / "artifacts",
    )


@pytest.fixture(autouse=True)
def reset_store() -> None:
    STORE.reset()

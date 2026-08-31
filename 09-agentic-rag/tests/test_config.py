from pathlib import Path

import pytest

from sales_agent.config import ConfigurationError, Settings


def test_settings_keep_runtime_artifacts_inside_lab(tmp_path: Path) -> None:
    settings = Settings.load(tmp_path)

    assert settings.index_path == (tmp_path / ".local/data/sales-library.sqlite3").resolve()
    assert settings.runs_dir == (tmp_path / ".local/runs").resolve()
    assert settings.history_turns == 4


@pytest.mark.parametrize(
    "line",
    [
        "OLLAMA_BASE_URL=https://api.example.com",
        "OLLAMA_BASE_URL=http://192.168.1.7:11434",
        "SALES_AGENT_CHAT_MODEL=remote-cloud",
        "SALES_AGENT_INDEX_PATH=../shared.sqlite3",
    ],
)
def test_settings_fail_closed_for_remote_or_escaping_configuration(
    tmp_path: Path, line: str
) -> None:
    (tmp_path / ".env").write_text(f"{line}\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        Settings.load(tmp_path)


def test_lab_env_overrides_root_env_without_exposing_values(tmp_path: Path) -> None:
    root = tmp_path / "09-agentic-rag"
    root.mkdir()
    (tmp_path / ".env").write_text("SALES_AGENT_TOP_K=2\n", encoding="utf-8")
    (root / ".env").write_text("SALES_AGENT_TOP_K=6\n", encoding="utf-8")

    assert Settings.load(root).top_k == 6

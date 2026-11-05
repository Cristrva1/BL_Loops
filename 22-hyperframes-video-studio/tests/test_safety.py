"""Garantías de seguridad y honestidad del estudio: endpoint local, fallback visible y medición."""

import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from hyperframes_studio import renderer as renderer_module
from hyperframes_studio.config import ConfigurationError, Settings
from hyperframes_studio.ollama_client import DEFAULT_SCENES, OllamaVideoDirector
from hyperframes_studio.orchestrator import HyperFramesOrchestrator
from hyperframes_studio.renderer import HyperFramesRenderer
from hyperframes_studio.schemas import RenderResult, VideoBrief

RELEVANT = ("OLLAMA_BASE_URL", "OLLAMA_MODEL", "BL_LOOPS_MODEL_STANDARD", "HOST", "PORT")


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in RELEVANT:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_defaults_are_local(clean_env: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = Settings.load(tmp_path / "lab")

    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.ollama_model == "qwen3.5:9b"
    assert (settings.host, settings.port) == ("127.0.0.1", 8022)


def test_lab_env_overrides_workspace_env_key_by_key(
    clean_env: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    lab = tmp_path / "lab"
    lab.mkdir()
    (tmp_path / ".env").write_text("BL_LOOPS_MODEL_STANDARD=qwen3.5:4b\nPORT=9022\n", encoding="utf-8")
    (lab / ".env").write_text("PORT=9122\n", encoding="utf-8")

    settings = Settings.load(lab)

    assert settings.ollama_model == "qwen3.5:4b"
    assert settings.port == 9122


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("OLLAMA_BASE_URL", "http://example.com:11434", "HTTP local"),
        ("OLLAMA_BASE_URL", "https://127.0.0.1:11434", "HTTP local"),
        ("OLLAMA_MODEL", "qwen3.5:cloud", "no cloud"),
        ("HOST", "0.0.0.0", "HOST debe ser"),
    ],
)
def test_unsafe_configuration_is_rejected(
    clean_env: pytest.MonkeyPatch, tmp_path: Path, name: str, value: str, message: str
) -> None:
    clean_env.setenv(name, value)

    with pytest.raises(ConfigurationError, match=message):
        Settings.load(tmp_path / "lab")


async def test_director_reports_fallback_source() -> None:
    director = OllamaVideoDirector(base_url="http://127.0.0.1:9", model="no-existe")

    scenes = await director.generate_scenes(VideoBrief(target_duration=10.0))

    assert len(scenes) == len(DEFAULT_SCENES)
    assert director.last_source == "fallback"
    assert director.last_fallback_reason


async def test_orchestrator_publishes_the_fallback_as_event_and_metric(tmp_path: Path) -> None:
    orch = HyperFramesOrchestrator(workspace_dir=str(tmp_path / "workspace"))
    queue = orch.subscribe()

    async def fallback_scenes(brief: VideoBrief):
        orch.director.last_source = "fallback"
        orch.director.last_fallback_reason = "ConnectError al consultar Ollama"
        return list(DEFAULT_SCENES)

    fake_render = RenderResult(
        video_path=str(tmp_path / "mock.mp4"),
        duration=15.0,
        width=1920,
        height=1080,
        fps=30,
        file_size_bytes=50 * 1024,
        render_elapsed_seconds=1.0,
        success=True,
    )
    with (
        patch.object(orch.director, "generate_scenes", new=fallback_scenes),
        patch.object(orch.renderer, "render_video", new=AsyncMock(return_value=fake_render)),
    ):
        await orch.run_pipeline(VideoBrief(target_duration=15.0), output_path=str(tmp_path / "m.mp4"))

    messages = []
    while not queue.empty():
        messages.append((await queue.get()).message)
    assert any(message.startswith("Fallback visible") for message in messages)
    assert orch.last_eval is not None
    assert orch.last_eval.metrics["director_source"] == "fallback"


async def test_missing_npx_fails_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(renderer_module.shutil, "which", lambda _name: None)
    renderer = HyperFramesRenderer(workspace_dir=tmp_path / "workspace")

    result = await renderer.render_video(tmp_path / "out.mp4")

    assert result.success is False
    assert "npx" in (result.error or "")


def test_unprobed_video_has_no_invented_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def missing_ffprobe(*_args, **_kwargs):
        raise FileNotFoundError("ffprobe")

    monkeypatch.setattr(subprocess, "run", missing_ffprobe)
    renderer = HyperFramesRenderer(workspace_dir=tmp_path / "workspace")

    metadata = renderer._probe_video(tmp_path / "video.mp4")

    assert metadata["duration"] == 0.0


def test_panel_assets_and_truthful_status_are_served() -> None:
    from fastapi.testclient import TestClient

    from hyperframes_studio.main import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/styles.css").status_code == 200
    status = client.get("/api/status").json()
    assert isinstance(status["ollama_reachable"], bool)
    assert isinstance(status["npx_available"], bool)

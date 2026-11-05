"""Garantías de seguridad y honestidad del estudio: endpoint local, fallback visible y medición."""

import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from remotion_studio import remotion_renderer as renderer_module
from remotion_studio.config import ConfigurationError, Settings
from remotion_studio.ollama_director import DEFAULT_REMOTION_SCENES, RemotionOllamaDirector
from remotion_studio.orchestrator import RemotionOrchestrator
from remotion_studio.remotion_renderer import RemotionRenderer
from remotion_studio.schemas import RemotionBrief, RenderResult

RELEVANT = ("OLLAMA_BASE_URL", "OLLAMA_MODEL", "BL_LOOPS_MODEL_STANDARD", "HOST", "PORT")


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in RELEVANT:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_defaults_are_local(clean_env: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = Settings.load(tmp_path / "lab")

    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert (settings.host, settings.port) == ("127.0.0.1", 8023)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("OLLAMA_BASE_URL", "http://example.com:11434", "HTTP local"),
        ("OLLAMA_MODEL", "qwen3.5:cloud", "no cloud"),
        ("HOST", "0.0.0.0", "HOST debe ser"),
        ("PORT", "80", "PORT debe estar"),
    ],
)
def test_unsafe_configuration_is_rejected(
    clean_env: pytest.MonkeyPatch, tmp_path: Path, name: str, value: str, message: str
) -> None:
    clean_env.setenv(name, value)

    with pytest.raises(ConfigurationError, match=message):
        Settings.load(tmp_path / "lab")


async def test_director_reports_fallback_and_keeps_exact_frames() -> None:
    director = RemotionOllamaDirector(base_url="http://127.0.0.1:9", model="no-existe")

    scenes = await director.generate_scenes(RemotionBrief(target_duration=12.0, fps=30))

    assert len(scenes) == len(DEFAULT_REMOTION_SCENES)
    assert [scene.start_frame for scene in scenes] == [0, 90, 180, 270]
    assert sum(scene.duration_in_frames for scene in scenes) == 360
    assert director.last_source == "fallback"
    assert director.last_fallback_reason


async def test_orchestrator_publishes_the_fallback_as_event_and_metric(tmp_path: Path) -> None:
    orch = RemotionOrchestrator(root_dir=tmp_path)
    queue = orch.subscribe()
    brief = RemotionBrief(target_duration=12.0, fps=30)
    scenes = await orch.director.generate_scenes(brief)
    fake_render = RenderResult(
        video_path=str(tmp_path / "mock.mp4"),
        duration=12.0,
        width=1920,
        height=1080,
        fps=30,
        total_frames=360,
        file_size_bytes=60 * 1024,
        render_elapsed_seconds=1.0,
        success=True,
    )

    async def fallback_scenes(_brief: RemotionBrief):
        orch.director.last_source = "fallback"
        orch.director.last_fallback_reason = "ConnectError al consultar Ollama"
        return scenes

    with (
        patch.object(orch.director, "generate_scenes", new=fallback_scenes),
        patch.object(orch.renderer, "render_video", new=AsyncMock(return_value=fake_render)),
    ):
        await orch.run_pipeline(brief, output_path=str(tmp_path / "m.mp4"))

    messages = []
    while not queue.empty():
        messages.append((await queue.get()).message)
    assert any(message.startswith("Fallback visible") for message in messages)
    assert orch.last_eval is not None
    assert orch.last_eval.metrics["director_source"] == "fallback"


async def test_missing_npx_fails_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(renderer_module.shutil, "which", lambda _name: None)
    renderer = RemotionRenderer(root_dir=tmp_path)

    result = await renderer.render_video(tmp_path / "out.mp4")

    assert result.success is False
    assert "npx" in (result.error or "")


def test_unprobed_video_has_no_invented_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def missing_ffprobe(*_args, **_kwargs):
        raise FileNotFoundError("ffprobe")

    monkeypatch.setattr(subprocess, "run", missing_ffprobe)

    metadata = RemotionRenderer(root_dir=tmp_path)._probe_video(tmp_path / "video.mp4")

    assert metadata["duration"] == 0.0
    assert metadata["nb_frames"] == 0


def test_panel_assets_and_truthful_status_are_served() -> None:
    from fastapi.testclient import TestClient

    from remotion_studio.main import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/styles.css").status_code == 200
    status = client.get("/api/status").json()
    assert isinstance(status["ollama_reachable"], bool)
    assert isinstance(status["npx_available"], bool)

"""Regresiones de la API: contrato del brief, una corrida a la vez y medición sin invenciones."""

import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from remotion_studio.remotion_renderer import RemotionRenderer
from remotion_studio.schemas import RemotionBrief, RemotionScene


def test_briefs_reject_cloud_models_and_impossible_durations() -> None:
    with pytest.raises(ValidationError, match="no cloud"):
        RemotionBrief(model="gpt-oss:120b-cloud")
    with pytest.raises(ValidationError):
        RemotionBrief(target_duration=0.5)


def test_probe_without_a_video_stream_reports_zeros(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audio_only = {"format": {"duration": "12.0"}, "streams": [{"codec_type": "audio"}]}

    def fake_ffprobe(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(audio_only))

    monkeypatch.setattr(subprocess, "run", fake_ffprobe)
    renderer = RemotionRenderer(root_dir=tmp_path)

    assert renderer._probe_video(tmp_path / "video.mp4") == {
        "duration": 12.0,
        "width": 0,
        "height": 0,
        "fps": 0,
        "nb_frames": 0,
    }


@pytest.fixture
def api():
    from remotion_studio import main

    return main, TestClient(main.app)


def test_pipeline_rejects_cloud_models_with_422(api) -> None:
    _main, client = api

    response = client.post("/api/pipeline/run", json={"model": "qwen3.5:cloud"})

    assert response.status_code == 422


def test_pipeline_refuses_a_second_run_while_one_is_active(
    api, monkeypatch: pytest.MonkeyPatch
) -> None:
    main, client = api

    class Pending:
        def done(self) -> bool:
            return False

    monkeypatch.setattr(main, "_current_run", Pending())

    assert client.post("/api/pipeline/run", json={}).status_code == 409
    assert client.get("/api/status").json()["run_in_progress"] is True


def test_scene_styles_from_the_model_are_whitelisted(tmp_path: Path) -> None:
    hostile = RemotionScene(
        id="s1",
        title="t",
        start_frame=0,
        duration_in_frames=90,
        headline="h",
        subheadline="s",
        bg_gradient="url(http://example.com/x.png)",
        accent_color="red; position: fixed",
    )
    renderer = RemotionRenderer(root_dir=tmp_path)

    renderer.update_scenes_json([hostile])

    written = json.loads(renderer.scenes_json_path.read_text(encoding="utf-8"))[0]
    assert written["bgGradient"] == RemotionScene.model_fields["bg_gradient"].default
    assert written["accentColor"] == "#6366f1"

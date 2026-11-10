"""Regresiones de la API y de la plantilla HTML: texto del modelo como dato y una corrida a la vez."""

import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from hyperframes_studio import renderer as renderer_module
from hyperframes_studio.ollama_client import DEFAULT_SCENES
from hyperframes_studio.renderer import HyperFramesRenderer
from hyperframes_studio.schemas import SceneSpec, VideoBrief
from hyperframes_studio.templates import generate_hyperframes_html, lint_composition


class CompositionProbe(HTMLParser):
    """Recoge los clips, los scripts y el texto visible de los bloques de código."""

    def __init__(self) -> None:
        super().__init__()
        self.clip_ids: list[str | None] = []
        self.scripts = 0
        self.code_text: list[str] = []
        self._in_code = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "clip" in (values.get("class") or "").split():
            self.clip_ids.append(values.get("id"))
        if tag == "script":
            self.scripts += 1
        if tag == "code":
            self._in_code = True

    def handle_endtag(self, tag):
        if tag == "code":
            self._in_code = False

    def handle_data(self, data):
        if self._in_code and data.strip():
            self.code_text.append(data.strip())


def test_code_snippets_are_shown_as_text_not_parsed_as_clips() -> None:
    """Regresión: el fragmento `<div class="clip" ...>` de la escena 2 creaba un clip real."""

    probe = CompositionProbe()
    probe.feed(generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES))

    scene_ids = [scene.id for scene in DEFAULT_SCENES]
    assert probe.clip_ids == [*scene_ids, None, "progress-indicator"]  # None = pie de marca
    assert '<div class="clip" data-start="0" data-duration="3">' in probe.code_text


def test_hostile_model_values_cannot_inject_markup_or_css() -> None:
    hostile = SceneSpec(
        id='x" onload="alert(1)',
        title="t",
        start_time=15.0,
        duration=3.0,
        headline="<script>alert(1)</script>",
        body="a & b",
        accent_color="red;}</style>",
        bg_gradient="url(http://example.com/x.png)",
        badge_text="<b>badge</b>",
    )

    html = generate_hyperframes_html(VideoBrief(), [*DEFAULT_SCENES, hostile])
    probe = CompositionProbe()
    probe.feed(html)

    assert probe.scripts == 2  # GSAP y la línea de tiempo propia; ninguno del modelo
    assert "scene-6" in probe.clip_ids
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "url(" not in html
    assert "red;}" not in html


def test_briefs_reject_cloud_models_and_impossible_durations() -> None:
    with pytest.raises(ValidationError, match="no cloud"):
        VideoBrief(model="gpt-oss:120b-cloud")
    with pytest.raises(ValidationError):
        VideoBrief(target_duration=1.0)


def test_probe_without_a_video_stream_reports_zeros(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audio_only = {"format": {"duration": "15.0"}, "streams": [{"codec_type": "audio"}]}

    def fake_ffprobe(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(audio_only))

    monkeypatch.setattr(subprocess, "run", fake_ffprobe)
    renderer = HyperFramesRenderer(workspace_dir=tmp_path / "workspace")

    assert renderer._probe_video(tmp_path / "video.mp4") == {
        "duration": 15.0,
        "width": 0,
        "height": 0,
        "fps": 0,
    }


@pytest.fixture
def api():
    from hyperframes_studio import main

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


async def test_render_subprocess_always_disables_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict = {}

    async def fake_exec(*cmd, **kwargs):
        captured.update(kwargs)
        raise OSError("sin render en las pruebas")

    monkeypatch.setattr(renderer_module.shutil, "which", lambda _name: "/fake/npx")
    monkeypatch.setattr(renderer_module.asyncio, "create_subprocess_exec", fake_exec)
    monkeypatch.setenv("DO_NOT_TRACK", "0")
    renderer = HyperFramesRenderer(workspace_dir=tmp_path / "workspace")

    result = await renderer.render_video(tmp_path / "out.mp4")

    assert result.success is False
    assert captured["env"]["HYPERFRAMES_NO_TELEMETRY"] == "1"
    assert captured["env"]["DO_NOT_TRACK"] == "1"


# --- Lint local de la composición ------------------------------------------------------------


def test_lint_accepts_the_calibrated_composition() -> None:
    html = generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES)

    assert lint_composition(html, DEFAULT_SCENES) == []


def test_lint_detects_a_stray_clip_like_the_old_snippet_bug() -> None:
    html = generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES).replace(
        "</body>", '<div class="clip" data-start="0" data-duration="3"></div></body>'
    )

    assert lint_composition(html, DEFAULT_SCENES) == [
        "clip inesperado id=None data-start=0 data-duration=3"
    ]


def test_lint_detects_gaps_in_the_timeline() -> None:
    scenes = [scene.model_copy() for scene in DEFAULT_SCENES]
    scenes[1] = scenes[1].model_copy(update={"start_time": 4.0})

    problems = lint_composition(generate_hyperframes_html(VideoBrief(), scenes), scenes)

    assert problems[0] == "scene-2-architecture: empieza en 4.0 s y debería empezar en 3.0 s"


async def test_orchestrator_stops_before_rendering_when_lint_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from hyperframes_studio import orchestrator as orchestrator_module
    from hyperframes_studio.orchestrator import HyperFramesOrchestrator

    orch = HyperFramesOrchestrator(
        ollama_url="http://127.0.0.1:9", workspace_dir=str(tmp_path / "workspace")
    )
    queue = orch.subscribe()
    render = AsyncMock()
    monkeypatch.setattr(
        orchestrator_module, "lint_composition", lambda *_args, **_kwargs: ["clip inesperado"]
    )
    monkeypatch.setattr(orch.renderer, "render_video", render)

    result = await orch.run_pipeline(VideoBrief(), output_path=str(tmp_path / "out.mp4"))

    events = []
    while not queue.empty():
        events.append(await queue.get())
    render.assert_not_awaited()
    assert result.success is False
    assert result.error == "La composición no supera el lint: clip inesperado"
    assert events[-1].state == "FAILED"


async def test_director_keeps_the_timeline_even_if_the_model_proposes_other_times(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from hyperframes_studio.ollama_client import OllamaVideoDirector

    proposed = [
        {"id": f"s{i}", "start_time": 7.5, "duration": 9.0, "headline": f"Escena {i}"}
        for i in range(1, 6)
    ]
    real_client = httpx.AsyncClient

    def factory(**kwargs):
        handler = lambda _request: httpx.Response(200, json={"response": json.dumps(proposed)})  # noqa: E731
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)
    director = OllamaVideoDirector()

    scenes = await director.generate_scenes(VideoBrief(target_duration=10.0))

    assert director.last_source == "ollama"
    assert [(scene.start_time, scene.duration) for scene in scenes] == [
        (0.0, 2.0),
        (2.0, 2.0),
        (4.0, 2.0),
        (6.0, 2.0),
        (8.0, 2.0),
    ]

"""Pruebas unitarias para 22-hyperframes-video-studio."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from hyperframes_studio.evaluation import export_evaluation_jsonl
from hyperframes_studio.ollama_client import DEFAULT_SCENES, OllamaVideoDirector
from hyperframes_studio.orchestrator import HyperFramesOrchestrator
from hyperframes_studio.schemas import (
    EvaluationRecord,
    PipelineState,
    RenderResult,
    SceneSpec,
    VideoBrief,
)
from hyperframes_studio.templates import generate_hyperframes_html


def test_schemas_validation():
    brief = VideoBrief(
        topic="Video Tutorial",
        target_duration=10.0,
        model="qwen3.5:9b"
    )
    assert brief.width == 1920
    assert brief.target_duration == 10.0

    scene = SceneSpec(
        id="scene-test",
        title="Escena de Prueba",
        start_time=0.0,
        duration=5.0,
        headline="Hola Mundo",
        body="Texto descriptivo",
    )
    assert scene.duration == 5.0
    assert scene.badge_text == "HyperFrames"


def test_template_generation():
    brief = VideoBrief(topic="Test Hyperframes", target_duration=10.0)
    scenes = [
        SceneSpec(
            id="sc-1",
            title="Scene 1",
            start_time=0.0,
            duration=5.0,
            headline="Headline 1",
            body="Body 1",
            code_snippet="npx hyperframes init",
        ),
        SceneSpec(
            id="sc-2",
            title="Scene 2",
            start_time=5.0,
            duration=5.0,
            headline="Headline 2",
            body="Body 2",
        ),
    ]

    html = generate_hyperframes_html(brief, scenes)

    assert "<!doctype html>" in html
    assert 'data-composition-id="main"' in html
    assert 'data-duration="10.0"' in html
    assert 'id="sc-1"' in html
    assert 'id="sc-2"' in html
    assert 'class="clip scene-card"' in html
    assert 'window.__timelines["main"] = tl;' in html
    assert "npx hyperframes init" in html


@pytest.mark.asyncio
async def test_ollama_director_fallback():
    # Test fallback logic when network is unavailable
    director = OllamaVideoDirector(base_url="http://127.0.0.1:99999", model="nonexistent")
    brief = VideoBrief(target_duration=20.0)
    scenes = await director.generate_scenes(brief)

    assert len(scenes) == len(DEFAULT_SCENES)
    total_dur = sum(s.duration for s in scenes)
    assert pytest.approx(total_dur, 0.1) == 20.0


def test_evaluation_export_jsonl(tmp_path):
    record = EvaluationRecord(
        case_id="TEST-CASE-001",
        model="qwen3.5:9b",
        success=True,
        duration_actual=15.0,
        duration_expected=15.0,
        render_time_seconds=12.4,
        file_size_kb=32.5,
        scenes_count=5,
        metrics={"resolution": "1920x1080", "fps": 30},
    )

    out_file = tmp_path / "eval_out.jsonl"
    exported_path = export_evaluation_jsonl(record, output_path=out_file)

    assert exported_path.exists()
    lines = exported_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["lab_id"] == "22-hyperframes-video-studio"
    assert data["case_id"] == "TEST-CASE-001"
    assert data["success"] is True


@pytest.mark.asyncio
async def test_orchestrator_pipeline_mock(tmp_path):
    orch = HyperFramesOrchestrator(workspace_dir=str(tmp_path / "workspace"))
    queue = orch.subscribe()

    # Brief, escenas y render simulados coherentes: 5 escenas de 3 s = 15 s.
    brief = VideoBrief(target_duration=15.0)

    # Mock renderer to avoid calling Chrome in unit test
    fake_render = RenderResult(
        video_path=str(tmp_path / "mock.mp4"),
        duration=15.0,
        width=1920,
        height=1080,
        fps=30,
        file_size_bytes=1024 * 50,
        render_elapsed_seconds=2.5,
        success=True,
    )

    # Director y renderer simulados: la prueba nunca llama a Ollama ni a Chrome reales.
    with (
        patch.object(orch.director, "generate_scenes", new=AsyncMock(return_value=list(DEFAULT_SCENES))),
        patch.object(orch.renderer, "render_video", new=AsyncMock(return_value=fake_render)),
    ):
        res = await orch.run_pipeline(brief, output_path=str(tmp_path / "mock.mp4"))

    assert res.success is True
    assert orch.state == PipelineState.COMPLETED
    assert orch.last_eval is not None
    assert orch.last_eval.success is True

    # Check emitted events
    events = []
    while not queue.empty():
        events.append(await queue.get())

    states = [e.state for e in events]
    assert PipelineState.ANALYZING_BRIEF in states
    assert PipelineState.GENERATING_SCRIPT in states
    assert PipelineState.BUILDING_COMPOSITION in states
    assert PipelineState.RENDERING_VIDEO in states
    assert PipelineState.COMPLETED in states

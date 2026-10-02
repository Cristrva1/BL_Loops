"""Pruebas unitarias para 23-remotion-superpowers-studio."""

import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch

from remotion_studio.schemas import (
    EvaluationRecord,
    PipelineEvent,
    RemotionBrief,
    RemotionScene,
    RemotionState,
    RenderResult,
)
from remotion_studio.ollama_director import (
    DEFAULT_REMOTION_SCENES,
    RemotionOllamaDirector,
)
from remotion_studio.evaluation import export_evaluation_jsonl
from remotion_studio.remotion_renderer import RemotionRenderer
from remotion_studio.orchestrator import RemotionOrchestrator


def test_schemas_validation():
    brief = RemotionBrief(
        topic="Prueba Remotion",
        target_duration=12.0,
        fps=30,
        model="qwen3.5:9b"
    )
    assert brief.width == 1920
    assert brief.target_duration == 12.0
    assert brief.fps == 30

    scene = RemotionScene(
        id="scene-test",
        title="Escena Test",
        start_frame=0,
        duration_in_frames=90,
        headline="React Remotion",
        subheadline="Subheadline test",
    )
    assert scene.duration_in_frames == 90
    assert scene.badge == "Remotion Superpowers"


def test_frame_calculations():
    brief = RemotionBrief(target_duration=10.0, fps=30)
    total_frames = int(round(brief.target_duration * brief.fps))
    assert total_frames == 300

    scenes_count = 4
    frames_per_scene = total_frames // scenes_count
    assert frames_per_scene == 75


def test_scenes_json_update(tmp_path):
    renderer = RemotionRenderer(root_dir=tmp_path)
    scenes = [
        RemotionScene(
            id="s1",
            title="Scene 1",
            start_frame=0,
            duration_in_frames=100,
            headline="H1",
            subheadline="S1",
        )
    ]
    renderer.update_scenes_json(scenes)
    assert renderer.scenes_json_path.exists()
    content = json.loads(renderer.scenes_json_path.read_text(encoding="utf-8"))
    assert len(content) == 1
    assert content[0]["id"] == "s1"
    assert content[0]["durationInFrames"] == 100


@pytest.mark.asyncio
async def test_ollama_director_fallback():
    director = RemotionOllamaDirector(base_url="http://127.0.0.1:99999", model="nonexistent")
    brief = RemotionBrief(target_duration=12.0, fps=30)
    scenes = await director.generate_scenes(brief)

    assert len(scenes) == len(DEFAULT_REMOTION_SCENES)
    total_frames = sum(s.duration_in_frames for s in scenes)
    assert total_frames == int(round(12.0 * 30))


def test_evaluation_export_jsonl(tmp_path):
    record = EvaluationRecord(
        case_id="EVAL-REMOTION-001",
        model="qwen3.5:9b",
        success=True,
        duration_actual=12.0,
        duration_expected=12.0,
        render_time_seconds=15.2,
        file_size_kb=850.4,
        total_frames=360,
        scenes_count=4,
        metrics={"resolution": "1920x1080", "fps": 30},
    )

    out_file = tmp_path / "eval_out.jsonl"
    exported_path = export_evaluation_jsonl(record, output_path=out_file)

    assert exported_path.exists()
    lines = exported_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["lab_id"] == "23-remotion-superpowers-studio"
    assert data["case_id"] == "EVAL-REMOTION-001"
    assert data["success"] is True


@pytest.mark.asyncio
async def test_orchestrator_pipeline_mock(tmp_path):
    orch = RemotionOrchestrator(root_dir=tmp_path)
    queue = orch.subscribe()

    brief = RemotionBrief(target_duration=10.0, fps=30)

    fake_render = RenderResult(
        video_path=str(tmp_path / "mock.mp4"),
        duration=10.0,
        width=1920,
        height=1080,
        fps=30,
        total_frames=300,
        file_size_bytes=1024 * 60,
        render_elapsed_seconds=3.1,
        success=True,
    )

    with patch.object(orch.renderer, "render_video", new=AsyncMock(return_value=fake_render)):
        res = await orch.run_pipeline(brief, output_path=str(tmp_path / "mock.mp4"))

    assert res.success is True
    assert orch.state == RemotionState.COMPLETED
    assert orch.last_eval is not None
    assert orch.last_eval.success is True

    events = []
    while not queue.empty():
        events.append(await queue.get())

    states = [e.state for e in events]
    assert RemotionState.ANALYZING_BRIEF in states
    assert RemotionState.PLANNING_SCENES in states
    assert RemotionState.CALCULATING_FRAMES in states
    assert RemotionState.WRITING_REACT_PROPS in states
    assert RemotionState.RENDERING_VIDEO in states
    assert RemotionState.COMPLETED in states

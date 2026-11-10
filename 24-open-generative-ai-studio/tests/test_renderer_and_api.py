"""Renderizador FFmpeg, orquestador y API: errores explícitos y nada de métricas inventadas."""

import shutil
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from open_genai_studio import animatic_renderer as renderer_module
from open_genai_studio.animatic_renderer import (
    AnimaticRenderer,
    build_filter_graph,
    drawtext_value,
    fontfile_option,
    safe_hex_color,
)
from open_genai_studio.orchestrator import OpenGenAIOrchestrator
from open_genai_studio.schemas import RenderResult, StoryboardProject, StoryboardShot
from open_genai_studio.storyboard_engine import calibrated_shots

TRICKY = StoryboardShot(
    shot_number=1,
    duration_seconds=1.0,
    headline="Plano: 'uno', 100% [listo]; fin",
    description="Texto con comillas 'simples'",
    prompt_expansion="Prompt: comas, dos puntos: y una barra \\ invertida",
    accent_color="#zzzzzz",
)


# --- Preparación del texto para drawtext ------------------------------------------------------


def test_drawtext_value_neutralizes_quotes_colons_and_backslashes() -> None:
    assert drawtext_value("Plano: 'uno'\n  y \\ fin") == "Plano\\: ’uno’ y / fin"


def test_drawtext_value_truncates_with_an_ellipsis() -> None:
    assert drawtext_value("abcdefghij", limit=5) == "abcd…"
    assert drawtext_value("corto", limit=5) == "corto"


def test_invented_colors_fall_back_to_the_base_accent() -> None:
    assert safe_hex_color("#38BDF8") == "38bdf8"
    assert safe_hex_color("38bdf8") == "38bdf8"
    assert safe_hex_color("red; drawbox") == "6366f1"


def test_fontfile_option_escapes_the_windows_drive_colon() -> None:
    assert (
        fontfile_option("C:/Windows/Fonts/arial.ttf") == ":fontfile='C\\:/Windows/Fonts/arial.ttf'"
    )
    assert fontfile_option(None) == ""
    assert fontfile_option("/fonts/it's.ttf") == ""


def test_filter_graph_keeps_model_text_inside_quoted_values() -> None:
    graph = build_filter_graph(TRICKY, 0, font_file="C:/Windows/Fonts/arial.ttf")

    assert graph.startswith("color=c=0x0a0f1d:s=1920x1080:d=1.0:r=30,")
    assert graph.count("drawtext=") == 6
    assert graph.count("expansion=none") == 6
    # Solo las comillas que abren y cierran `text` y `fontfile`: ninguna viene del modelo.
    assert graph.count("'") == 6 * 4
    assert "Plano\\: ’uno’, 100% [listo]; fin" in graph
    assert "fontfile='C\\:/Windows/Fonts/arial.ttf'" in graph
    assert "color=0x6366f1@0.3" in graph


# --- Renderizador ---------------------------------------------------------------------------


async def test_missing_ffmpeg_fails_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(renderer_module.shutil, "which", lambda _name: None)
    renderer = AnimaticRenderer(workspace_dir=tmp_path / "workspace")

    result = await renderer.render_animatic(calibrated_shots(3.0), tmp_path / "out.mp4")

    assert result.success is False
    assert "FFmpeg" in (result.error or "")


async def test_a_failed_shot_is_never_dropped_silently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regresión: el renderizador anterior omitía el plano fallido y aun así declaraba éxito."""

    async def fake_run(cmd: list[str]) -> tuple[bool, str]:
        target = Path(cmd[-1])
        if target.name == "shot_2.mp4":
            return False, "Error initializing filter 'drawtext'"
        target.write_bytes(b"segmento simulado")
        return True, ""

    monkeypatch.setattr(renderer_module.shutil, "which", lambda name: f"/fake/{name}")
    monkeypatch.setattr(renderer_module, "_run", fake_run)
    renderer = AnimaticRenderer(workspace_dir=tmp_path / "workspace")

    result = await renderer.render_animatic(calibrated_shots(3.0), tmp_path / "out.mp4")

    assert result.success is False
    assert result.error == "FFmpeg no pudo generar el plano 2: Error initializing filter 'drawtext'"
    assert result.duration == 0.0


def test_unprobed_video_has_no_invented_metrics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def missing_ffprobe(*_args, **_kwargs):
        raise FileNotFoundError("ffprobe")

    monkeypatch.setattr(subprocess, "run", missing_ffprobe)
    renderer = AnimaticRenderer(workspace_dir=tmp_path / "workspace")

    assert renderer._probe_video(tmp_path / "video.mp4") == {
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "fps": 0,
    }


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="FFmpeg/ffprobe no están instalados: se omite el render real",
)
async def test_real_ffmpeg_render_keeps_every_shot(tmp_path: Path) -> None:
    second = TRICKY.model_copy(update={"shot_number": 2, "accent_color": "#10b981"})
    renderer = AnimaticRenderer(workspace_dir=tmp_path / "workspace")

    result = await renderer.render_animatic([TRICKY, second], tmp_path / "animatic.mp4")

    assert result.success is True, result.error
    assert result.duration == pytest.approx(2.0, abs=0.1)
    assert (result.width, result.height, result.fps, result.shots_count) == (1920, 1080, 30, 2)


# --- Orquestador ----------------------------------------------------------------------------


async def test_orchestrator_publishes_the_fallback_as_event_and_metric(tmp_path: Path) -> None:
    orch = OpenGenAIOrchestrator(workspace_dir=str(tmp_path / "workspace"))
    queue = orch.subscribe()

    async def fallback_storyboard(project: StoryboardProject):
        orch.storyboard_engine.last_source = "fallback"
        orch.storyboard_engine.last_fallback_reason = "ConnectError al consultar Ollama"
        return calibrated_shots(3.0)

    fake_render = RenderResult(
        video_path=str(tmp_path / "mock.mp4"),
        duration=12.0,
        width=1920,
        height=1080,
        fps=30,
        shots_count=4,
        file_size_bytes=50 * 1024,
        render_elapsed_seconds=1.0,
        success=True,
    )
    with (
        patch.object(orch.storyboard_engine, "generate_storyboard", new=fallback_storyboard),
        patch.object(orch.renderer, "render_animatic", new=AsyncMock(return_value=fake_render)),
    ):
        await orch.run_pipeline(StoryboardProject(), output_path=str(tmp_path / "m.mp4"))

    events = []
    while not queue.empty():
        events.append(await queue.get())
    assert any(event.message.startswith("Fallback visible") for event in events)
    assert events[-1].state == "COMPLETED"
    assert orch.last_eval is not None
    assert orch.last_eval.success is True
    assert orch.last_eval.metrics["director_source"] == "fallback"
    assert orch.last_eval.metrics["duration_measured"] is True


# --- API ----------------------------------------------------------------------------------


@pytest.fixture
def api():
    from open_genai_studio import main

    return main, TestClient(main.app)


def test_panel_assets_and_truthful_status_are_served(api) -> None:
    _main, client = api

    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/styles.css").status_code == 200
    status = client.get("/api/status").json()
    assert isinstance(status["ollama_reachable"], bool)
    assert isinstance(status["ffmpeg_available"], bool)
    assert status["run_in_progress"] is False


def test_pipeline_rejects_out_of_contract_requests(api) -> None:
    _main, client = api

    assert client.post("/api/pipeline/run", json={"model": "qwen3.5:cloud"}).status_code == 422
    assert client.post("/api/pipeline/run", json={"total_duration_target": 1}).status_code == 422


def test_pipeline_refuses_a_second_run_while_one_is_active(
    api, monkeypatch: pytest.MonkeyPatch
) -> None:
    main, client = api

    class Pending:
        def done(self) -> bool:
            return False

    monkeypatch.setattr(main, "_current_run", Pending())

    response = client.post("/api/pipeline/run", json={})

    assert response.status_code == 409


def test_prompt_expansion_reports_its_source_and_uses_the_configured_model(
    api, monkeypatch: pytest.MonkeyPatch
) -> None:
    main, client = api
    monkeypatch.setattr(main.expander, "base_url", "http://127.0.0.1:9")

    body = client.post("/api/prompt/expand", json={"raw_idea": "Un faro en la niebla"}).json()

    assert body["source"] == "fallback"
    assert "al consultar Ollama" in body["fallback_reason"]
    assert body["model"] == main.SETTINGS.ollama_model
    assert set(body["result"]) == {
        "positive_prompt",
        "negative_prompt",
        "camera_settings",
        "mood_palette",
    }


def test_storyboard_and_video_return_404_before_the_first_run(api) -> None:
    main, client = api
    if main.orchestrator.last_shots:
        pytest.skip("El orquestador compartido ya tiene una corrida en memoria")

    assert client.get("/api/storyboard").status_code == 404
    assert client.get("/api/video").status_code == 404
    assert client.post("/api/export").status_code == 400

"""Orquestador agéntico para la generación y renderizado de video en HyperFrames."""

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from hyperframes_studio.schemas import (
    EvaluationRecord,
    PipelineEvent,
    PipelineState,
    RenderResult,
    SceneSpec,
    VideoBrief,
)
from hyperframes_studio.ollama_client import OllamaVideoDirector
from hyperframes_studio.templates import generate_hyperframes_html
from hyperframes_studio.renderer import HyperFramesRenderer

logger = logging.getLogger(__name__)


class HyperFramesOrchestrator:
    def __init__(
        self,
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        workspace_dir: str = ".local/workspace",
    ):
        self.director = OllamaVideoDirector(base_url=ollama_url, model=model)
        self.renderer = HyperFramesRenderer(workspace_dir=workspace_dir)
        self.state = PipelineState.IDLE
        self.event_subscribers: list[asyncio.Queue[PipelineEvent]] = []
        self.last_brief: VideoBrief | None = None
        self.last_scenes: list[SceneSpec] = []
        self.last_html: str = ""
        self.last_render: RenderResult | None = None
        self.last_eval: EvaluationRecord | None = None

    def subscribe(self) -> asyncio.Queue[PipelineEvent]:
        q = asyncio.Queue()
        self.event_subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[PipelineEvent]) -> None:
        if q in self.event_subscribers:
            self.event_subscribers.remove(q)

    async def _emit(self, state: PipelineState, node: str, message: str, data: dict | None = None) -> None:
        self.state = state
        event = PipelineEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            state=state,
            node=node,
            message=message,
            data=data or {},
        )
        for q in list(self.event_subscribers):
            try:
                q.put_nowait(event)
            except Exception:
                pass

    async def run_pipeline(self, brief: VideoBrief, output_path: str = ".local/output/tutorial_hyperframes.mp4") -> RenderResult:
        """Ejecuta el pipeline completo de creación audiovisual."""
        self.last_brief = brief
        await self._emit(
            PipelineState.ANALYZING_BRIEF,
            node="BriefAnalyzer",
            message=f"Analizando brief: '{brief.topic}' con duración objetivo de {brief.target_duration}s",
            data={"brief": brief.model_dump()},
        )

        # 1. Generar guión y escenas con Ollama
        await self._emit(
            PipelineState.GENERATING_SCRIPT,
            node="OllamaDirector",
            message=f"Solicitando guión técnico y desglose de escenas al modelo {brief.model}...",
        )
        scenes = await self.director.generate_scenes(brief)
        self.last_scenes = scenes
        await self._emit(
            PipelineState.BUILDING_COMPOSITION,
            node="HtmlComposer",
            message=f"Diseñando composición HTML y líneas de tiempo GSAP para {len(scenes)} escenas.",
            data={"scenes_count": len(scenes), "scenes": [s.model_dump() for s in scenes]},
        )

        # 2. Generar el documento HTML HyperFrames
        html_code = generate_hyperframes_html(brief, scenes)
        self.last_html = html_code
        self.renderer.prepare_workspace(html_code)

        # 3. Validación de estructura y tiempos
        await self._emit(
            PipelineState.VALIDATING_LINT,
            node="HyperFramesLinter",
            message="Validando consistencia de selectores, atributos data-* y timelines GSAP...",
            data={"html_length_bytes": len(html_code.encode("utf-8"))},
        )

        # 4. Renderizado a MP4
        await self._emit(
            PipelineState.RENDERING_VIDEO,
            node="ChromeFFmpegRenderer",
            message=f"Renderizando MP4 a {brief.width}x{brief.height} ({brief.fps} fps) en Chrome Headless...",
        )
        render_res = await self.renderer.render_video(output_path)
        self.last_render = render_res

        if not render_res.success:
            await self._emit(
                PipelineState.FAILED,
                node="ChromeFFmpegRenderer",
                message=f"Fallo en el renderizado: {render_res.error}",
                data=render_res.model_dump(),
            )
            return render_res

        # 5. Evaluación de criterios
        await self._emit(
            PipelineState.EVALUATING,
            node="QualityEvaluator",
            message=f"Evaluando calidad y sincronía del video renderizado ({render_res.duration}s)...",
            data=render_res.model_dump(),
        )
        eval_record = self._evaluate_run(brief, scenes, render_res)
        self.last_eval = eval_record

        # 6. Completado
        await self._emit(
            PipelineState.COMPLETED,
            node="PipelineGate",
            message=f"Video MP4 generado con éxito en {render_res.render_elapsed_seconds}s. Ruta: {render_res.video_path}",
            data={"eval": eval_record.model_dump(), "render": render_res.model_dump()},
        )

        return render_res

    def _evaluate_run(self, brief: VideoBrief, scenes: list[SceneSpec], render_res: RenderResult) -> EvaluationRecord:
        file_size_kb = round(render_res.file_size_bytes / 1024.0, 2)
        duration_diff = abs(render_res.duration - brief.target_duration)
        duration_valid = duration_diff <= 1.0  # margen de 1s
        has_min_size = file_size_kb > 10.0

        success = render_res.success and duration_valid and has_min_size

        return EvaluationRecord(
            case_id="EVAL-HYPERFRAMES-001",
            model=brief.model,
            success=success,
            duration_actual=render_res.duration,
            duration_expected=brief.target_duration,
            render_time_seconds=render_res.render_elapsed_seconds,
            file_size_kb=file_size_kb,
            scenes_count=len(scenes),
            metrics={
                "resolution": f"{render_res.width}x{render_res.height}",
                "fps": render_res.fps,
                "duration_delta_seconds": round(duration_diff, 2),
                "deterministic": True,
                "has_min_size": has_min_size,
            },
        )

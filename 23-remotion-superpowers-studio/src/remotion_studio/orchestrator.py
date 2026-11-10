"""Orquestador agéntico para Remotion Superpowers."""

import asyncio
import contextlib
import logging
from datetime import UTC, datetime
from pathlib import Path

from remotion_studio.ollama_director import RemotionOllamaDirector
from remotion_studio.remotion_renderer import RemotionRenderer
from remotion_studio.schemas import (
    EvaluationRecord,
    PipelineEvent,
    RemotionBrief,
    RemotionScene,
    RemotionState,
    RenderResult,
)

logger = logging.getLogger(__name__)


class RemotionOrchestrator:
    def __init__(
        self,
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        root_dir: str | Path = ".",
    ):
        self.director = RemotionOllamaDirector(base_url=ollama_url, model=model)
        self.renderer = RemotionRenderer(root_dir=root_dir)
        self.state = RemotionState.IDLE
        self.event_subscribers: list[asyncio.Queue[PipelineEvent]] = []
        self.last_brief: RemotionBrief | None = None
        self.last_scenes: list[RemotionScene] = []
        self.last_render: RenderResult | None = None
        self.last_eval: EvaluationRecord | None = None

    def subscribe(self) -> asyncio.Queue[PipelineEvent]:
        q = asyncio.Queue()
        self.event_subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[PipelineEvent]) -> None:
        if q in self.event_subscribers:
            self.event_subscribers.remove(q)

    async def _emit(self, state: RemotionState, node: str, message: str, data: dict | None = None) -> None:
        self.state = state
        event = PipelineEvent(
            timestamp=datetime.now(UTC).isoformat(),
            state=state,
            node=node,
            message=message,
            data=data or {},
        )
        for q in list(self.event_subscribers):
            # Una cola llena o cerrada no debe detener el pipeline.
            with contextlib.suppress(asyncio.QueueFull):
                q.put_nowait(event)

    async def _emit_director_source(self, scenes_count: int) -> None:
        """Publica de dónde salieron las escenas: el respaldo calibrado nunca es silencioso."""

        if self.director.last_source == "ollama":
            await self._emit(
                RemotionState.PLANNING_SCENES,
                node="OllamaDirector",
                message=f"Ollama entregó {scenes_count} escenas válidas.",
                data={"director_source": "ollama"},
            )
            return
        reason = self.director.last_fallback_reason or "motivo desconocido"
        await self._emit(
            RemotionState.PLANNING_SCENES,
            node="OllamaDirector",
            message=(
                f"Fallback visible: {reason}. Se usan {scenes_count} escenas calibradas; "
                "el video no refleja una decisión del modelo."
            ),
            data={"director_source": "fallback", "fallback_reason": reason},
        )

    async def run_pipeline(
        self,
        brief: RemotionBrief,
        output_path: str = ".local/output/remotion_superpowers.mp4",
    ) -> RenderResult:
        """Ejecuta el pipeline completo de Remotion Superpowers."""
        self.last_brief = brief
        total_frames = int(round(brief.target_duration * brief.fps))

        # 1. Analizar brief
        await self._emit(
            RemotionState.ANALYZING_BRIEF,
            node="BriefAnalyzer",
            message=f"Analizando brief de video: '{brief.topic}' ({brief.target_duration}s)",
            data={"brief": brief.model_dump()},
        )

        # 2. Planificar escenas con Ollama
        await self._emit(
            RemotionState.PLANNING_SCENES,
            node="OllamaDirector",
            message=f"Consultando modelo {brief.model} para coreografía de escenas y guión audiovisual...",
        )
        scenes = await self.director.generate_scenes(brief)
        self.last_scenes = scenes
        await self._emit_director_source(len(scenes))

        # 3. Calcular fotogramas exactos
        await self._emit(
            RemotionState.CALCULATING_FRAMES,
            node="FrameCalculator",
            message=f"Calculando {total_frames} fotogramas exactos a {brief.fps} FPS distribuidos en {len(scenes)} secuencias.",
            data={"total_frames": total_frames, "scenes_count": len(scenes)},
        )

        # 4. Escribir props de React
        await self._emit(
            RemotionState.WRITING_REACT_PROPS,
            node="ReactComposer",
            message="Actualizando scenes.json para inyección en componentes React de Remotion.",
            data={"scenes": [s.model_dump() for s in scenes]},
        )
        self.renderer.update_scenes_json(scenes)

        # 5. Renderizado a MP4
        await self._emit(
            RemotionState.RENDERING_VIDEO,
            node="RemotionCliRenderer",
            message=f"Compilando video con @remotion/cli ({brief.width}x{brief.height} @ {brief.fps}fps)...",
        )
        render_res = await self.renderer.render_video(output_path)
        self.last_render = render_res

        if not render_res.success:
            await self._emit(
                RemotionState.FAILED,
                node="RemotionCliRenderer",
                message=f"Error en renderizado: {render_res.error}",
                data=render_res.model_dump(),
            )
            return render_res

        # 6. Evaluación
        await self._emit(
            RemotionState.EVALUATING,
            node="QualityEvaluator",
            message=f"Evaluando calidad y sincronía de fotogramas ({render_res.duration}s)...",
            data=render_res.model_dump(),
        )
        eval_record = self._evaluate_run(brief, scenes, render_res)
        self.last_eval = eval_record

        # 7. Completado
        await self._emit(
            RemotionState.COMPLETED,
            node="PipelineGate",
            message=f"Video Remotion renderizado con éxito en {render_res.render_elapsed_seconds}s.",
            data={"eval": eval_record.model_dump(), "render": render_res.model_dump()},
        )

        return render_res

    def _evaluate_run(
        self, brief: RemotionBrief, scenes: list[RemotionScene], render_res: RenderResult
    ) -> EvaluationRecord:
        file_size_kb = round(render_res.file_size_bytes / 1024.0, 2)
        duration_diff = abs(render_res.duration - brief.target_duration)
        duration_valid = duration_diff <= 1.0
        has_min_size = file_size_kb > 10.0

        success = render_res.success and duration_valid and has_min_size

        return EvaluationRecord(
            case_id="EVAL-REMOTION-001",
            model=brief.model,
            success=success,
            duration_actual=render_res.duration,
            duration_expected=brief.target_duration,
            render_time_seconds=render_res.render_elapsed_seconds,
            file_size_kb=file_size_kb,
            total_frames=render_res.total_frames,
            scenes_count=len(scenes),
            metrics={
                "resolution": f"{render_res.width}x{render_res.height}",
                "fps": render_res.fps,
                "duration_delta_seconds": round(duration_diff, 2),
                "deterministic": True,
                "react_component_root": "MainVideo",
                "duration_measured": render_res.duration > 0,
                "director_source": self.director.last_source,
            },
        )

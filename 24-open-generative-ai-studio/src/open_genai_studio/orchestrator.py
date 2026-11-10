"""Orquestador agéntico para Open Generative AI Studio."""

import asyncio
import contextlib
import logging
from datetime import UTC, datetime
from pathlib import Path

from open_genai_studio.animatic_renderer import AnimaticRenderer
from open_genai_studio.schemas import (
    EvaluationRecord,
    PipelineEvent,
    RenderResult,
    StoryboardProject,
    StoryboardShot,
    StudioState,
)
from open_genai_studio.storyboard_engine import OpenGenAIStoryboardEngine

logger = logging.getLogger(__name__)


class OpenGenAIOrchestrator:
    def __init__(
        self,
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        workspace_dir: str = ".local/workspace",
        font_file: str | Path | None = None,
    ):
        self.storyboard_engine = OpenGenAIStoryboardEngine(base_url=ollama_url, model=model)
        self.renderer = AnimaticRenderer(workspace_dir=workspace_dir, font_file=font_file)
        self.state = StudioState.IDLE
        self.event_subscribers: list[asyncio.Queue[PipelineEvent]] = []
        self.last_project: StoryboardProject | None = None
        self.last_shots: list[StoryboardShot] = []
        self.last_render: RenderResult | None = None
        self.last_eval: EvaluationRecord | None = None

    def subscribe(self) -> asyncio.Queue[PipelineEvent]:
        q: asyncio.Queue[PipelineEvent] = asyncio.Queue()
        self.event_subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[PipelineEvent]) -> None:
        if q in self.event_subscribers:
            self.event_subscribers.remove(q)

    async def _emit(
        self, state: StudioState, node: str, message: str, data: dict | None = None
    ) -> None:
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

    async def _emit_storyboard_source(self, shots_count: int) -> None:
        """Publica de dónde salieron los planos: el respaldo calibrado nunca es silencioso."""

        engine = self.storyboard_engine
        if engine.last_source == "ollama":
            await self._emit(
                StudioState.GENERATING_STORYBOARD,
                node="StoryboardStudio",
                message=f"Ollama entregó {shots_count} planos válidos.",
                data={"director_source": "ollama"},
            )
            return
        reason = engine.last_fallback_reason or "motivo desconocido"
        await self._emit(
            StudioState.GENERATING_STORYBOARD,
            node="StoryboardStudio",
            message=(
                f"Fallback visible: {reason}. Se usan {shots_count} planos calibrados; "
                "el storyboard no refleja una decisión del modelo."
            ),
            data={"director_source": "fallback", "fallback_reason": reason},
        )

    async def run_pipeline(
        self,
        project: StoryboardProject,
        output_path: str = ".local/output/open_genai_animatic.mp4",
    ) -> RenderResult:
        """Ejecuta el pipeline de storyboard y animatic."""
        self.last_project = project

        # 1. Analizar concepto
        await self._emit(
            StudioState.ANALYZING_CONCEPT,
            node="ConceptAnalyzer",
            message=(
                f"Analizando concepto narrativo: '{project.narrative_concept}' "
                f"({project.total_duration_target}s)"
            ),
            data={"project": project.model_dump()},
        )

        # 2. Generar Storyboard con Ollama
        await self._emit(
            StudioState.GENERATING_STORYBOARD,
            node="StoryboardStudio",
            message=f"Desglosando planos cinematográficos y prompts con Ollama ({project.model})...",
        )
        shots = await self.storyboard_engine.generate_storyboard(project)
        self.last_shots = shots
        project.shots = shots
        await self._emit_storyboard_source(len(shots))

        # 3. Renderizar animatic en video con FFmpeg
        await self._emit(
            StudioState.RENDERING_ANIMATIC,
            node="AnimaticEngine",
            message=f"Compilando animatic de {len(shots)} planos a 1080p con FFmpeg...",
            data={"shots": [s.model_dump() for s in shots]},
        )
        render_res = await self.renderer.render_animatic(shots, output_path)
        self.last_render = render_res

        if not render_res.success:
            await self._emit(
                StudioState.FAILED,
                node="AnimaticEngine",
                message=f"Error al renderizar animatic: {render_res.error}",
                data=render_res.model_dump(),
            )
            return render_res

        # 4. Evaluación
        await self._emit(
            StudioState.EVALUATING,
            node="QualityEvaluator",
            message=f"Evaluando animatic generado ({render_res.duration}s)...",
            data=render_res.model_dump(),
        )
        eval_record = self._evaluate_run(project, shots, render_res)
        self.last_eval = eval_record

        # 5. Completado
        await self._emit(
            StudioState.COMPLETED,
            node="PipelineGate",
            message=f"Animatic generado en {render_res.render_elapsed_seconds}s.",
            data={"eval": eval_record.model_dump(), "render": render_res.model_dump()},
        )

        return render_res

    def _evaluate_run(
        self,
        project: StoryboardProject,
        shots: list[StoryboardShot],
        render_res: RenderResult,
    ) -> EvaluationRecord:
        file_size_kb = round(render_res.file_size_bytes / 1024.0, 2)
        duration_diff = abs(render_res.duration - project.total_duration_target)
        duration_valid = duration_diff <= 1.0
        has_min_size = file_size_kb > 10.0

        success = render_res.success and duration_valid and has_min_size

        return EvaluationRecord(
            case_id="EVAL-OPEN-GENAI-001",
            model=project.model,
            success=success,
            duration_actual=render_res.duration,
            duration_expected=project.total_duration_target,
            render_time_seconds=render_res.render_elapsed_seconds,
            file_size_kb=file_size_kb,
            shots_count=len(shots),
            metrics={
                "resolution": f"{render_res.width}x{render_res.height}",
                "fps": render_res.fps,
                "duration_delta_seconds": round(duration_diff, 2),
                "deterministic": True,
                "all_shots_have_prompts": all(len(s.prompt_expansion) > 20 for s in shots),
                "duration_measured": render_res.duration > 0,
                "director_source": self.storyboard_engine.last_source,
            },
        )

"""Servidor FastAPI y CLI de demostración para 24-open-generative-ai-studio.

La API sirve también el panel (`frontend/`). Todo el estado vive en memoria y los artefactos
(segmentos, MP4 y JSONL) se guardan bajo `.local/` dentro del propio laboratorio.
"""

import asyncio
import shutil
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from open_genai_studio.config import ConfigurationError, Settings, lab_root
from open_genai_studio.evaluation import export_evaluation_jsonl
from open_genai_studio.orchestrator import OpenGenAIOrchestrator
from open_genai_studio.prompt_expander import PromptStudioExpander
from open_genai_studio.schemas import PromptExpansionRequest, StoryboardProject

# En Windows la consola puede usar cp1252; así los acentos no rompen la demo.
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

# Configuración validada: Ollama solo en loopback y servidor solo en una interfaz local.
try:
    SETTINGS = Settings.load()
except ConfigurationError as exc:
    print(f"Configuracion invalida: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc

LOCAL_DIR = lab_root() / ".local"
OUTPUT_PATH = LOCAL_DIR / "output" / "open_genai_animatic.mp4"
EVAL_PATH = LOCAL_DIR / "eval_results.jsonl"
FRONTEND_DIR = lab_root() / "frontend"

app = FastAPI(
    title="Open Generative AI Studio",
    description="Prompt Studio, Storyboard Studio y animatic MP4 con IA local (Ollama) y FFmpeg",
    version="0.1.0",
)

# El panel se sirve desde esta misma API; solo se aceptan orígenes locales del laboratorio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://127.0.0.1:{SETTINGS.port}",
        f"http://localhost:{SETTINGS.port}",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

orchestrator = OpenGenAIOrchestrator(
    ollama_url=SETTINGS.ollama_base_url,
    model=SETTINGS.ollama_model,
    workspace_dir=str(LOCAL_DIR / "workspace"),
    font_file=SETTINGS.font_file,
)
expander = PromptStudioExpander(base_url=SETTINGS.ollama_base_url, model=SETTINGS.ollama_model)

# Se guarda la referencia de la corrida activa: evita dos renders simultáneos sobre el mismo
# workspace y que el recolector de basura elimine la tarea a mitad de camino.
_current_run: asyncio.Task | None = None


def _use_default_model(request: StoryboardProject | PromptExpansionRequest) -> None:
    """Si el cliente no eligió modelo, se usa el del `.env` y no el valor fijo del esquema."""

    if "model" not in request.model_fields_set:
        request.model = SETTINGS.ollama_model


def _run_in_progress() -> bool:
    return _current_run is not None and not _current_run.done()


async def _ollama_reachable() -> bool:
    """Comprueba de verdad si Ollama responde, para que el panel no muestre un estado inventado."""

    try:
        async with httpx.AsyncClient(timeout=1.5, trust_env=False) as client:
            response = await client.get(f"{SETTINGS.ollama_base_url}/api/tags")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


@app.get("/api/status")
async def get_status():
    return {
        "status": "ok",
        "orchestrator_state": orchestrator.state,
        "run_in_progress": _run_in_progress(),
        "ollama_url": SETTINGS.ollama_base_url,
        "model": SETTINGS.ollama_model,
        "ollama_reachable": await _ollama_reachable(),
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
        "ffprobe_available": shutil.which("ffprobe") is not None,
        "last_render": orchestrator.last_render.model_dump() if orchestrator.last_render else None,
        "last_eval": orchestrator.last_eval.model_dump() if orchestrator.last_eval else None,
    }


@app.post("/api/pipeline/run")
async def run_pipeline(project: StoryboardProject):
    global _current_run
    if _run_in_progress():
        raise HTTPException(
            status_code=409, detail="Ya hay un animatic en curso; espera a que termine"
        )
    _use_default_model(project)
    _current_run = asyncio.create_task(
        orchestrator.run_pipeline(project, output_path=str(OUTPUT_PATH))
    )
    return {"message": "Pipeline iniciado", "model": project.model}


@app.get("/api/pipeline/events")
async def pipeline_events():
    queue = orchestrator.subscribe()

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {event.model_dump_json()}\n\n"
        finally:
            orchestrator.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/storyboard")
async def get_storyboard():
    if not orchestrator.last_shots:
        raise HTTPException(status_code=404, detail="Todavía no se ha generado ningún storyboard")
    engine = orchestrator.storyboard_engine
    return {
        "director_source": engine.last_source,
        "fallback_reason": engine.last_fallback_reason,
        "shots": [shot.model_dump() for shot in orchestrator.last_shots],
    }


@app.post("/api/prompt/expand")
async def expand_prompt(request: PromptExpansionRequest):
    _use_default_model(request)
    result = await expander.expand_prompt(request)
    return {
        "source": expander.last_source,
        "fallback_reason": expander.last_fallback_reason,
        "model": request.model,
        "result": result,
    }


@app.get("/api/video")
async def get_video():
    if not orchestrator.last_render or not orchestrator.last_render.success:
        raise HTTPException(status_code=404, detail="No hay animatic renderizado disponible aún")
    video_path = Path(orchestrator.last_render.video_path)
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado")
    return FileResponse(path=str(video_path), media_type="video/mp4", filename=video_path.name)


@app.post("/api/export")
async def export_eval():
    if not orchestrator.last_eval:
        raise HTTPException(status_code=400, detail="No hay evaluación para exportar")
    target = export_evaluation_jsonl(orchestrator.last_eval, output_path=EVAL_PATH)
    return {"status": "exported", "path": target.relative_to(lab_root()).as_posix()}


@app.get("/app.js", include_in_schema=False)
async def serve_app_js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="text/javascript")


@app.get("/styles.css", include_in_schema=False)
async def serve_styles():
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>24-open-generative-ai-studio: API activa</h1>")


def run_demo_cli() -> None:
    """Demostración de extremo a extremo desde la terminal: storyboard, animatic y JSONL."""

    print("=== BL_Loops: Laboratorio 24 - Open Generative AI Studio ===")
    project = StoryboardProject(model=SETTINGS.ollama_model)
    print(f"1. Ollama: {SETTINGS.ollama_base_url} | modelo: {project.model}")
    print(f"2. Proyecto: '{project.title}' ({project.total_duration_target}s)")

    orch = OpenGenAIOrchestrator(
        ollama_url=SETTINGS.ollama_base_url,
        model=SETTINGS.ollama_model,
        workspace_dir=str(LOCAL_DIR / "workspace"),
        font_file=SETTINGS.font_file,
    )

    async def main_coro() -> int:
        res = await orch.run_pipeline(project, output_path=str(OUTPUT_PATH))
        engine = orch.storyboard_engine
        reason = engine.last_fallback_reason
        print(f"3. Origen de los planos: {engine.last_source}" + (f" ({reason})" if reason else ""))
        for shot in orch.last_shots:
            print(
                f"   - Plano {shot.shot_number}: {shot.shot_type.value} | "
                f"{shot.camera_movement.value} | {shot.duration_seconds}s | {shot.headline}"
            )
        if not res.success:
            print(f"[ERROR] No se pudo renderizar el animatic: {res.error}")
            return 1
        print("4. Animatic renderizado:")
        print(f"   - Archivo: {Path(res.video_path).relative_to(lab_root()).as_posix()}")
        print(f"   - Duración medida: {res.duration}s | {res.width}x{res.height} a {res.fps} fps")
        print(f"   - Tamaño: {round(res.file_size_bytes / 1024.0, 2)} KB")
        if orch.last_eval:
            target = export_evaluation_jsonl(orch.last_eval, output_path=EVAL_PATH)
            print(f"5. Evaluación exportada a {target.relative_to(lab_root()).as_posix()}")
            print(f"   - Aprobada: {orch.last_eval.success}")
        return 0

    sys.exit(asyncio.run(main_coro()))


if __name__ == "__main__":
    uvicorn.run("open_genai_studio.main:app", host=SETTINGS.host, port=SETTINGS.port, reload=True)

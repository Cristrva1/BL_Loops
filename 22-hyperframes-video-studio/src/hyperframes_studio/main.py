"""Servidor FastAPI y CLI para 22-hyperframes-video-studio."""

import asyncio
import shutil
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from hyperframes_studio.config import ConfigurationError, Settings, lab_root
from hyperframes_studio.evaluation import export_evaluation_jsonl
from hyperframes_studio.orchestrator import HyperFramesOrchestrator
from hyperframes_studio.schemas import VideoBrief

# Configurar stdout para evitar fallos de encoding en Windows cp1252
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

app = FastAPI(
    title="HyperFrames Video Studio",
    description="Estudio visual y pipeline de renderizado de video HTML con IA Local (Ollama)",
    version="0.1.0",
)

# Configuración validada: Ollama solo en loopback y servidor solo en una interfaz local.
try:
    SETTINGS = Settings.load()
except ConfigurationError as exc:
    print(f"Configuracion invalida: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc
LOCAL_DIR = lab_root() / ".local"
OUTPUT_PATH = LOCAL_DIR / "output" / "tutorial_hyperframes.mp4"
EVAL_PATH = LOCAL_DIR / "eval_results.jsonl"
OLLAMA_URL = SETTINGS.ollama_base_url
OLLAMA_MODEL = SETTINGS.ollama_model

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

orchestrator = HyperFramesOrchestrator(
    ollama_url=OLLAMA_URL,
    model=OLLAMA_MODEL,
    workspace_dir=str(LOCAL_DIR / "workspace"),
)


# Referencia a la corrida activa: evita dos renders simultáneos sobre el mismo workspace y que el
# recolector de basura elimine la tarea a mitad de camino.
_current_run: asyncio.Task | None = None


def _run_in_progress() -> bool:
    return _current_run is not None and not _current_run.done()


async def _ollama_reachable() -> bool:
    """Comprueba de verdad si Ollama responde, para que el panel no muestre un estado inventado."""

    try:
        async with httpx.AsyncClient(timeout=1.5, trust_env=False) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


@app.get("/api/status")
async def get_status():
    return {
        "status": "ok",
        "orchestrator_state": orchestrator.state,
        "run_in_progress": _run_in_progress(),
        "ollama_url": OLLAMA_URL,
        "model": OLLAMA_MODEL,
        "ollama_reachable": await _ollama_reachable(),
        "npx_available": shutil.which("npx") is not None,
        "last_render": orchestrator.last_render.model_dump() if orchestrator.last_render else None,
        "last_eval": orchestrator.last_eval.model_dump() if orchestrator.last_eval else None,
    }


@app.post("/api/pipeline/run")
async def run_pipeline(brief: VideoBrief):
    global _current_run
    if _run_in_progress():
        raise HTTPException(status_code=409, detail="Ya hay un render en curso; espera a que termine")
    if "model" not in brief.model_fields_set:
        brief.model = OLLAMA_MODEL  # sin modelo explícito, manda el .env
    _current_run = asyncio.create_task(
        orchestrator.run_pipeline(brief, output_path=str(OUTPUT_PATH))
    )
    return {"message": "Pipeline iniciado", "brief": brief}


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


@app.get("/api/video")
async def get_video():
    if not orchestrator.last_render or not orchestrator.last_render.success:
        raise HTTPException(status_code=404, detail="No hay video renderizado disponible aún")
    video_path = Path(orchestrator.last_render.video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado")
    return FileResponse(path=str(video_path), media_type="video/mp4", filename=video_path.name)


@app.get("/api/composition/html", response_class=HTMLResponse)
async def get_composition_html():
    if not orchestrator.last_html:
        raise HTTPException(status_code=404, detail="No se ha generado HTML aún")
    return HTMLResponse(content=orchestrator.last_html)


@app.post("/api/export")
async def export_eval():
    if not orchestrator.last_eval:
        raise HTTPException(status_code=400, detail="No hay evaluación para exportar")
    target = export_evaluation_jsonl(orchestrator.last_eval, output_path=EVAL_PATH)
    return {"status": "exported", "path": str(target.relative_to(lab_root()))}


# Servir Frontend
FRONTEND_DIR = lab_root() / "frontend"


@app.get("/app.js", include_in_schema=False)
async def serve_app_js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="text/javascript")


@app.get("/styles.css", include_in_schema=False)
async def serve_styles():
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>22-hyperframes-video-studio API activa</h1>")


def run_demo_cli():
    """Ejecutor de demostración desde CLI."""
    print("=== BL_Loops: Laboratorio 22 - HyperFrames Video Studio ===")
    brief = VideoBrief(
        topic="Explicar qué es HyperFrames, cómo usarlo y qué puede hacer",
        target_duration=15.0,
        model=OLLAMA_MODEL,
    )
    print(f"1. Conectando a Ollama ({OLLAMA_URL}) con modelo: {brief.model}")
    print(f"2. Brief de video: '{brief.topic}' ({brief.target_duration}s)")

    orch = HyperFramesOrchestrator(
        ollama_url=OLLAMA_URL, model=brief.model, workspace_dir=str(LOCAL_DIR / "workspace")
    )

    async def main_coro():
        res = await orch.run_pipeline(brief, output_path=str(OUTPUT_PATH))
        source = orch.director.last_source
        reason = orch.director.last_fallback_reason
        print(f"3. Origen de las escenas: {source}" + (f" ({reason})" if reason else ""))
        if res.success:
            print("\n========================================================")
            print("[OK] VIDEO RENDERIZADO EXITOSAMENTE:")
            print(f"   - Archivo: {Path(res.video_path).relative_to(lab_root()).as_posix()}")
            print(f"   - Duración: {res.duration}s")
            print(f"   - Resolución: {res.width}x{res.height} ({res.fps} FPS)")
            print(f"   - Tamaño: {round(res.file_size_bytes / 1024.0, 2)} KB")
            print(f"   - Tiempo de render: {res.render_elapsed_seconds}s")
            print("========================================================\n")
            # Exportar evaluación
            if orch.last_eval:
                target_jsonl = export_evaluation_jsonl(orch.last_eval, output_path=EVAL_PATH)
                print(f"[OK] Evaluación exportada a: {target_jsonl.relative_to(lab_root())}")
                print(f"[OK] Aprobada: {orch.last_eval.success}")
        else:
            print(f"[ERROR] Error durante el renderizado: {res.error}")
            sys.exit(1)

    asyncio.run(main_coro())


if __name__ == "__main__":
    uvicorn.run("hyperframes_studio.main:app", host=SETTINGS.host, port=SETTINGS.port, reload=True)

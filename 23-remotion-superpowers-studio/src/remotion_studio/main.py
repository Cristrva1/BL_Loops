"""Servidor FastAPI y CLI para 23-remotion-superpowers-studio."""

import asyncio
import shutil
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from remotion_studio.config import ConfigurationError, Settings, lab_root
from remotion_studio.evaluation import export_evaluation_jsonl
from remotion_studio.orchestrator import RemotionOrchestrator
from remotion_studio.schemas import RemotionBrief

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

app = FastAPI(
    title="Remotion Superpowers Studio",
    description="Estudio visual y pipeline de renderizado de video en React con IA Local (Ollama)",
    version="0.1.0",
)

# Configuración validada: Ollama solo en loopback y servidor solo en una interfaz local.
try:
    SETTINGS = Settings.load()
except ConfigurationError as exc:
    print(f"Configuracion invalida: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc
OLLAMA_URL = SETTINGS.ollama_base_url
OLLAMA_MODEL = SETTINGS.ollama_model
LAB_ROOT = lab_root()
OUTPUT_PATH = LAB_ROOT / ".local" / "output" / "remotion_superpowers.mp4"
EVAL_PATH = LAB_ROOT / ".local" / "eval_results.jsonl"

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
orchestrator = RemotionOrchestrator(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL, root_dir=LAB_ROOT)


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
async def run_pipeline(brief: RemotionBrief):
    global _current_run
    if _run_in_progress():
        raise HTTPException(status_code=409, detail="Ya hay un render en curso; espera a que termine")
    if "model" not in brief.model_fields_set:
        brief.model = OLLAMA_MODEL  # sin modelo explícito, manda el .env
    _current_run = asyncio.create_task(
        orchestrator.run_pipeline(brief, output_path=str(OUTPUT_PATH))
    )
    return {"message": "Pipeline de Remotion iniciado", "brief": brief}


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
        raise HTTPException(status_code=404, detail="No hay video disponible")
    video_path = Path(orchestrator.last_render.video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado")
    return FileResponse(path=str(video_path), media_type="video/mp4", filename=video_path.name)


@app.get("/api/scenes")
async def get_scenes():
    scenes_file = LAB_ROOT / "src" / "video_composition" / "scenes.json"
    if scenes_file.exists():
        return HTMLResponse(content=scenes_file.read_text(encoding="utf-8"), media_type="application/json")
    return []


@app.post("/api/export")
async def export_eval():
    if not orchestrator.last_eval:
        raise HTTPException(status_code=400, detail="No hay evaluación para exportar")
    target = export_evaluation_jsonl(orchestrator.last_eval, output_path=EVAL_PATH)
    return {"status": "exported", "path": str(target.relative_to(LAB_ROOT))}


FRONTEND_DIR = LAB_ROOT / "frontend"


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
    return HTMLResponse(content="<h1>23-remotion-superpowers-studio API activa</h1>")


def run_demo_cli():
    print("=== BL_Loops: Laboratorio 23 - Remotion Superpowers Studio ===")
    brief = RemotionBrief(
        topic="Demostrar Remotion y el patrón Remotion Superpowers con React y IA Local",
        target_duration=12.0,
        model=OLLAMA_MODEL,
    )
    print(f"1. Conectando a Ollama ({OLLAMA_URL}) con modelo: {brief.model}")
    print(f"2. Brief de video: '{brief.topic}' ({brief.target_duration}s @ {brief.fps} FPS)")

    orch = RemotionOrchestrator(ollama_url=OLLAMA_URL, model=brief.model, root_dir=LAB_ROOT)

    async def main_coro():
        res = await orch.run_pipeline(brief, output_path=str(OUTPUT_PATH))
        source = orch.director.last_source
        reason = orch.director.last_fallback_reason
        print(f"3. Origen de las escenas: {source}" + (f" ({reason})" if reason else ""))
        if res.success:
            print("\n========================================================")
            print("[OK] VIDEO REMOTION RENDERIZADO EXITOSAMENTE:")
            print(f"   - Archivo: {Path(res.video_path).relative_to(LAB_ROOT).as_posix()}")
            print(f"   - Duración: {res.duration}s")
            print(f"   - Resolución: {res.width}x{res.height} ({res.fps} FPS)")
            print(f"   - Fotogramas Totales: {res.total_frames}")
            print(f"   - Tamaño: {round(res.file_size_bytes / 1024.0, 2)} KB")
            print(f"   - Tiempo de render: {res.render_elapsed_seconds}s")
            print("========================================================\n")
            if orch.last_eval:
                target_jsonl = export_evaluation_jsonl(orch.last_eval, output_path=EVAL_PATH)
                print(f"[OK] Evaluación exportada a: {target_jsonl.relative_to(LAB_ROOT)}")
                print(f"[OK] Aprobada: {orch.last_eval.success}")
        else:
            print(f"[ERROR] Error durante el renderizado: {res.error}")
            sys.exit(1)

    asyncio.run(main_coro())


if __name__ == "__main__":
    uvicorn.run("remotion_studio.main:app", host=SETTINGS.host, port=SETTINGS.port, reload=True)

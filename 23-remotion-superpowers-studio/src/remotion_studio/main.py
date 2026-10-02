"""Servidor FastAPI y CLI para 23-remotion-superpowers-studio."""

import asyncio
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
import uvicorn

from remotion_studio.orchestrator import RemotionOrchestrator
from remotion_studio.schemas import RemotionBrief
from remotion_studio.evaluation import export_evaluation_jsonl

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

app = FastAPI(
    title="Remotion Superpowers Studio",
    description="Estudio visual y pipeline de renderizado de video en React con IA Local (Ollama)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
LAB_ROOT = Path(__file__).resolve().parent.parent.parent
orchestrator = RemotionOrchestrator(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL, root_dir=LAB_ROOT)


@app.get("/api/status")
async def get_status():
    return {
        "status": "ok",
        "orchestrator_state": orchestrator.state,
        "ollama_url": OLLAMA_URL,
        "model": OLLAMA_MODEL,
        "last_render": orchestrator.last_render.model_dump() if orchestrator.last_render else None,
        "last_eval": orchestrator.last_eval.model_dump() if orchestrator.last_eval else None,
    }


@app.post("/api/pipeline/run")
async def run_pipeline(brief: RemotionBrief):
    asyncio.create_task(orchestrator.run_pipeline(brief))
    return {"message": "Pipeline de Remotion iniciado", "brief": brief}


@app.get("/api/pipeline/events")
async def pipeline_events():
    queue = orchestrator.subscribe()

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {event.model_dump_json()}\n\n"
        except asyncio.CancelledError:
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
    target = export_evaluation_jsonl(orchestrator.last_eval)
    return {"status": "exported", "path": str(target)}


FRONTEND_DIR = LAB_ROOT / "frontend"


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
        res = await orch.run_pipeline(brief)
        if res.success:
            print("\n========================================================")
            print("[OK] VIDEO REMOTION RENDERIZADO EXITOSAMENTE:")
            print(f"   - Archivo: {res.video_path}")
            print(f"   - Duración: {res.duration}s")
            print(f"   - Resolución: {res.width}x{res.height} ({res.fps} FPS)")
            print(f"   - Fotogramas Totales: {res.total_frames}")
            print(f"   - Tamaño: {round(res.file_size_bytes / 1024.0, 2)} KB")
            print(f"   - Tiempo de render: {res.render_elapsed_seconds}s")
            print("========================================================\n")
            if orch.last_eval:
                target_jsonl = export_evaluation_jsonl(orch.last_eval)
                print(f"[OK] Evaluación exportada a: {target_jsonl}")
        else:
            print(f"[ERROR] Error durante el renderizado: {res.error}")
            sys.exit(1)

    asyncio.run(main_coro())


if __name__ == "__main__":
    uvicorn.run("remotion_studio.main:app", host="127.0.0.1", port=8023, reload=True)

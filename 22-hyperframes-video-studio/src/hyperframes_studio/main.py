"""Servidor FastAPI y CLI para 22-hyperframes-video-studio."""

import asyncio
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
import uvicorn

from hyperframes_studio.orchestrator import HyperFramesOrchestrator
from hyperframes_studio.schemas import VideoBrief
from hyperframes_studio.evaluation import export_evaluation_jsonl

# Configurar stdout para evitar fallos de encoding en Windows cp1252
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

app = FastAPI(
    title="HyperFrames Video Studio",
    description="Estudio visual y pipeline de renderizado de video HTML con IA Local (Ollama)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de estado y orquestador
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
orchestrator = HyperFramesOrchestrator(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL)


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
async def run_pipeline(brief: VideoBrief):
    # Ejecuta el pipeline en segundo plano
    asyncio.create_task(orchestrator.run_pipeline(brief))
    return {"message": "Pipeline iniciado", "brief": brief}


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
    target = export_evaluation_jsonl(orchestrator.last_eval)
    return {"status": "exported", "path": str(target)}


# Servir Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


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

    orch = HyperFramesOrchestrator(ollama_url=OLLAMA_URL, model=brief.model)

    async def main_coro():
        res = await orch.run_pipeline(brief)
        if res.success:
            print("\n========================================================")
            print("[OK] VIDEO RENDERIZADO EXITOSAMENTE:")
            print(f"   - Archivo: {res.video_path}")
            print(f"   - Duración: {res.duration}s")
            print(f"   - Resolución: {res.width}x{res.height} ({res.fps} FPS)")
            print(f"   - Tamaño: {round(res.file_size_bytes / 1024.0, 2)} KB")
            print(f"   - Tiempo de render: {res.render_elapsed_seconds}s")
            print("========================================================\n")
            # Exportar evaluación
            if orch.last_eval:
                target_jsonl = export_evaluation_jsonl(orch.last_eval)
                print(f"[OK] Evaluación exportada a: {target_jsonl}")
        else:
            print(f"[ERROR] Error durante el renderizado: {res.error}")
            sys.exit(1)

    asyncio.run(main_coro())


if __name__ == "__main__":
    uvicorn.run("hyperframes_studio.main:app", host="127.0.0.1", port=8022, reload=True)

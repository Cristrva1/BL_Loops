# Laboratorio 25: Resúmenes Inteligentes de Videollamadas (`25-meeting-summarizer`)

Herramienta autónoma y visual para convertir transcripciones de reuniones de videollamadas (Google Meet, Zoom, Microsoft Teams, tl;dv, texto libre) en resúmenes ejecutivos, decisiones clave, matrices de compromisos y minutas de seguimiento utilizando IA local con Ollama.

## Arquitectura rápida

- **Backend**: FastAPI + Python 3.12 + SQLite + SSE en el puerto `8025`.
- **Frontend**: React + Vite + TypeScript en el puerto `5175`.
- **Motor LLM**: Ollama local (`qwen3.5:9b`, `qwen3.5:4b`) vía `http://127.0.0.1:11434`.

## Inicio rápido

### 1. Backend (PowerShell)
```powershell
cd 25-meeting-summarizer
uv sync
uv run uvicorn meeting_summarizer.main:app --port 8025 --reload
```

### 2. Frontend (PowerShell)
```powershell
cd 25-meeting-summarizer/frontend
npm install
npm run dev
```

Abre tu navegador en `http://127.0.0.1:5175`.

### 3. Demostración CLI sin frontend
```powershell
cd 25-meeting-summarizer
uv run meeting-summarizer-demo
```

### 4. Pruebas automáticas
```powershell
cd 25-meeting-summarizer
uv run pytest
```

Para más detalles, consulta la documentación humana en [`docs/humano/README.md`](docs/humano/README.md).

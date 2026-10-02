# Inicio Rápido · Laboratorio 25 (`25-meeting-summarizer`)

Este documento explica paso a paso cómo iniciar y utilizar la herramienta de resúmenes de reuniones en tu máquina local.

## 1. Requisitos previos

1. **Python 3.12 y `uv`**:
   ```powershell
   uv --version
   ```
2. **Node.js (v18+) y `npm`**:
   ```powershell
   node --version
   npm --version
   ```
3. **Ollama local iniciado**:
   Asegúrate de que Ollama esté corriendo con el modelo `qwen3.5:9b`:
   ```powershell
   ollama list
   # Si no lo tienes descargado:
   ollama pull qwen3.5:9b
   ```

## 2. Iniciar el Backend (FastAPI en puerto 8025)

En una terminal PowerShell:

```powershell
cd c:\Users\criss\Desktop\Claude\BL_Loops\25-meeting-summarizer
uv sync
uv run uvicorn meeting_summarizer.main:app --host 127.0.0.1 --port 8025 --reload
```

Salida esperada:
```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8025 (Press CTRL+C to quit)
```

Puedes abrir `http://127.0.0.1:8025/docs` para explorar la documentación Swagger interactiva.

## 3. Iniciar el Frontend (React + Vite en puerto 5175)

En otra terminal PowerShell:

```powershell
cd c:\Users\criss\Desktop\Claude\BL_Loops\25-meeting-summarizer\frontend
npm install
npm run dev
```

Abre tu navegador en:
```text
http://127.0.0.1:5175
```

## 4. Uso de la herramienta

1. **Pegar o cargar transcripción**:
   - Puedes pegar directamente el texto de tu videollamada (Google Meet, Zoom, Teams o texto libre).
   - O hacer clic en los botones de "Ejemplo Rápido" para cargar una reunión de prueba (`Sprint Planning`, `Zoom Standup`, etc.).
2. **Seleccionar modelo y modo**:
   - Modelo: `qwen3.5:9b` (recomendado) o `qwen3.5:4b` (ultrarrápido).
   - Modo: *Completo* (minuta integral), *Ejecutivo* (TL;DR de 1 minuto), *Solo Tareas* o *Técnico*.
3. **Generar resumen**:
   - Haz clic en **"Generar Resumen Inteligente"**.
   - Observa la barra de progreso y los nodos visuales de análisis en tiempo real (vía SSE).
4. **Explorar resultados**:
   - Navega por las pestañas de **Resumen Ejecutivo**, **Decisiones Clave**, **Tareas y Compromisos** (con responsable y fecha), y **Minuta para Correo**.
   - Copia la minuta con 1 clic para enviarla a Slack, Teams o Email.
5. **Preguntar a la reunión**:
   - Escribe dudas como: *"¿Qué plazo fijó Ana para el frontend?"* o *"¿Se tomó alguna decisión sobre la base de datos?"* y recibe respuestas con evidencia.

## 5. Uso alternativo desde CLI (Consola)

También puedes procesar transcripciones directamente desde la terminal sin abrir la web:

```powershell
uv run meeting-summarizer summarize fixtures/meet_sprint_planning.txt
```

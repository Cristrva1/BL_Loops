# Inicio Rápido: 23-remotion-superpowers-studio

Guía de comandos paso a paso para configurar y ejecutar el laboratorio en Windows PowerShell.

## 1. Requisitos
- **Ollama**: En ejecución local (`http://127.0.0.1:11434`) con modelo `qwen3.5:9b`.
- **Node.js**: v22+ y npm (`node --version`).
- **uv**: Gestor de paquetes Python.
- **FFmpeg**: Disponible en el PATH.

## 2. Instalación

```powershell
cd 23-remotion-superpowers-studio

# 1. Sincronizar entorno virtual Python
uv sync

# 2. Instalar dependencias de Remotion y React
npm install
```

## 3. Demostración CLI

```powershell
uv run remotion-studio-demo
```
**Resultado:**
- Ollama genera las escenas y el cálculo de fotogramas.
- Se actualiza `src/video_composition/scenes.json`.
- `@remotion/cli` compila el video a `.local/output/remotion_superpowers.mp4`.
- Se genera el registro de evaluación en `.local/eval_results.jsonl`.

## 4. Previsualización en Remotion Studio

```powershell
npm run dev
```
Abre la interfaz interactiva de Remotion Studio en el navegador para reproducir cuadro a cuadro la composición.

## 5. Servidor API y Panel Visual

```powershell
uv run python -m remotion_studio.main
```
Abre `http://localhost:8023` para ver el grafo SSE de estados y el reproductor.

## 6. Pruebas Unitarias

```powershell
uv run pytest
```

# Inicio Rápido: 22-hyperframes-video-studio

Este documento detalla los comandos para poner en marcha y evaluar el laboratorio en Windows PowerShell.

## 1. Requisitos Previos
- **Ollama**: En ejecución local en `http://127.0.0.1:11434` con el modelo `qwen3.5:9b` (o `gemma4:e4b`).
- **Node.js**: v22 o superior (`node --version`).
- **FFmpeg**: Instalado y disponible en el PATH del sistema (`ffmpeg -version`).
- **uv**: Instalado para gestionar dependencias Python.

## 2. Preparación del Entorno

```powershell
# Acceder a la carpeta del laboratorio
cd 22-hyperframes-video-studio

# Crear y sincronizar el entorno virtual aislado con uv
uv sync
```

## 3. Diagnóstico de HyperFrames

```powershell
# Ejecutar el chequeo de dependencias de HyperFrames
npx hyperframes doctor
```
El resultado debe mostrar marcas de verificación verdes para Node.js, CPU, FFmpeg, FFprobe y Chrome Headless Shell.

## 4. Ejecución de la Demostración Completa

```powershell
# Ejecutar el flujo end-to-end (Ollama -> HTML -> Render MP4 -> JSONL)
uv run hyperframes-studio-demo
```
**Resultado esperado:**
- Se consulta el modelo local Ollama para el guión de 5 escenas.
- Se compila el HTML con animaciones GSAP.
- HyperFrames renderiza a 30 FPS generando `.local/output/tutorial_hyperframes.mp4`.
- Se registra la evaluación en `.local/eval_results.jsonl`.

## 5. Iniciar la Aplicación Web

```powershell
uv run python -m hyperframes_studio.main
```
Abre tu navegador en `http://localhost:8022` para interactuar con la consola de estados SSE, el reproductor de video y el visor HTML.

## 6. Ejecutar Pruebas Automatizadas

```powershell
uv run pytest
```

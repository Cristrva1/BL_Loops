# Laboratorio 22: HyperFrames Video Studio (IA Local)

Laboratorio didáctico y autónomo para evaluar el framework de video HTML **HyperFrames** (`heygen-com/hyperframes`) integrándolo con IA Local (**Ollama**).

El laboratorio utiliza un modelo local (`qwen3.5:9b`) como Director Audiovisual e Ingeniero de Animación para generar automáticamente un video explicativo que enseña qué es HyperFrames, su modelo de composición seekable, sus atributos HTML y su renderizado determinista a MP4 a 60/30 FPS.

## Inicio Rápido

```powershell
# 1. Instalar dependencias Python
cd 22-hyperframes-video-studio
uv sync

# 2. Ejecutar la demostración de generación y renderizado
uv run hyperframes-studio-demo

# 3. Iniciar el servidor API y estudio web
uv run python -m hyperframes_studio.main
```

## Arquitectura y Componentes
- **Orquestador Agéntico**: Genera guiones didácticos, escenas, timings, y código HTML con timelines GSAP.
- **Motor de Render**: `npx hyperframes render` impulsado por Chrome Headless Shell y FFmpeg local.
- **Visualizador SSE**: Trazas de nodos, estados, transiciones y métricas en tiempo real.
- **Evaluación y Exportación JSONL**: Suite determinista con criterios de validación temporal y estructural.

Consulta la guía completa en [docs/humano/README.md](docs/humano/README.md).

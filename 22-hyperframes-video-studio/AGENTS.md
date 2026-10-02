# AGENTS.md - 22-hyperframes-video-studio

Instrucciones operativas para futuras sesiones de agentes en este laboratorio.

## Propósito
Este laboratorio pone a prueba el motor `hyperframes` (HeyGen) generando videos estructurados mediante HTML/CSS/GSAP orquestados por IA Local (Ollama: `qwen3.5:9b`). Produce un video explicativo completo sobre qué es HyperFrames, su arquitectura seekable, sintaxis de composición y capacidades de renderizado determinista a MP4 con Chrome Headless y FFmpeg.

## Reglas locales
- No depender de servicios cloud ni modelos propietarios; todo funciona contra Ollama local (`127.0.0.1:11434`).
- El backend vive bajo `src/hyperframes_studio/`.
- Las pruebas unitarias viven en `tests/` y deben ejecutarse con `uv run pytest`.
- Los artefactos generados (renders MP4, HTMLs, JSONL de evaluación) se almacenan exclusivamente bajo `.local/`.
- El runtime jamás debe importar o requerir archivos ubicados dentro de `docs/humano/`.
- Cada ejecución emite trazas de eventos SSE para inspección en vivo de estados, transiciones y métricas.
- La exportación JSONL debe cumplir el esquema estándar de evaluación de `BL_Loops`.

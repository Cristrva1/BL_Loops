# 22 · HyperFrames Video Studio: video desde HTML con IA local

> **Pregunta:** ¿cómo puede un modelo local «dirigir» un video si quien lo dibuja es un motor
> determinista que renderiza HTML?
> **Nivel:** 5 · **Tiempo:** ~45 min · **Necesita Ollama:** opcional (sin él, el respaldo es visible)
> · **Necesita para renderizar:** Node.js 22+, FFmpeg y, la primera vez, red para descargar
> HyperFrames y su Chrome headless

El modelo propone cinco escenas (titular, texto, colores y un fragmento de código). El estudio fija
la línea de tiempo, escribe una composición HTML con clips `data-start`/`data-duration` y una línea
de tiempo GSAP, la **valida con un lint local** y la renderiza con
[HyperFrames](https://github.com/heygen-com/hyperframes) (`npx hyperframes@0.8.34 render`).
`ffprobe` mide el MP4 y el resultado se exporta a JSONL. La telemetría de HyperFrames se desactiva en
cada render.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\22-hyperframes-video-studio
uv sync
uv run pytest                                   # 28 pruebas, sin red ni Ollama
uv run hyperframes-studio-demo                  # escenas + HTML + render + JSONL
uv run python -m hyperframes_studio.main        # panel en http://127.0.0.1:8022
```

## Qué deberías ver

Salida real de la demo **sin Ollama y sin Node.js**, que muestra los dos avisos honestos:

```text
=== BL_Loops: Laboratorio 22 - HyperFrames Video Studio ===
1. Conectando a Ollama (http://127.0.0.1:11434) con modelo: qwen3.5:9b
2. Brief de video: 'Explicar qué es HyperFrames, cómo usarlo y qué puede hacer' (15.0s)
Ollama no entregó escenas (All connection attempts failed); se usan escenas calibradas.
No se encontró npx: instala Node.js para renderizar con HyperFrames.
3. Origen de las escenas: fallback (ConnectError al consultar Ollama)
[ERROR] Error durante el renderizado: No se encontró npx: instala Node.js para renderizar con HyperFrames.
```

Con Node.js y FFmpeg, la demo renderiza `.local/output/tutorial_hyperframes.mp4` y añade una línea
a `.local/eval_results.jsonl`. Las salidas completas están en
[EXAMPLES.md](docs/humano/EXAMPLES.md).

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/hyperframes_studio/config.py` | Fusión de `.env` y rechazo de endpoints o modelos no locales |
| `src/hyperframes_studio/schemas.py` | Contratos: brief (5–60 s, modelo local), escena, eventos, render, evaluación |
| `src/hyperframes_studio/ollama_client.py` | Prompt del director, lectura de la respuesta y escenas calibradas |
| `src/hyperframes_studio/templates.py` | Composición HTML con texto escapado y `lint_composition()` |
| `src/hyperframes_studio/renderer.py` | Workspace, `npx hyperframes render` sin telemetría y medición con `ffprobe` |
| `src/hyperframes_studio/orchestrator.py` | Estados, eventos SSE, lint y evaluación |
| `src/hyperframes_studio/main.py` | API FastAPI, panel y demo |
| `frontend/` | Panel sin dependencias: nodos, video, HTML generado y trazas |
| `tests/` | Pruebas deterministas (configuración, plantilla, lint, API, telemetría, medición) |
| `.local/` | `workspace/index.html`, `output/*.mp4` y `eval_results.jsonl` (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): objetivo, conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): requisitos, demo, panel y pruebas.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): composición, lint, configuración y API.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [14-local-code-hermes](../14-local-code-hermes/README.md) en la ruta del nivel 5, o
directamente de [09-agentic-rag](../09-agentic-rag/README.md) si te interesa el fallback visible.
**Sigue con:** [23-remotion-superpowers-studio](../23-remotion-superpowers-studio/README.md), que
compone el video con React y fotogramas.

## Estado y límites

- **Implementado:** director con respaldo visible, composición HTML escapada, lint local, render con
  HyperFrames, medición con `ffprobe`, API con SSE, panel, demo, JSONL y pruebas.
- **Necesita red en el render:** `npx` descarga HyperFrames 0.8.34 la primera vez y la composición
  carga GSAP desde jsDelivr. Ollama y la API siguen siendo locales.
- **No hace:** audio, voz ni subtítulos; tampoco usa la nube de HeyGen.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

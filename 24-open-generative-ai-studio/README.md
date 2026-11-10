# 24 · Open Generative AI Studio: de una idea a un animatic

> **Pregunta:** ¿cómo se pasa de una sinopsis a un storyboard verificable y a una previsualización
> en video, sin confiar a ciegas en lo que responde el modelo?
> **Nivel:** 5 · **Tiempo:** ~45 min · **Necesita Ollama:** opcional (sin él, el respaldo es visible)
> · **Necesita FFmpeg:** sí, con `ffprobe`, para renderizar y medir

Estudio local con tres piezas: **Prompt Studio** expande una idea breve en un prompt cinematográfico
(positivo, negativo, cámara y paleta); **Storyboard Studio** pide a Ollama cuatro planos y valida su
contrato antes de usarlos; el **Animatic Engine** dibuja cada plano con FFmpeg durante su duración
real y mide el MP4 con `ffprobe`. Si Ollama falla o responde fuera de contrato, se usan planos
calibrados y el motivo aparece en la terminal, en el panel y en el JSONL.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\24-open-generative-ai-studio
uv sync
uv run pytest
uv run open-genai-demo                      # storyboard + animatic + JSONL
uv run python -m open_genai_studio.main     # panel en http://127.0.0.1:8024
```

## Qué deberías ver

Salida real de `uv run open-genai-demo` con FFmpeg instalado y **Ollama apagado**:

```text
=== BL_Loops: Laboratorio 24 - Open Generative AI Studio ===
1. Ollama: http://127.0.0.1:11434 | modelo: qwen3.5:9b
2. Proyecto: 'Expedición Nebular' (12.0s)
Storyboard calibrado en uso: ConnectError al consultar Ollama
3. Origen de los planos: fallback (ConnectError al consultar Ollama)
   - Plano 1: Extreme Wide Shot | Slow Pan Right | 3.0s | El Vasto Glaciar de Europa
   ...
4. Animatic renderizado:
   - Archivo: .local/output/open_genai_animatic.mp4
   - Duración medida: 12.0s | 1920x1080 a 30 fps
   - Tamaño: 179.52 KB
5. Evaluación exportada a .local/eval_results.jsonl
   - Aprobada: True
```

«Aprobada» se refiere al render (duración, tamaño y medición). La línea `Origen de los planos`
dice si el modelo participó: con `fallback`, la corrida no sirve como evidencia de calidad del
modelo. Con Ollama activo, esa línea muestra `ollama` y los planos cambian en cada corrida.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/open_genai_studio/config.py` | Lee `.env` por fusión de claves y rechaza endpoints o modelos no locales |
| `src/open_genai_studio/schemas.py` | Contratos Pydantic: planos, peticiones, eventos, render y evaluación |
| `src/open_genai_studio/model_output.py` | Quita vallas Markdown, interpreta JSON y resume errores |
| `src/open_genai_studio/storyboard_engine.py` | Prompt de storyboard, validación de 4 planos y respaldo calibrado |
| `src/open_genai_studio/prompt_expander.py` | Prompt Studio con salida normalizada a cuatro claves |
| `src/open_genai_studio/animatic_renderer.py` | Filtergraph de FFmpeg, escapado de texto, fuentes y medición |
| `src/open_genai_studio/orchestrator.py` | Estados, eventos SSE y evaluación de la corrida |
| `src/open_genai_studio/main.py` | API FastAPI, panel y demo de terminal |
| `frontend/` | Panel sin dependencias externas: nodos, storyboard, Prompt Studio y trazas |
| `tests/` | 37 pruebas deterministas: sin red, sin Ollama; el render real se omite sin FFmpeg |
| `.local/` | Segmentos, MP4 y `eval_results.jsonl` (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): objetivo, conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): instalación, demo, panel y pruebas en PowerShell.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): salidas reales de la demo, la API y los contratos.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [23-remotion-superpowers-studio](../23-remotion-superpowers-studio/README.md), donde
el video se compone con código React.
**Sigue con:** es el último estudio de la [ruta de aprendizaje](../docs/humano/maestro/RUTA_DE_APRENDIZAJE.md).
Compara los JSONL de 22, 23 y 24: los tres registran `director_source` y `duration_measured`.

## Estado y límites

- **Implementado:** Prompt Studio, Storyboard Studio con contrato validado, animatic MP4 con FFmpeg,
  medición con `ffprobe`, API con SSE, panel local, demo de terminal, exportación JSONL y pruebas.
- **No hace:** generar imágenes ni video con modelos de difusión. El animatic son tarjetas de texto
  que muestran tipo de plano, movimiento, luz y prompt; el movimiento de cámara no se anima.
- [Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) es solo una referencia
  conceptual: no se instala ni se copia código. Ver [METHODOLOGY.md](docs/humano/METHODOLOGY.md).
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

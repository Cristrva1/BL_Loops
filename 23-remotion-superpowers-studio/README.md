# 23 · Remotion Superpowers Studio: video con React y fotogramas

> **Pregunta:** ¿cómo se traduce «un video de 12 segundos» a fotogramas exactos que un componente
> React puede dibujar siempre igual?
> **Nivel:** 5 · **Tiempo:** ~45 min · **Necesita Ollama:** opcional (sin él, el respaldo es visible)
> · **Necesita para renderizar:** Node.js 22+, `npm ci` en el laboratorio y FFmpeg con `ffprobe`

El modelo propone el contenido de cuatro escenas; el estudio calcula los fotogramas
(`segundos × 30 fps`), escribe `src/video_composition/scenes.json` y
[Remotion](https://www.remotion.dev) renderiza la composición React `MainVideo` a MP4 con Chrome
headless. `ffprobe` mide el resultado y la evaluación se exporta a JSONL. El patrón de trabajo se
inspira en *Remotion Superpowers*: el agente edita datos tipados, no código de video.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\23-remotion-superpowers-studio
uv sync
npm ci                                         # Remotion, React y TypeScript del laboratorio
uv run pytest                                  # 21 pruebas, sin red ni Remotion
uv run remotion-studio-demo                    # escenas + scenes.json + render + JSONL
uv run python -m remotion_studio.main          # panel en http://127.0.0.1:8023
npm run dev                                    # Remotion Studio para ver la composición
```

## Qué deberías ver

Salida real de `uv run remotion-studio-demo` con Node.js y FFmpeg, **sin Ollama**:

```text
3. Origen de las escenas: fallback (ConnectError al consultar Ollama)

========================================================
[OK] VIDEO REMOTION RENDERIZADO EXITOSAMENTE:
   - Archivo: .local/output/remotion_superpowers.mp4
   - Duración: 12.0s
   - Resolución: 1920x1080 (30 FPS)
   - Fotogramas Totales: 360
   - Tamaño: 2644.73 KB
   - Tiempo de render: 29.53s
========================================================

[OK] Evaluación exportada a: .local/eval_results.jsonl
[OK] Aprobada: True
```

12 s × 30 fps = 360 fotogramas, 4 escenas de 90. La primera corrida tarda más porque Remotion
descarga su Chrome headless. Salidas completas en [EXAMPLES.md](docs/humano/EXAMPLES.md).

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/remotion_studio/config.py` | Fusión de `.env` y rechazo de endpoints o modelos no locales |
| `src/remotion_studio/schemas.py` | Contratos: brief (4–60 s, 1920×1080 a 30 fps, modelo local), escena, eventos |
| `src/remotion_studio/ollama_director.py` | Prompt del director, cálculo de fotogramas y escenas calibradas |
| `src/remotion_studio/remotion_renderer.py` | `scenes.json` con estilos validados, `remotion render` y `ffprobe` |
| `src/remotion_studio/orchestrator.py` | Estados, eventos SSE y evaluación |
| `src/remotion_studio/main.py` | API FastAPI, panel y demo |
| `src/video_composition/` | Composición React: `Root.tsx`, `MainComposition.tsx`, `SceneSequence.tsx` y `scenes.json` |
| `frontend/` | Panel sin dependencias: nodos, video, `scenes.json` y trazas |
| `tests/` | Pruebas deterministas de Python |
| `.local/` | `output/remotion_superpowers.mp4` y `eval_results.jsonl` (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): objetivo, conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): Python, Node.js, demo, Studio y panel.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): fotogramas, `scenes.json`, render real y API.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [22-hyperframes-video-studio](../22-hyperframes-video-studio/README.md), donde el
video es HTML con tiempos en segundos.
**Sigue con:** [24-open-generative-ai-studio](../24-open-generative-ai-studio/README.md), que valida
un storyboard y renderiza con FFmpeg directo.

## Estado y límites

- **Implementado:** director con respaldo visible, cálculo de fotogramas, `scenes.json` con estilos
  validados, render con `@remotion/cli` 4.0.523, medición con `ffprobe`, API con SSE, panel, demo,
  JSONL y pruebas.
- **Cada corrida reescribe** `src/video_composition/scenes.json`, que está versionado porque es la
  entrada de la composición. La versión del repositorio coincide con las escenas calibradas; tras
  una corrida con Ollama, `git restore src/video_composition/scenes.json` la recupera.
- **Licencia de Remotion:** gratuita para personas, empresas de hasta 3 empleados, organizaciones
  sin ánimo de lucro y evaluación; el resto necesita licencia de empresa. Ver `node_modules/remotion/LICENSE.md`.
- **No hace:** audio, voz ni subtítulos.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

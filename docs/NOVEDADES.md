# Novedades de BL_Loops

> Registro de cambios visibles. Cada entrada dice **qué cambió**, **para quién** y **dónde verlo**.
> Lo más reciente va primero. Los cambios de arquitectura se deciden en el
> [plan maestro](PLAN_MAESTRO_DIDACTICO.md); este registro solo los resume.

## 2026-11-05 · Revisión didáctica de todos los laboratorios

### Para estudiantes: nuevas formas de aprender

| Novedad | Dónde verla |
|---|---|
| Ruta de aprendizaje por niveles, con tiempos, requisitos y puntos de control | [RUTA_DE_APRENDIZAJE.md](humano/maestro/RUTA_DE_APRENDIZAJE.md) |
| Glosario común con ejemplo y laboratorio para cada término, ahora con una sección de video generado por código | [GLOSARIO.md](humano/maestro/GLOSARIO.md) |
| `docs/humano/EXAMPLES.md` en los quince laboratorios: entrada, comando, qué observar y salida **real** | La carpeta `docs/humano/` de cada laboratorio |
| Ejercicios con solución plegable y comprobada | `docs/humano/EXERCISES.md` de cada laboratorio |
| Mapa de puertos de todos los laboratorios | [QUICKSTART del maestro](humano/maestro/QUICKSTART.md#mapa-de-puertos) |
| Tabla de precedencia del `.env` (fusión por clave, archivo único, sin dotenv) | [ENVIRONMENTS.md](humano/maestro/ENVIRONMENTS.md#precedencia-actual) |

### Nuevas herramientas en los laboratorios

| Laboratorio | Novedad | Cómo probarla |
|---|---|---|
| 01 | La demo procesa cualquier briefing: `--list`, `--intake <archivo>` y `--all`; cuatro briefings nuevos | `uv run factory-demo --list` |
| 02 | Comandos de chat `/ayuda`, `/memoria` y `/olvidar` para ver y vaciar la memoria de sesión | `uv run single-agent` |
| 03 | `orchestration-score` puntúa guías Markdown con el gate determinista; tres guías de ejemplo | `uv run orchestration-score examples/guides/*.md` |
| 05 | `agent-loops-score` puntúa salidas de ejemplo del loop | `uv run agent-loops-score examples/outputs/*` |
| 06 | Subcomando `search` para ver qué recupera el índice sin llamar al modelo | `uv run naive-rag search "..."` |
| 22 | Lint local de la composición antes del render | [EXAMPLES del 22](../22-hyperframes-video-studio/docs/humano/EXAMPLES.md#ejemplo-4-el-lint-local-en-acción) |
| 23 | `npm run typecheck` y render de fotogramas sueltos con `npx remotion still` | [EXAMPLES del 23](../23-remotion-superpowers-studio/docs/humano/EXAMPLES.md#ejemplo-5-renderizar-un-solo-fotograma) |
| 24 | **Laboratorio completado**: API, panel, Prompt Studio, storyboard con contrato, animatic con FFmpeg, 37 pruebas y documentación completa | [README del 24](../24-open-generative-ai-studio/README.md) |
| 25 | Subcomando `parse` (sin Ollama) con `--max-words` y `--overlap-words`; dos transcripciones nuevas | `uv run meeting-summarizer parse .\fixtures\zoom_standup.vtt` |

### Correcciones que cambian lo que ves

| Laboratorio | Antes | Ahora |
|---|---|---|
| 01 | Las pruebas fallaban en un clon limpio (necesitaban `.env` y `.local/`) | Pasan sin `.env`, sin `.local/` y sin Ollama, como en el resto de laboratorios |
| 03, 04, 05 | Carrera: `run.completed` podía llegar al panel antes que los resultados | El evento terminal se publica junto con el resultado final; hay prueba de regresión |
| 08 | El diagrama Mermaid dibujaba al revés los saltos inversos | Las flechas siguen la dirección real y el predicado inverso se marca con `^` |
| 22 | El fragmento de código de la escena 2 se convertía en un clip HTML real y su texto no se veía; el nodo «Linter» no comprobaba nada | Texto escapado, ids y CSS en lista blanca, y un lint real que detiene la corrida antes de abrir Chrome |
| 22 | HyperFrames enviaba telemetría anónima por defecto | Cada render recibe `HYPERFRAMES_NO_TELEMETRY=1` y `DO_NOT_TRACK=1` |
| 22, 23 | `ffprobe` inventaba 1920×1080 a 30 fps (y 360 fotogramas en el 23) si no había pista de video | Sin medición, ceros: la evaluación no aprueba a ciegas |
| 22, 23, 24 | Un brief podía pedir un modelo `cloud`, otra resolución u otros fps que el render ignoraba | `422` con el campo exacto; la resolución y los fps quedan fijados en el contrato |
| 22, 23 | Dos corridas simultáneas compartían workspace; el panel duplicaba eventos al reconectar | `409` mientras hay una corrida activa; una sola conexión SSE |
| 23 | `tsc` fallaba al importar `scenes.json`; el `scenes.json` versionado no coincidía con las escenas calibradas | `resolveJsonModule` activado y archivo sincronizado: una corrida sin Ollama ya no ensucia Git |
| 24 | El renderizador omitía en silencio un plano fallido y declaraba éxito con un video más corto; el texto del modelo podía romper el filtro `drawtext` | Fallo explícito («FFmpeg no pudo generar el plano N»), texto y fuentes escapados, colores validados |
| 25 | El JSONL guardaba el informe completo, con nombres y tareas | Solo métricas y `report_sha256`; el informe vive en SQLite local |
| 25 | El dashboard usaba el puerto 5175, el mismo que el 04; no se validaba que Ollama fuera local | Puerto 5177 y validación de endpoint y modelo locales |
| 22, 23 | `.env.example` anunciaba variables que el código no leía | Solo las claves reales, con su precedencia explicada |

### Para mantenedores

- `AGENTS.md` de la raíz: `EXAMPLES.md` forma parte del contrato didáctico y sus salidas deben ser
  reales; las pruebas deben pasar en un clon limpio con `--basetemp=.pytest-tmp`; los puertos se
  eligen con el mapa del QUICKSTART maestro; la ruta y el glosario se actualizan al añadir un
  laboratorio o un concepto.
- Los laboratorios 22–24 fijan Python 3.12 en `pyproject.toml` y `uv.lock`, y declaran sus reglas de
  `ruff` (`E`, `F`, `I`, `UP`, `B`, `SIM`).
- Los README y `AGENTS.md` de cada laboratorio siguen una misma estructura: pregunta, nivel, cómo
  ejecutarlo en 5 minutos, qué deberías ver, mapa, ruta de aprendizaje y límites.

### Verificación de esta revisión

- Pruebas de los quince laboratorios en verde, sin `.env`, sin `.local/` y sin Ollama.
- Demos ejecutadas sin Ollama: el fallback aparece en la terminal, los eventos y el JSONL.
- Renders reales: animatic del 24 con FFmpeg y video del 23 con Remotion (12,0 s, 360 fotogramas).
- El render del 22 con HyperFrames **no** se ejecutó en esta revisión; se verificó con pruebas, la
  demo sin `npx`, la API y el análisis del paquete `hyperframes@0.8.34` sin ejecutarlo.
- Enlaces internos de toda la documentación comprobados.

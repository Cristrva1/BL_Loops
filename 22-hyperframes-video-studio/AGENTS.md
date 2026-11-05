# Instrucciones de trabajo de 22-hyperframes-video-studio

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz;
al copiar la carpeta, conservan sus límites esenciales.

## Objetivo y estado

- Enseña a separar **dirección** (el modelo propone escenas) de **render determinista** (HyperFrames
  convierte HTML en MP4) con validación y medición en medio.
- Implementado: director Ollama con escenas calibradas de respaldo, composición HTML
  (`templates.py`), lint local (`lint_composition()`), render con `npx hyperframes@0.8.34 render`,
  medición con `ffprobe`, API FastAPI con SSE y panel, demo `hyperframes-studio-demo`, JSONL y pruebas.
- No presentar como existentes: audio, voz, subtítulos, render en la nube de HeyGen ni el
  `npx hyperframes lint` oficial (el lint del laboratorio es propio y local).

## Separación y seguridad

- `src/`, `frontend/` y `tests/` son operativos; `docs/humano/` es enseñanza y nunca una dependencia
  del runtime.
- Solo se admite Ollama por HTTP en loopback y modelos sin etiqueta cloud, también en el campo
  `model` de cada brief (`schemas.py`). La validación tiene pruebas.
- Todo texto del modelo es **dato**: en la composición pasa por `html.escape`; ids, colores y
  gradientes se validan con listas blancas. En el panel se usa `textContent`.
- La línea de tiempo la fija el estudio (escenas contiguas que suman la duración pedida); el lint la
  comprueba antes de abrir Chrome y detiene la corrida si falla.
- El subproceso de render siempre recibe `HYPERFRAMES_NO_TELEMETRY=1` y `DO_NOT_TRACK=1`
  (`renderer.py`). No quitar esa exclusión.
- Sin medición no hay métricas: si `ffprobe` falla o no hay pista de video, se registran ceros.
- No añadir fallback cloud ni recursos remotos al panel.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio (Python 3.12).
- Configuración por **fusión de claves**: `.env` de la raíz, después el del laboratorio y por último
  las variables del proceso. Contrato en `.env.example`.
- Puerto propio: `127.0.0.1:8022`. CORS solo admite ese origen.
- Artefactos bajo `.local/`: `workspace/` (HTML y configuración de HyperFrames), `output/` y
  `eval_results.jsonl`.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md`, `docs/humano/EXAMPLES.md` y el documento humano relacionado con la tarea.
3. Escribir o ajustar primero la prueba determinista. Las pruebas no usan red ni lanzan HyperFrames.
4. Si cambias la plantilla, ejecuta `lint_composition()` sobre las escenas calibradas y actualiza
   `docs/humano/EXAMPLES.md`.
5. Actualizar documentación y pruebas en el mismo cambio.
6. No hacer commit, push, publicación ni descargas de modelos sin solicitud explícita.

## Verificación

```powershell
uv sync
uv run pytest
uv run ruff check .
uv run hyperframes-studio-demo
```

La demo necesita Node.js 22+ y FFmpeg para renderizar; sin `npx` debe terminar con el mensaje
`No se encontró npx: ...` y código `1`.

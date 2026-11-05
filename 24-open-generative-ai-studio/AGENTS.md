# Instrucciones de trabajo de 24-open-generative-ai-studio

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz;
al copiar la carpeta, conservan sus límites esenciales.

## Objetivo y estado

- Enseña el recorrido idea → storyboard → animatic con IA local: el modelo propone, el contrato
  valida y FFmpeg produce un MP4 que se mide con `ffprobe`.
- Implementado: Prompt Studio (`prompt_expander.py`), Storyboard Studio (`storyboard_engine.py`),
  Animatic Engine (`animatic_renderer.py`), orquestador con eventos SSE, API FastAPI con panel
  (`main.py` + `frontend/`), demo `open-genai-demo`, exportación JSONL y pruebas.
- No presentar como existentes: generación de imágenes o video por difusión, animación real del
  movimiento de cámara, audio, ni integración con el proyecto Open-Generative-AI.

## Separación y seguridad

- `src/`, `frontend/` y `tests/` son operativos; `docs/humano/` es enseñanza y nunca una dependencia
  del runtime.
- No importar código, configuración mutable ni servicios de otro laboratorio.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`, y modelos sin etiqueta cloud.
  La validación vive en `config.py` y también protege el campo `model` de las peticiones
  (`schemas.py`). Tiene pruebas.
- Todo texto del modelo es **dato**: en FFmpeg pasa por `drawtext_value()` y `safe_hex_color()`; en el
  panel se inserta con `textContent`, nunca con `innerHTML`.
- Un fallo nunca es silencioso: el respaldo calibrado publica `director_source=fallback` y su motivo;
  un plano que FFmpeg no genera detiene el render con un error explícito; sin `ffprobe` las métricas
  quedan en cero.
- No añadir fallback cloud, telemetría, fuentes o scripts remotos en el panel.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio (Python 3.12).
- Configuración por **fusión de claves**: `.env` de la raíz de BL_Loops, después el `.env` de este
  laboratorio (gana clave a clave) y por último las variables del proceso. Contrato en `.env.example`.
- Puerto propio: `127.0.0.1:8024`. CORS solo admite ese origen.
- `ANIMATIC_FONT_FILE` es opcional; si falta, se busca una fuente del sistema (`FONT_CANDIDATES`).
- Artefactos bajo `.local/` de este laboratorio: `workspace/`, `output/open_genai_animatic.mp4` y
  `eval_results.jsonl`.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md`, `docs/humano/EXAMPLES.md` y el documento humano relacionado con la tarea.
3. Escribir o ajustar primero la prueba determinista que demuestra el cambio. Las pruebas no usan red:
   Ollama se sustituye con `httpx.MockTransport`.
4. Si cambias el texto de los planos, el escapado o el filtergraph, ejecuta la demo con FFmpeg y
   actualiza las salidas de `docs/humano/EXAMPLES.md`.
5. Actualizar documentación y pruebas en el mismo cambio.
6. No hacer commit, push, publicación ni descargas de modelos sin solicitud explícita.

## Verificación

```powershell
uv sync
uv run pytest
uv run ruff check .
uv run open-genai-demo
```

La demo necesita FFmpeg y `ffprobe` en el `PATH`; Ollama es opcional. Sin Ollama, la salida debe
mostrar `Origen de los planos: fallback (...)`.

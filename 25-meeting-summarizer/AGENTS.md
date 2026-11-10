# Instrucciones de trabajo de 25-meeting-summarizer

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz;
al copiar la carpeta, conservan sus límites esenciales.

## Objetivo y estado

- Enseña a convertir transcripciones de videollamadas (Meet, Zoom WebVTT, Teams, texto libre) en una
  minuta estructurada: resumen, temas, decisiones, compromisos, preguntas abiertas y correo de
  seguimiento.
- Implementado: parser multi-formato, troceador con solapamiento, single-pass hasta 3 200 palabras y
  map-reduce por encima, SQLite local, API FastAPI con SSE, dashboard React y CLI
  `parse`/`summarize`/`list`.
- `parse` es determinista y no invoca Ollama; `summarize` sí.
- No presentar transcripción de audio, conexión a plataformas de videollamada, envío de correos o
  mensajes, ni evaluación automática de calidad como capacidades existentes.

## Separación y seguridad

- `backend/`, `frontend/` y `fixtures/` son operativos; `docs/humano/` es enseñanza y nunca una
  dependencia del runtime.
- No importar código, configuración mutable, bases de datos ni servicios de otro laboratorio.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`, y modelos sin etiqueta cloud.
  La validación vive en `config.py` y tiene pruebas.
- Las transcripciones contienen datos personales. Usar fixtures sintéticos o transcripciones propias
  con consentimiento. No versionar transcripciones reales.
- El informe completo vive solo en `.local/data/meetings.db`. La traza JSONL de `.local/runs/` guarda
  métricas y `report_sha256`, **nunca** nombres, tareas ni texto de la reunión.
- No añadir fallback cloud, telemetría ni conectores de correo o mensajería.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio, y `frontend/package-lock.json`.
- Configuración de **archivo único**: se usa el `.env` del laboratorio si existe; si no, el `.env` de
  la raíz de BL_Loops (solo si la carpeta superior es realmente el workspace). Las variables del
  proceso ganan siempre.
- Puertos: API `127.0.0.1:8025`, dashboard `127.0.0.1:5177` (preview `4177`). CORS solo admite el
  puerto del dashboard propio.
- Las rutas relativas se resuelven contra la raíz de este laboratorio.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md`, `docs/humano/EXAMPLES.md` y el documento humano relacionado con la tarea.
3. Escribir o ajustar primero la prueba determinista que demuestra el cambio.
4. Si cambias el parser, el troceador o sus límites (`SUMMARY_MAX_WORDS_PER_CHUNK`,
   `SUMMARY_OVERLAP_WORDS`), vuelve a ejecutar `parse` sobre los cinco fixtures y actualiza las salidas
   de `docs/humano/EXAMPLES.md`.
5. Actualizar documentación y pruebas en el mismo cambio.
6. No hacer commit, push, publicación ni descargas de modelos sin solicitud explícita.

## Verificación

```powershell
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run meeting-summarizer parse .\fixtures\zoom_standup.vtt
uv run meeting-summarizer parse .\fixtures\meet_sprint_planning.txt --max-words 120 --overlap-words 30
npm --prefix frontend run build
uv run meeting-summarizer summarize .\fixtures\meet_compromisos_ambiguos.txt
```

El último comando necesita Ollama con el modelo configurado. Comprueba después que el JSONL más
reciente de `.local/runs/` no contiene ningún nombre de participante.

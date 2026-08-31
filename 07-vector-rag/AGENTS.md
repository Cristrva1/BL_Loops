# Instrucciones de trabajo de 07-vector-rag

## Objetivo vigente

- Comparar recuperación `lexical`, `vector` e `hybrid` sobre el mismo corpus y top-k.
- La variante recomendada actual es híbrida: FTS5 + Qwen3 Embedding + RRF + citas.
- No presentar el filtro de calidad como verificación humana ni los vectores como corrección de
  datos falsos.

## Aislamiento y seguridad

- El proyecto no importa otro laboratorio. Toda proyección y corrida vive en su `.local/`.
- `docs/humano/` explica el runtime pero nunca se importa ni parsea durante la ejecución.
- La fuente Markdown es de solo lectura. Solo se aceptan Ollama y HTTP local.
- No usar proxy, redirecciones, cloud, telemetría ni reintentos automáticos.
- El JSONL no conserva preguntas, fragmentos o respuestas crudos.
- El índice contiene texto y vectores del corpus; permanece fuera de Git.

## Perfil durable

- Un índice queda ligado al modelo, dimensiones e instrucción de consulta usados al construirlo.
- Un cambio de cualquiera de esos valores exige reconstrucción completa y atómica.
- No mezclar vectores con dimensiones o perfiles diferentes.
- `Contexto (Wikipedia)`, `Fuentes y Adquisición`, `Metadatos` y `Temas (Open Library)` se excluyen
  por política explícita; cualquier nuevo filtro requiere prueba y documentación.

## Verificación

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag search --mode lexical "necesidad real"
uv run vector-rag search --mode vector "necesidad real"
uv run vector-rag ask "¿Cómo entender al comprador antes de ofrecer una solución?"
uv run vector-rag-validate
```

Antes de cerrar, repetir con el corpus objetivo y una paráfrasis real. No hacer commit, push,
descargas ni efectos externos salvo solicitud expresa.

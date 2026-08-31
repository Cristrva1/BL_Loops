# Instrucciones de trabajo de 06-naive-rag

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de
la raíz; al copiar la carpeta conservan los límites esenciales.

## Objetivo y estado

- Este corte enseña el RAG más simple: Markdown -> SQLite FTS5 -> contexto -> Ollama -> citas.
- La recuperación es léxica. No presentar embeddings, búsqueda semántica, memoria de chat,
  PDF/OCR, reranking, API web o dashboard como capacidades existentes.
- El corpus se importa explícitamente. La consulta solo depende del índice local generado.

## Separación y seguridad

- `src/`, `contracts/`, `fixtures/`, `examples/` y `tests/` son operativos;
  `docs/humano/` es enseñanza y nunca una dependencia del runtime.
- No importar código, configuración mutable, bases de datos ni servicios de otro laboratorio.
- La fuente Markdown es de solo lectura. Toda escritura se limita a `.local/` dentro del lab.
- El índice contiene texto recuperable del corpus: mantenerlo fuera de Git y tratarlo según la
  sensibilidad de la fuente.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`.
- No añadir fallback cloud, telemetría, conectores reales ni reintentos automáticos.
- El JSONL no guarda pregunta, fragmentos ni respuesta crudos.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se lee el `.env` raíz; fuera se admite un `.env` local derivado de
  `.env.example`.
- Las rutas de índice y corridas son relativas a esta raíz y no pueden escapar de ella.
- No añadir un modelo de embeddings: esta variante existe para medir primero FTS5.

## Forma de trabajar

1. Revisar `git status --short` y preservar todos los cambios previos.
2. Leer este archivo, `README.md` y el documento humano relacionado con la tarea.
3. Mantener una sola ruta explicable y estados observables derivados de eventos reales.
4. Escribir o ajustar pruebas deterministas antes de ampliar el runtime.
5. Actualizar documentación y pruebas en el mismo cambio.
6. No hacer commit, push, publicación, descargas ni escrituras externas sin solicitud expresa.

## Verificación

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run naive-rag index --source .\fixtures\evaluation-corpus
uv run naive-rag ask "¿Cuál es el plazo vigente de seguimiento LUNA y qué debe confirmarse?"
uv run naive-rag-validate
```

Antes de declarar el corte listo, repetir la indexación con el corpus objetivo, realizar una
pregunta real a Ollama y validar el JSONL resultante.


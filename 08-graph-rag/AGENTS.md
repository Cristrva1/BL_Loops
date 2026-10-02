# Instrucciones de trabajo de 08-graph-rag

## Objetivo vigente

- Enseñar cuándo una relación explícita justifica un grafo: una pregunta multi-hop del caso
  `A-RAG-GRAPH-001` recorre al menos dos aristas extraídas y marca la composición como inferida.
- Comparar esa ruta con recuperación léxica sobre el mismo corpus. No presentar FTS5 como
  equivalente a 07-vector-rag ni el grafo como una base de verdad.
- No adoptar Microsoft GraphRAG, Neo4j ni grafos de código en este corte.

## Aislamiento y seguridad

- El proyecto no importa otro laboratorio. Toda proyección y corrida vive en su `.local/`.
- `docs/humano/` explica el runtime pero nunca se importa ni parsea durante la ejecución.
- La fuente Markdown es de solo lectura. Solo se aceptan Ollama y HTTP local.
- No usar proxy, redirecciones, cloud, telemetría ni reintentos automáticos.
- El JSONL no conserva preguntas, rutas, fragmentos o respuestas crudos.
- El índice contiene texto y aristas del corpus; permanece fuera de Git.

## Extracción

- Solo se indexan triples visibles con la forma `` `Sujeto` --predicado--> `Objeto` ``.
- Esas aristas se guardan como `extracted`. Una ruta de dos o más saltos produce una arista
  `inferred` en consulta, nunca en SQLite.
- Un bucle, un enlace simbólico o un corpus sin aristas fallan de forma explícita.

## Verificación

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag search --mode graph "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag search --mode compare "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag-validate
```

Antes de cerrar, confirmar que la ruta pasa por `02-proyectos.md` y que el JSONL no guarda el
texto de la pregunta. No hacer commit, push, descargas ni efectos externos salvo solicitud expresa.

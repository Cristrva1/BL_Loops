# Diagnóstico

## El índice no existe

```powershell
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag stats
```

La consulta no lee la carpeta original. Si el SQLite falta o el schema cambió, hay que reconstruir.

## No hay rutas

La pregunta no contiene una etiqueta de nodo, o `GRAPH_RAG_MAX_HOPS` es menor que la distancia
real. Lista las semillas que imprime `search` y compara con los triples del fixture.

## El modo lexical parece suficiente

Abre `02-proyectos.md`. Si ese archivo no está en el ranking y sí está en la ruta, la coincidencia
léxica estaba incompleta aunque devolviera una fecha.

## Un bucle o un enlace simbólico abortan la indexación

Es intencional. Corrige el triple o copia el archivo real. El índice anterior permanece intacto.

## Ollama o JSONL

```powershell
ollama list
uv run graph-rag stats
uv run graph-rag-validate
```

El endpoint debe ser HTTP local y el JSONL debe terminar en `run.completed` o `run.failed`. La
traza no debe contener la pregunta ni los nombres de la ruta.

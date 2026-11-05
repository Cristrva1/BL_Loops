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

## La ruta útil no es la primera

Es lo esperado: las rutas se ordenan por longitud, no por pertinencia. El grafo enumera caminos desde
la semilla; elegir el que responde la pregunta es trabajo del modelo. Revisa el predicado de cada
ruta (`owns`, `depends_on`, `freeze_date`).

## Un diagrama Mermaid dibujaba una flecha al revés

Antes del 2026-11-05, los saltos inversos se dibujaban en el sentido del recorrido
(`AtlasCRM -->|owns| Ana_Ruiz`). Ahora se dibujan en el sentido del triple escrito y la arista
inferida marca los saltos inversos con `^`. Lo cubren
`test_reverse_hop_is_drawn_in_the_direction_of_the_written_triple` y
`test_inferred_edge_marks_reverse_hops_with_a_caret`.

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

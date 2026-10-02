# Evaluación

**Caso:** `A-RAG-GRAPH-001@0.1.0`

El fixture reparte personas, aplicaciones, proveedores y fechas. La pregunta exige tres aristas
extraídas para llegar a la congelación que afecta el trabajo de Ana Ruiz.

```powershell
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag search --mode compare "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag-validate
```

Criterios:

- La ruta usada existe en el fixture: Ana Ruiz → AtlasCRM → NortePay → 2026-03-01.
- Cada hop de esa ruta es `extracted` y cita archivo y líneas reales.
- La composición extremo a extremo se muestra como `inferred` y no se guarda en SQLite.
- `02-proyectos.md` participa en la ruta y no es necesario en el top léxico.
- La respuesta cita IDs existentes. El JSONL no guarda pregunta, ruta ni respuesta crudas.
- No hay llamadas a Neo4j, GraphRAG de Microsoft ni a otro laboratorio.

Métricas: hops, nodos visitados, aristas recorridas, fuentes citables, aciertos léxicos, latencia y
tokens. La comparación útil es si la ruta es recuperable, no solo si el texto final “se ve bien”.

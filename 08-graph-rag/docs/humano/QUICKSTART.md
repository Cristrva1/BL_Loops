# Inicio rápido

```powershell
Set-Location .\08-graph-rag          # desde la raíz de BL_Loops
uv sync --locked --all-groups
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag stats
```

El índice se publica con reemplazo atómico: un fallo no deja medio grafo. Las aristas salen de
líneas visibles, no de una inferencia oculta del modelo.

Compara la misma pregunta multi-hop:

```powershell
uv run graph-rag search --mode graph "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag search --mode lexical "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag search --mode compare "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
```

El modo `graph` debe mostrar la ruta:

`Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01`

El modo `lexical` suele devolver personas, proveedores o el calendario, pero no el documento que
acopla AtlasCRM con NortePay. Ese hueco es la lección.

Genera una respuesta con citas:

```powershell
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag-validate
```

Cada hop extraído cita archivo y líneas. La arista compuesta se etiqueta `inferred` y no se guarda
en SQLite.

Siguiente paso: los siete [ejemplos resueltos](EXAMPLES.md), seis de ellos sin Ollama.

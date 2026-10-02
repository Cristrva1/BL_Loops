# 08-graph-rag

RAG de grafo local. Importa Markdown con triples visibles, construye un grafo en SQLite,
recorre rutas de hasta tres saltos y pide a `qwen3.5:4b` en Ollama que responda con citas.
Compara esa ruta con una búsqueda léxica FTS5 sobre los mismos documentos. No usa Neo4j,
Microsoft GraphRAG, embeddings ni otro laboratorio.

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\08-graph-rag
uv sync --locked --all-groups
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag search --mode compare "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag-validate
```

El índice y las corridas viven en `.local/`. El runtime usa Python estándar, SQLite y la API
local `/api/chat` de Ollama.

Organización:

- `src/graph_rag/`: extracción de triples, grafo SQLite, generación y JSONL.
- `fixtures/evaluation-corpus/`: personas, aplicaciones, proveedores, calendario y distractor.
- `contracts/`: contrato de eventos.
- `docs/humano/`: manual didáctico completo.
- `tests/`: pruebas herméticas sin Ollama real.

Empieza en [docs/humano/README.md](docs/humano/README.md).

> Estado: corte vertical CLI de la variante base `SQLite + triples extraídos + multi-hop`.
> Microsoft GraphRAG, CodeGraph, Graphify, Neo4j y dashboard quedan aplazados.

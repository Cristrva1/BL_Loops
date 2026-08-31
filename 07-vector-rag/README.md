# 07-vector-rag

RAG local que compara tres recuperadores sobre el mismo corpus: SQLite FTS5, similitud vectorial
con `qwen3-embedding:latest` y una fusión híbrida RRF. Antes de indexar elimina secciones conocidas
como contaminadas y conserva el estado de confianza de cada fuente.

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\07-vector-rag
uv sync --locked --all-groups
uv run vector-rag index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
uv run vector-rag search --mode hybrid "¿Cómo descubrir la necesidad real sin presionar?"
uv run vector-rag ask "¿Cómo descubrir la necesidad real sin presionar?"
uv run vector-rag-validate
```

El índice, los vectores y las corridas viven en `.local/`. El runtime usa solo Python estándar,
SQLite y las APIs locales `/api/embed` y `/api/chat` de Ollama.

Organización:

- `src/vector_rag/`: filtro de calidad, embeddings, índice híbrido, generación y JSONL.
- `fixtures/evaluation-corpus/`: caso sintético con paráfrasis, obsolescencia y contaminación.
- `contracts/`: contrato de eventos.
- `docs/humano/`: manual didáctico completo.
- `tests/`: pruebas herméticas sin Ollama real.

Empieza en [docs/humano/README.md](docs/humano/README.md).


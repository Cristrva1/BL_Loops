# 06-naive-rag

RAG léxico mínimo y local. Importa archivos Markdown a un índice propio de SQLite FTS5,
recupera fragmentos por palabras y pide a `qwen3.5:4b` en Ollama que responda con citas de
archivo y líneas. No usa embeddings, nube, frameworks RAG ni otro laboratorio.

## Ejecutar

Desde PowerShell:

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\06-naive-rag
uv sync --locked --all-groups
uv run naive-rag index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
uv run naive-rag stats
uv run naive-rag ask "¿Qué explica SPIN Selling sobre la venta consultiva?"
uv run naive-rag-validate
```

La importación solo lee `.md`; los PDF paralelos no se procesan. El índice y las corridas se
guardan en `.local/`, que Git ignora. Después de indexar, consultar no requiere acceso a la
carpeta original.

## Organización

- `src/naive_rag/`: configuración, indexación, recuperación, prompt, Ollama y pipeline.
- `tests/`: pruebas herméticas que no invocan el modelo real.
- `fixtures/evaluation-corpus/`: cinco documentos sintéticos para evaluar versiones y citas.
- `contracts/run-event.schema.json`: forma de cada evento JSONL exportado.
- `examples/questions.txt`: preguntas iniciales para el corpus de libros.
- `docs/humano/`: tutorial, arquitectura, ejercicios, diagnóstico y evaluación.
- `.local/data/`: índice SQLite generado; no se versiona.
- `.local/runs/`: trazas sanitizadas; no guardan pregunta, contexto ni respuesta crudos.

Empieza en [docs/humano/README.md](docs/humano/README.md) y continúa con el
[inicio rápido](docs/humano/QUICKSTART.md).

> Estado: corte vertical CLI funcional de la variante base `SQLite FTS5 + Ollama + citas`.
> Embeddings, PDF/OCR, reranking, conversación, API web y dashboard quedan aplazados.


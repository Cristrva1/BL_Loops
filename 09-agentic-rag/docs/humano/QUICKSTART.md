# Quickstart explicado

Todos los comandos se ejecutan en PowerShell. No copies `.env` reales ni imprimas secretos.

## 1. Entrar y crear el entorno aislado

```powershell
cd C:\Users\criss\Desktop\Claude\BL_Loops\09-agentic-rag
uv sync
```

Resultado esperado: `.venv` y `uv.lock` pertenecen únicamente a este laboratorio.

## 2. Confirmar modelos locales

```powershell
ollama list
```

Deben aparecer `qwen3.5:4b` y `qwen3-embedding:latest`. El laboratorio no descarga modelos
ni usa APIs pagadas como fallback.

## 3. Construir el índice privado

```powershell
uv run sales-agent index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
```

Resultado observado el 30 de agosto de 2026: 49 Markdown descubiertos, 24 con contenido
sustantivo indexable, 594 vectores, 134 secciones excluidas y 20 fuentes marcadas como no
revisadas. Estas cifras son una instantánea y cambiarán si cambia el corpus.

La base publicada queda en `.local/data/sales-library.sqlite3`. El reemplazo ocurre solo
después de terminar todos los embeddings.

## 4. Ejecutar un turno

```powershell
uv run sales-agent ask "Soy asesor inmobiliario. ¿Cómo vendo sin presionar y construyo una relación duradera?"
```

Resultado esperado:

```text
[1/4 decidir] model_tool_call
[2/4 herramienta] search_sales_library -> ... fuentes
[3/4 evidencia] ... fragmentos no confiables delimitados
[4/4 responder] done
```

La respuesta debe citar `[S1]` y listar rutas y líneas. `runtime_fallback` también es válido:
significa que el modelo no emitió una llamada aceptable y el runtime buscó la pregunta original.

## 5. Conversar con memoria volátil

```powershell
uv run sales-agent chat
```

Comandos internos:

- `/estado`: cuenta mensajes conservados en RAM.
- `/limpiar`: elimina la memoria de la sesión.
- `/salir`: termina el proceso y descarta la memoria.

Cada turno vuelve a consultar la biblioteca una sola vez. La memoria no sustituye las fuentes.

## 6. Validar la corrida y el código

```powershell
uv run sales-agent-validate
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Resultado esperado: JSONL válido, pruebas verdes y cero errores de lint/formato.


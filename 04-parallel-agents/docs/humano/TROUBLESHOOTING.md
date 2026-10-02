# Diagnóstico de fallos

## `No se pudo conectar con Ollama local`

**Causa probable:** Ollama no está iniciado o no escucha en `127.0.0.1:11434`.

```powershell
ollama list
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:11434/api/tags"
```

Inicia la aplicación de Ollama o, si tu instalación lo requiere, `ollama serve`.

## `Ollama no encontró el modelo 'qwen3.5:4b'`

```powershell
ollama list
```

Si no aparece y autorizas la descarga:

```powershell
ollama pull qwen3.5:4b
```

Puedes cambiar el modelo en el `.env` local con `PARALLEL_MODEL`, siempre que el tag no sea cloud.

## Timeout de una rama

El límite predeterminado es 180 segundos por rama. Si una fuente hace timeout, las otras pueden completar. Sube `PARALLEL_BRANCH_TIMEOUT_SECONDS` solo si tú decides que es seguro. El máximo es 1800. No hay retry automático.

## El paralelo no es más rápido que el secuencial

Es un resultado didáctico, no un fallo del grafo. Un único modelo en Ollama puede serializar las tres peticiones. Mira `overlap_observed` y `max_in_flight`. Con `PARALLEL_MAX_IN_FLIGHT=1` el overlap debe desaparecer.

## `OLLAMA_BASE_URL debe ser HTTP local`

Usa únicamente:

```text
http://127.0.0.1:11434
http://localhost:11434
http://[::1]:11434
```

HTTPS, credenciales embebidas y hosts remotos se rechazan.

## El frontend dice que el backend no está en 8014

Arranca Uvicorn en `127.0.0.1:8014` antes de Vite. El proxy de Vite solo reenvía `/api`. No abras el frontend contra otro puerto. El 5174 ya lo usa otro laboratorio; este usa `5175`.

## El grafo no se mueve

Confirma que la corrida existe con `GET /api/v1/runs/<run_id>`. Si el snapshot avanza y el grafo no, recarga la página: el estado vivo está en memoria y no sobrevive a un reinicio del API.

## Una rama falla y las otras no

Es el comportamiento correcto. Lee `failed_sources` y el evento `node.failed` de esa fuente. La tabla no debe incluir sus filas.

## El JSONL no valida

```powershell
uv run parallel-agents-validate
```

Debe empezar en `run.started` y terminar en `run.completed` o `run.failed`, con `lab_id=04-parallel-agents` y secuencia consecutiva. Si el archivo está a medias, la corrida todavía corre. Tampoco puede contener el texto de los documentos fuente.

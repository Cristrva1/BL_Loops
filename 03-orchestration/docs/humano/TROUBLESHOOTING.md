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

Puedes cambiar el modelo en el `.env` local con `ORCH_MODEL`, siempre que el tag no sea cloud.

## Timeout

Tres o cuatro llamadas secuenciales pueden superar un minuto en frío. El límite predeterminado es 180 segundos por llamada. No hay retry automático. Sube `ORCH_TIMEOUT_SECONDS` solo si tú decides que es seguro. El máximo es 1800.

## `OLLAMA_BASE_URL debe ser HTTP local`

Usa únicamente:

```text
http://127.0.0.1:11434
http://localhost:11434
http://[::1]:11434
```

HTTPS, credenciales embebidas y hosts remotos se rechazan.

## El frontend dice que el backend no está en 8012

Arranca Uvicorn en `127.0.0.1:8012` antes de Vite. El proxy de Vite solo reenvía `/api`. No abras el frontend contra otro puerto.

## El grafo no se mueve

Confirma que la corrida existe con `GET /api/v1/runs/<run_id>`. Si el snapshot avanza y el grafo no, recarga la página: el estado vivo está en memoria y no sobrevive a un reinicio del API.

## La orquestada falla y la línea base no

Es un resultado didáctico. Un Plan JSON inválido tumba solo esa rama. Lee `orchestrated.preview` y el evento `node.failed` del planificador.

## El JSONL no valida

```powershell
uv run orchestration-validate
```

Debe empezar en `run.started` y terminar en `run.completed` o `run.failed`, con `lab_id=03-orchestration` y secuencia consecutiva. Si el archivo está a medias, la corrida todavía corre.

## El revisor LLM dice que sí y el gate dice que no

No es un bug. El laboratorio enseña esa discrepancia. El ganador usa el gate determinista.

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

Puedes cambiar el modelo en el `.env` local con `LOOP_MODEL`, siempre que el tag no sea cloud.

## Timeout del loop

El presupuesto del caso es de 180 segundos para **toda** la corrida. Cada llamada a Ollama tiene además `LOOP_TIMEOUT_SECONDS` (60 por defecto). Si el modelo está en frío, la primera iteración puede consumir buena parte del presupuesto. No hay retry automático.

## `OLLAMA_BASE_URL debe ser HTTP local`

Usa únicamente:

```text
http://127.0.0.1:11434
http://localhost:11434
http://[::1]:11434
```

HTTPS, credenciales embebidas y hosts remotos se rechazan.

## El frontend dice que el backend no está en 8015

Arranca Uvicorn en `127.0.0.1:8015` antes de Vite. El proxy de Vite solo reenvía `/api`. No abras el frontend contra otro puerto. El 5175 ya lo usa otro laboratorio; este usa `5176`.

## El grafo no se mueve

Confirma que la corrida existe con `GET /api/v1/runs/<run_id>`. Si el snapshot avanza y el grafo no, recarga la página: el estado vivo está en memoria y no sobrevive a un reinicio del API.

## El loop para en `max_errors`

Dos fallos de Ollama o dos reescrituras inválidas cierran el ciclo. Lee `stop_reason` y el evento `node.failed`. No es un reintento infinito.

## El JSONL no valida

```powershell
uv run agent-loops-validate
```

Debe empezar en `run.started` y terminar en `run.completed` o `run.failed`, con `lab_id=05-agent-loops` y secuencia consecutiva. Si el archivo está a medias, la corrida todavía corre.

## El mejor score no es el de la última iteración

No es un bug. El laboratorio enseña a conservar el máximo. Mira `is_best` en cada `iteration.recorded`.

## `agent-loops-score` no encuentra archivos con `*`

PowerShell no expande comodines para programas nativos; el comando los expande él mismo si el patrón
va entre comillas: `uv run agent-loops-score ".\.local\artifacts\*\best-output.txt"`.

## El panel final aparecía vacío al terminar una corrida

Era una carrera corregida el 2026-11-05: el evento `run.completed` marcaba la corrida como terminada
antes de guardar las iteraciones y el mejor candidato. Ahora los eventos terminales se publican junto
con el resultado y el stream SSE lee eventos y snapshot bajo el mismo candado
(`test_terminal_event_is_published_together_with_the_final_result`).

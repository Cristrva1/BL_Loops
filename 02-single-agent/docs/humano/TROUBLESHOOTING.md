# Diagnóstico de fallos

## `No se pudo conectar con Ollama local`

**Causa probable:** Ollama no está iniciado o no escucha en `127.0.0.1:11434`.

**Comprobación:**

```powershell
ollama list
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:11434/api/tags"
```

Inicia la aplicación de Ollama o, si tu instalación lo requiere, ejecuta `ollama serve` en otra terminal.

## `Ollama no encontró el modelo 'gemma4:e4b'`

Comprueba el nombre exacto:

```powershell
ollama list
```

Si no aparece y autorizas la descarga de sus pesos:

```powershell
ollama pull gemma4:e4b
```

## Timeout

La primera respuesta puede incluir la carga de los pesos y tardar más. El límite predeterminado es 300 segundos. No hay retry automático. Comprueba carga de CPU/GPU y vuelve a enviar solo si tú decides que es seguro.

Para un equipo más lento puedes definir, como variable de proceso o en el `.env` local:

```text
SIMPLE_AGENT_TIMEOUT_SECONDS=600
```

El máximo admitido es 1800 segundos.

## `OLLAMA_BASE_URL debe ser HTTP local`

Es una protección deliberada. Usa una de estas formas:

```text
http://127.0.0.1:11434
http://localhost:11434
http://[::1]:11434
```

Endpoints remotos, HTTPS, credenciales embebidas y rutas adicionales se rechazan. No existe fallback cloud.

## El agente olvidó algo después de reiniciar

Es el comportamiento esperado. El historial solo vive en RAM durante la sesión actual. Este corte no implementa memoria persistente.

## La respuesta no es siempre igual

El modelo genera texto de forma probabilística. Evalúa congruencia y cumplimiento, no identidad literal. Los parámetros usados quedan registrados en el JSONL.

## El JSONL no valida

Ejecuta:

```powershell
uv run single-agent-validate .\.local\runs\archivo.jsonl
```

El importador informa si falta un campo, se rompe la secuencia o no existe evento terminal. Una sesión cerrada abruptamente por terminar el proceso desde fuera podría dejar una traza incompleta; consérvala como evidencia del fallo.

## Caracteres españoles incorrectos

La CLI configura su salida como UTF-8 para admitir acentos y emojis, incluso al canalizar entrada desde PowerShell. Usa Windows Terminal o PowerShell 7 y ejecuta Python mediante `uv run`. Los archivos del proyecto y el JSONL también se escriben en UTF-8.

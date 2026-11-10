# Ejemplos resueltos · Agente único

> Seis recorridos con su salida. Los ejemplos 1, 4, 5 y 6 se obtuvieron **con Ollama apagado** y son
> exactamente reproducibles. Los ejemplos 2 y 3 dependen del modelo: se muestra la parte determinista
> (lo que hace el programa) y la forma esperada de la respuesta, no un texto inventado.
> Ejecuta todo desde `02-single-agent`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Comandos locales | Lo que el programa hace sin llamar al modelo |
| 2 | Recordar un dato | La memoria es el historial reenviado |
| 3 | Olvidar a propósito | Sin historial, no hay memoria |
| 4 | Leer la traza | Qué se registra y qué nunca se registra |
| 5 | Ollama apagado | Fallo visible, sin reintento ni fallback cloud |
| 6 | Configuración insegura | El programa se niega a arrancar |

---

## Ejemplo 1 · Comandos locales sin modelo

```powershell
uv run single-agent
```

```text
Tu > /ayuda
Comandos locales (nunca se envían al modelo):
  /ayuda    muestra esta lista
  /memoria  cuenta los mensajes y caracteres que se reenviarán en el próximo turno
  /olvidar  vacía el historial y conserva solo la instrucción de sistema
  /salir    termina la sesión y cierra la traza JSONL

Tu > /memoria
Memoria > 1 mensaje en RAM: 1 de sistema y 0 de conversación (0 turnos completos).
Memoria > En el próximo turno se reenviarán 292 caracteres más tu nuevo mensaje.
Memoria > Tokens de entrada del último turno según Ollama: sin dato todavía.
```

**Qué observar:** antes de escribir nada ya hay un mensaje en memoria: la **instrucción de sistema**
(292 caracteres). Esa instrucción viaja en *todas* las llamadas. Los comandos locales no generan
eventos en la traza porque no ocurre nada con el modelo.

## Ejemplo 2 · El modelo «recuerda» porque recibe todo de nuevo

```text
Tu > Recuerda que mi color de prueba es verde.
Agente > (confirma que lo recordará)
Tu > /memoria
Memoria > 3 mensajes en RAM: 1 de sistema y 2 de conversación (1 turno completo).
Memoria > En el próximo turno se reenviarán N caracteres más tu nuevo mensaje.
Memoria > Tokens de entrada del último turno según Ollama: T.
Tu > ¿Cuál es mi color de prueba?
Agente > (responde «verde»)
```

`N` y `T` dependen de la longitud de la respuesta del modelo. Lo determinista es la estructura:

```text
turno 1 → se envían [system, user-1]
turno 2 → se envían [system, user-1, assistant-1, user-2]
```

**Por qué ocurre:** el modelo no tiene memoria propia entre llamadas. El programa guarda la lista y
la reenvía completa. Ejecuta `/memoria` después de cada turno: los caracteres crecen siempre, y los
tokens de entrada (`T`) crecen con ellos. Por eso una conversación larga es cada vez más lenta.

## Ejemplo 3 · Olvidar a propósito

```text
Tu > Recuerda que mi animal de prueba es el ajolote.
Agente > (confirma)
Tu > /olvidar
Memoria > Historial vaciado. El modelo ya no recibirá los turnos anteriores.
Tu > ¿Cuál es mi animal de prueba?
Agente > (dice que no lo sabe o pide que se lo indiques)
```

**Qué observar:** la siguiente llamada solo contiene `[system, user]`. Una prueba automática lo
verifica (`test_forget_command_resets_the_history_sent_to_the_model`). Si el modelo «adivina» el
ajolote, sería una coincidencia: no recibió ese dato.

## Ejemplo 4 · Leer la traza de una sesión

Con Ollama apagado se envió un mensaje y después `/salir`. La traza tiene siete eventos:

```powershell
uv run single-agent-validate
```

```text
JSONL valido: 7 eventos, terminal=run.completed, run_id=run-e99a34fc-caa9-4634-b6f7-a273467eceea
```

Contenido resumido (secuencia, tipo, estado del nodo, payload, métricas):

```text
1 run.started      -        {"interface": "windows-cli", "conversation_memory": "session_only", "raw_conversation_stored": false}
2 node.queued      queued   {"turn": 1, "input_chars": 41}
3 node.started     running  {"turn": 1}
4 model.requested  waiting  {"turn": 1, "history_messages": 2}
5 error.raised     failed   {"turn": 1, "error_type": "OllamaError"}   {"wall_duration_ms": 1.807}
6 node.failed      failed   {"turn": 1}
7 run.completed    -        {"status": "completed", "turns": 0, "reason": "user_exit", "raw_conversation_stored": false}
```

**Qué observar:**

- `input_chars: 41` es la **longitud** de «Recuerda que mi color de prueba es verde.»; la palabra
  «verde» no aparece en ningún lugar del archivo.
- `history_messages: 2` confirma que se enviaron sistema + mensaje del usuario.
- La sesión termina `completed` aunque un turno falló: el chat siguió disponible y el humano salió.
  `turns: 0` indica que ningún turno llegó a completarse.

## Ejemplo 5 · Ollama apagado

```text
Tu > Hola
[procesando] humano -> Ollama -> agente
Error > No se pudo conectar con Ollama local. Comprueba que Ollama este iniciado.

Tu >
```

**Qué observar:** no hay reintento automático (un timeout podría haber empezado trabajo en el
servidor) y no aparece ningún proveedor alternativo. El chat sigue abierto para que decidas.

## Ejemplo 6 · Configuración insegura rechazada

```powershell
$env:OLLAMA_BASE_URL = "http://example.com:11434"
uv run single-agent
Remove-Item Env:OLLAMA_BASE_URL
```

```text
Configuracion invalida: OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434.
```

```powershell
$env:SIMPLE_AGENT_MODEL = "gpt-oss:120b-cloud"
uv run single-agent
Remove-Item Env:SIMPLE_AGENT_MODEL
```

```text
Configuracion invalida: SIMPLE_AGENT_MODEL debe referirse a un modelo local, no cloud.
```

**Qué observar:** el programa termina con código `2` **antes** de enviar nada. Las variables del
proceso ganan al `.env`, por eso basta con `$env:` para probarlo; `Remove-Item` deja la sesión limpia.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

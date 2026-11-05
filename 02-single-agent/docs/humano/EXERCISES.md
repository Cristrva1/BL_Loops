# Ejercicios

Antes de comenzar, ejecuta `uv run single-agent` desde la raíz del laboratorio. Cada ejercicio
tiene una solución plegada: intenta primero. Los recorridos completos están en
[EXAMPLES.md](EXAMPLES.md).

## Básico — pregunta y respuesta

1. Escribe: `Explícame en dos frases qué es un modelo de lenguaje.`
2. Comprueba que la respuesta sea legible y relacionada con la pregunta.
3. Sal con `/salir`.

**Resultado esperado:** una respuesta final congruente; no aparecen JSON, etiquetas de pensamiento
ni llamadas a herramientas.

<details>
<summary>Qué comprobar</summary>

La respuesta debe ser texto normal. Si ves bloques `<think>` o JSON, algo cambió en el cliente: el
laboratorio envía `think: false` y solo imprime `message.content`. Al salir, la última línea indica
la ruta de la traza en `.local/runs/`.
</details>

## Intermedio 1 — contexto entre turnos

1. Escribe: `Mi animal de prueba es el ajolote.`
2. Pregunta: `¿Cuál es mi animal de prueba y en qué turno te lo dije?`
3. Haz otra pregunta sobre el mismo animal sin repetir su nombre.

**Resultado esperado:** el modelo usa mensajes anteriores porque el programa reenvía el historial
completo de la sesión.

**Reflexión:** cierra y vuelve a abrir el chat. Pregunta otra vez por el animal. Debe quedar claro
que la memoria era temporal.

<details>
<summary>Solución</summary>

En el segundo turno el modelo recibe `[system, user-1, assistant-1, user-2]`, así que puede decir
«ajolote» y «en el primer turno». Al reiniciar, el nuevo proceso empieza solo con `[system]`: el
modelo no puede saberlo. Nada se guardó en disco; la traza JSONL solo tiene longitudes y tiempos.
</details>

## Intermedio 2 — medir cómo crece el contexto

1. Ejecuta `/memoria` y anota los caracteres.
2. Haz tres preguntas cortas y ejecuta `/memoria` después de cada una.
3. Ejecuta `/olvidar` y otra vez `/memoria`.

**Resultado esperado:** una tabla de cuatro filas donde los caracteres y los tokens de entrada
crecen; tras `/olvidar` vuelven al valor inicial.

<details>
<summary>Solución</summary>

| Momento | Mensajes en RAM | Caracteres | Tokens de entrada |
|---|---|---|---|
| Inicio | 1 | 292 (solo sistema) | sin dato |
| Tras turno 1 | 3 | 292 + pregunta + respuesta | `T1` |
| Tras turno 2 | 5 | lo anterior + nuevo par | `T2 > T1` |
| Tras turno 3 | 7 | lo anterior + nuevo par | `T3 > T2` |
| Tras `/olvidar` | 1 | 292 | sin dato |

El crecimiento depende de lo largo que responda el modelo. La lección: cada turno cuesta más que el
anterior porque se reenvía todo. Las memorias persistentes o resumidas existen para controlar ese
costo; este laboratorio todavía no las implementa.
</details>

## Avanzado — experimento observable

1. Inicia una sesión y formula la misma pregunta corta dos veces.
2. Termina con `/salir`.
3. Ejecuta `uv run single-agent-validate`.
4. Abre el JSONL más reciente y localiza los eventos `model.completed`.
5. Compara `wall_duration_ms`, `ollama_duration_ms`, `prompt_tokens` y `output_tokens`.

**Resultado esperado:** hay dos rutas completas de nodo y un evento terminal. La primera llamada
puede incluir carga del modelo y tardar más; no se exige que las respuestas sean idénticas.

<details>
<summary>Cómo leer el resultado</summary>

Puedes listar los eventos sin abrir un editor:

```powershell
$run = Get-ChildItem .local\runs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $run | ConvertFrom-Json | Where-Object event_type -eq "model.completed" |
    ForEach-Object { $_.metrics }
```

- El primer `wall_duration_ms` suele ser mucho mayor: incluye cargar los pesos en memoria.
- El segundo `prompt_tokens` es mayor que el primero: incluye la primera pregunta y su respuesta.
- `wall_duration_ms` siempre es algo mayor que `ollama_duration_ms`, porque suma el viaje HTTP.
</details>

## Fallo didáctico A — Ollama detenido

Con Ollama cerrado, intenta un mensaje. La CLI debe mostrar un diagnóstico de conexión, registrar
`error.raised` y seguir disponible. No debe cambiar a cloud.

<details>
<summary>Salida esperada</summary>

`Error > No se pudo conectar con Ollama local. Comprueba que Ollama este iniciado.` La traza contiene
`error.raised` con `error_type: OllamaError` y después `node.failed`. El
[ejemplo 4](EXAMPLES.md#ejemplo-4--leer-la-traza-de-una-sesión) muestra los siete eventos.
</details>

## Fallo didáctico B — modelo inexistente

Usa temporalmente una variable de proceso:

```powershell
$env:SIMPLE_AGENT_MODEL = "modelo-inexistente"
uv run single-agent
Remove-Item Env:SIMPLE_AGENT_MODEL
```

La CLI debe indicar que compruebes `ollama list`. Una variable de proceso no toca tu `.env`.

<details>
<summary>Por qué así y no editando el `.env`</summary>

Las variables del proceso tienen prioridad máxima y desaparecen al cerrar la terminal o con
`Remove-Item`. Editar el `.env` compartido podría afectar a otros laboratorios y es fácil olvidar
restaurarlo.
</details>

Nunca uses información personal o secreta en estos ejercicios; los datos sintéticos bastan para
evaluar memoria conversacional.

## Autoevaluación

<details>
<summary>1. ¿Por qué el agente no reintenta solo cuando hay un timeout?</summary>

Porque Ollama pudo haber empezado a procesar. Repetir a ciegas duplicaría trabajo y ocultaría el
fallo. El laboratorio informa y deja que la persona decida.
</details>

<details>
<summary>2. ¿Qué contiene el primer mensaje de cada llamada?</summary>

La instrucción de sistema: reglas de claridad, idioma y continuidad que valen para toda la sesión.
</details>

<details>
<summary>3. ¿Por qué los comandos locales no aparecen en la traza?</summary>

Porque la traza describe la ruta humano → Ollama → respuesta. `/memoria` o `/olvidar` no llaman al
modelo; su efecto se observa en el siguiente `model.requested` (`history_messages`).
</details>

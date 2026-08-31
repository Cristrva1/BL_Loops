# Ejercicios

Antes de comenzar, ejecuta `uv run single-agent` desde la raíz del laboratorio.

## Básico — pregunta y respuesta

1. Escribe: `Explícame en dos frases qué es un modelo de lenguaje.`
2. Comprueba que la respuesta sea legible y relacionada con la pregunta.
3. Sal con `/salir`.

**Resultado esperado:** una respuesta final congruente; no aparecen JSON, etiquetas de pensamiento ni llamadas a herramientas.

## Intermedio — contexto entre turnos

1. Escribe: `Mi animal de prueba es el ajolote.`
2. Pregunta: `¿Cuál es mi animal de prueba y en qué turno te lo dije?`
3. Haz otra pregunta sobre el mismo animal sin repetir su nombre.

**Resultado esperado:** el modelo usa mensajes anteriores porque el programa reenvía el historial completo de la sesión.

**Reflexión:** cierra y vuelve a abrir el chat. Pregunta otra vez por el animal. Debe quedar claro que la memoria era temporal.

## Avanzado — experimento observable

1. Inicia una sesión y formula la misma pregunta corta dos veces.
2. Termina con `/salir`.
3. Ejecuta `uv run single-agent-validate`.
4. Abre el JSONL más reciente solo con datos sintéticos y localiza los eventos `model.completed`.
5. Compara `wall_duration_ms`, `ollama_duration_ms`, `prompt_tokens` y `output_tokens`.

**Resultado esperado:** hay dos rutas completas de nodo y un evento terminal. La primera llamada puede incluir carga del modelo y tardar más; no se exige que las respuestas sean idénticas.

## Fallo didáctico A — Ollama detenido

Con Ollama cerrado, intenta un mensaje. La CLI debe mostrar un diagnóstico de conexión, registrar `error.raised` y seguir disponible. No debe cambiar a cloud.

## Fallo didáctico B — modelo inexistente

En una copia local de `.env`, usa temporalmente `SIMPLE_AGENT_MODEL=modelo-inexistente`. La CLI debe indicar que compruebes `ollama list`. Restaura `gemma4:e4b` al terminar.

Nunca uses información personal o secreta en estos ejercicios; los fixtures sintéticos bastan para evaluar memoria conversacional.

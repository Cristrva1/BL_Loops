# Ejercicios

Antes de comenzar, deja el backend en `8015` y el frontend en `5176`, o usa `uv run agent-loops-demo`.

## Básico — una corrida guiada

1. Pulsa **Cargar caso I-LOOP-003**.
2. Deja el prompt inicial débil.
3. Lanza el loop y espera el evento terminal.
4. Anota score inicial, mejor score, número de iteraciones y motivo de salida.

**Resultado esperado:** el grafo termina con un `stop_reason` visible. El JSONL aparece como ruta relativa. El prompt completo no se pega en la bitácora.

## Intermedio — prompt ya bueno

1. Sustituye el prompt inicial por uno que pida explícitamente JSON con `title`, `steps`, `limits` (Ollama local) y `stop_condition` con `/salir`.
2. Lanza de nuevo la misma tarea.
3. Compara el número de llamadas con la corrida débil.

**Resultado esperado:** una sola iteración y `threshold_reached`. El nodo *Mejorar prompt* permanece inactivo o se salta.

**Reflexión:** ¿el loop sigue siendo útil cuando el prompt ya cumple el contrato?

## Avanzado — experimento observable

1. Ejecuta tres corridas con el prompt débil.
2. Valida cada JSONL con `uv run agent-loops-validate`.
3. Compara `prompt_tokens`, `output_tokens` y el número de eventos `iteration.recorded`.
4. Mira si alguna corrida conservó un mejor candidato distinto del último.

**Resultado esperado:** las tres trazas terminan y se reimportan. Más vueltas implican más tokens. Eso no implica peor calidad: implica más trabajo hasta el umbral o el presupuesto.

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un loop. Los nodos *Generar* o *Mejorar* deben pasar a `failed`. Al segundo error el loop para con `max_errors`. No debe aparecer un proveedor cloud.

## Fallo didáctico B — reescritura inválida

En las pruebas, `test_invalid_rewrite_counts_as_error_and_jsonl_is_sanitized` simula un mejorador que no devuelve JSON. El prompt anterior se conserva y el error cuenta para el presupuesto.

Nunca uses datos personales en la tarea. El fixture sintético basta.

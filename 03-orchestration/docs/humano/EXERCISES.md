# Ejercicios

Antes de comenzar, deja el backend en `8012` y el frontend en `5172`, o usa `uv run orchestration-demo`.

## Básico — una corrida guiada

1. Pulsa **Cargar caso I-ORCH-001**.
2. Deja marcadas las dos variantes.
3. Lanza el experimento y espera el evento terminal.
4. Anota cuántos checks aprueba cada variante y si *Corrección* se activó.

**Resultado esperado:** el grafo termina en *Comparación*. El JSONL aparece como ruta relativa. El Markdown completo no se pega en la bitácora.

## Intermedio — quitar la línea base

1. Desmarca **Agente único**.
2. Lanza de nuevo la misma tarea.
3. Lee el texto del ganador.

**Resultado esperado:** `winner=incomplete` o una nota de que falta la línea base. El laboratorio se niega a celebrar la orquestación sin contraste.

**Reflexión:** ¿qué afirmación ya no puedes hacer?

## Avanzado — experimento observable

1. Ejecuta tres corridas con la misma entrada.
2. Valida cada JSONL con `uv run orchestration-validate`.
3. Compara `prompt_tokens`, `output_tokens` y `wall_duration_ms` de `model.completed`.
4. Mira si el revisor LLM y el gate determinista discreparon (`llm_review_available` frente a `passed`).

**Resultado esperado:** las tres trazas terminan y se reimportan. La orquestada suele emitir más eventos y más tokens que el agente único. Eso no implica peor calidad: implica más trabajo.

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un experimento. El nodo activo debe pasar a `failed` con un diagnóstico de conexión. No debe aparecer un proveedor cloud.

## Fallo didáctico B — plan inválido

En las pruebas, `test_invalid_plan_fails_only_the_orchestrated_variant` simula un planificador que no devuelve JSON. La línea base sigue puntuable. Reproduce la idea en el dashboard solo si alteras un doble; no hace falta romper Ollama.

Nunca uses datos personales en la tarea. El fixture sintético basta.

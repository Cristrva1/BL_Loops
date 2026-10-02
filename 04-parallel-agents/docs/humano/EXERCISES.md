# Ejercicios

Antes de comenzar, deja el backend en `8014` y el frontend en `5175`, o usa `uv run parallel-agents-demo`.

## Básico — una corrida guiada

1. Pulsa **Cargar caso I-PARALLEL-002**.
2. Deja marcadas las dos variantes.
3. Lanza el experimento y espera el evento terminal.
4. Anota `wall_ms` de cada variante y si *Paralelo A/B/C* coincidieron en `running` o `waiting`.

**Resultado esperado:** el grafo termina en *Comparación*. El JSONL aparece como ruta relativa. Los documentos completos no se pegan en la bitácora.

## Intermedio — tope de concurrencia

1. En el `.env` local, pon `PARALLEL_MAX_IN_FLIGHT=1`.
2. Reinicia Uvicorn y lanza el mismo caso solo con la variante paralela.
3. Mira `overlap_observed` y el tiempo de pared.

**Resultado esperado:** `overlap_observed=false`. El “paralelo” se comporta como una cola. El laboratorio enseña el tope, no lo esconde.

**Reflexión:** ¿qué afirma entonces un dashboard que dibuja tres nodos en ámbar si el motor solo atiende uno?

## Avanzado — experimento observable

1. Ejecuta tres corridas con la misma entrada y `PARALLEL_MAX_IN_FLIGHT=3`.
2. Valida cada JSONL con `uv run parallel-agents-validate`.
3. Compara `speedup`, `prompt_tokens` y si Ollama serializó las llamadas.
4. Confirma que cada fila de la tabla tiene `source_id`.

**Resultado esperado:** las tres trazas terminan y se reimportan. Un speedup menor que 3 no es un bug: un modelo compartido puede atender en serie.

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un experimento. Las ramas activas deben pasar a `failed` con un diagnóstico de conexión. No debe aparecer un proveedor cloud.

## Fallo didáctico B — una rama inválida

La prueba `test_failed_branch_is_not_presented_as_complete` simula un extractor que no devuelve JSON. Las otras dos fuentes siguen en la tabla. La fallida queda en `failed_sources`.

Nunca uses datos personales en la tarea. El fixture sintético basta.

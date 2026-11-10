# Ejercicios

Antes de comenzar, deja el backend en `8014` y el frontend en `5175`, o usa
`uv run parallel-agents-demo`. Los ejercicios marcados **sin Ollama** se resuelven con los fragmentos
de [EXAMPLES.md](EXAMPLES.md). Cada uno tiene una solución plegada.

## Básico 1 — una corrida guiada

1. Pulsa **Cargar caso I-PARALLEL-002**.
2. Deja marcadas las dos variantes.
3. Lanza el experimento y espera el evento terminal.
4. Anota `wall_ms` de cada variante y si *Paralelo A/B/C* coincidieron en `running` o `waiting`.

**Resultado esperado:** el grafo termina en *Comparación*. El JSONL aparece como ruta relativa. Los
documentos completos no se pegan en la bitácora.

<details>
<summary>Cómo interpretarlo</summary>

Divide `wall_ms` secuencial entre `wall_ms` paralelo: ese es el speedup que muestra el panel. Si las
tres ramas estuvieron en `running` a la vez y el speedup se acerca a 3, hubo paralelismo real. Si las
ramas se encendieron una detrás de otra, Ollama serializó las llamadas aunque el código las lanzara
juntas.
</details>

## Básico 2 — encontrar el error de procedencia (sin Ollama)

Un extractor devolvió para la fuente B:

```json
{"source_id": "source-b", "facts": [
  {"fact_id": "apertura_semana", "topic": "horario", "value": "09:00", "evidence": "De lunes a viernes apertura_semana 09:00"},
  {"fact_id": "cierre_semana", "topic": "horario", "value": "14:00", "evidence": "cierra a las 14:00"}
]}
```

¿Aprueba `score_bundle()`? ¿Qué error cometió el modelo?

<details>
<summary>Solución</summary>

No aprueba: devuelve `(False, ['cierre_semana!=18'])`. La apertura es correcta, pero el cierre de
14:00 es el del **sábado**; el de lunes a viernes es 18:00. La evidencia citada («cierra a las 14:00»)
es real, pero pertenece a otra frase del mismo documento. Citar texto existente no basta: hay que
citar el texto que **sostiene** el hecho pedido.
</details>

## Intermedio 1 — tope de concurrencia

1. Define la variable de proceso `PARALLEL_MAX_IN_FLIGHT=1` (o ponla en un `.env` local).
2. Reinicia Uvicorn y lanza el mismo caso solo con la variante paralela.
3. Mira `overlap_observed` y el tiempo de pared.

**Resultado esperado:** `overlap_observed=false`. El “paralelo” se comporta como una cola. El
laboratorio enseña el tope, no lo esconde.

**Reflexión:** ¿qué afirma entonces un dashboard que dibuja tres nodos en ámbar si el motor solo
atiende uno?

<details>
<summary>Solución</summary>

Afirma algo falso si solo mira el dibujo. Por eso el laboratorio mide `overlap_peak` (el máximo de
llamadas simultáneas observadas) y deriva `overlap_observed = peak >= 2`. La lección general de
BL_Loops: una visualización solo es verdad si sale de eventos medidos.
</details>

## Intermedio 2 — predecir el speedup (sin Ollama)

Cada rama tarda, por separado: A = 2 s, B = 5 s, C = 2 s. Calcula el tiempo de pared y el speedup
para `max_in_flight = 3`, `2` y `1`, suponiendo que Ollama atiende de verdad tantas llamadas como el
tope permite.

<details>
<summary>Solución</summary>

| `max_in_flight` | Paralelo | Secuencial | Speedup |
|---|---|---|---|
| 3 | 5 s (la rama más lenta) | 9 s | 1.8 |
| 2 | 5 s (A y B empiezan; C entra cuando A termina, en el segundo 2, y acaba en el 4) | 9 s | 1.8 |
| 1 | 9 s | 9 s | 1.0 |

El límite del paralelismo es la rama más lenta (B). Con ramas desequilibradas, añadir concurrencia
deja de ayudar muy pronto.
</details>

## Avanzado — experimento observable

1. Ejecuta tres corridas con la misma entrada y `PARALLEL_MAX_IN_FLIGHT=3`.
2. Valida cada JSONL con `uv run parallel-agents-validate`.
3. Compara `speedup`, `prompt_tokens` y si Ollama serializó las llamadas.
4. Confirma que cada fila de la tabla tiene `source_id`.

**Resultado esperado:** las tres trazas terminan y se reimportan. Un speedup menor que 3 no es un
bug: un modelo compartido puede atender en serie.

<details>
<summary>Qué concluir</summary>

Los tokens totales son casi iguales en ambas variantes: el paralelismo no ahorra trabajo, solo
reorganiza **cuándo** se hace. Si el speedup varía mucho entre corridas, tu equipo está limitado por
la GPU o por la configuración de Ollama (`OLLAMA_NUM_PARALLEL`), no por el código del laboratorio.
</details>

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un experimento. Las ramas activas deben pasar a `failed` con un diagnóstico de
conexión. No debe aparecer un proveedor cloud.

## Fallo didáctico B — una rama inválida

La prueba `test_failed_branch_is_not_presented_as_complete` simula un extractor que no devuelve JSON.
Las otras dos fuentes siguen en la tabla. La fallida queda en `failed_sources`. El
[ejemplo 3](EXAMPLES.md#ejemplo-3--unir-con-una-rama-caída) muestra la misma unión con un timeout.

Nunca uses datos personales en la tarea. El fixture sintético basta.

## Autoevaluación

<details>
<summary>1. ¿Qué condición debe cumplir una tarea para paralelizarla así?</summary>

Que sus ramas sean independientes: ninguna necesita el resultado de otra. Si B dependiera de A, sería
una orquestación secuencial como la del laboratorio 03.
</details>

<details>
<summary>2. ¿Por qué el agregador no completa una rama fallida con «lo más probable»?</summary>

Porque fabricaría un hecho sin fuente. Un hueco visible (`failed_sources`) es información útil; un
dato inventado contamina todo lo que venga después.
</details>

<details>
<summary>3. ¿Ahorra tokens el paralelismo?</summary>

No. Hace el mismo trabajo en menos tiempo de pared, si el servidor lo permite. El costo en tokens es
prácticamente el mismo.
</details>

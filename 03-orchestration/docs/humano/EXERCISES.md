# Ejercicios

Antes de comenzar, deja el backend en `8012` y el frontend en `5172`, o usa
`uv run orchestration-demo`. Los ejercicios marcados **sin Ollama** solo necesitan
`uv run orchestration-score`. Cada uno tiene una solución plegada; consulta antes
[EXAMPLES.md](EXAMPLES.md) si necesitas un recorrido completo.

## Básico 1 — una corrida guiada

1. Pulsa **Cargar caso I-ORCH-001**.
2. Deja marcadas las dos variantes.
3. Lanza el experimento y espera el evento terminal.
4. Anota cuántos checks aprueba cada variante y si *Corrección* se activó.

**Resultado esperado:** el grafo termina en *Comparación*. El JSONL aparece como ruta relativa. El
Markdown completo no se pega en la bitácora.

<details>
<summary>Qué anotar y cómo interpretarlo</summary>

Una tabla como esta (los números dependen del modelo):

| Variante | Checks | Aprobada | Corrección | Latencia |
|---|---|---|---|---|
| Agente único | `n/9` | sí/no | no aplica | `ms` |
| Orquestada | `n/9` | sí/no | sí/no | `ms` |

Si *Corrección* se activó, el primer borrador del autor falló el gate y recibió la lista de checks
rotos. La orquestada casi siempre tarda más: hace al menos tres llamadas frente a una.
</details>

## Básico 2 — romper el gate a propósito (sin Ollama)

1. Copia `examples/guides/guia-aprobada.md` a `.local/mi-guia.md`.
2. Haz **un solo cambio** que rompa exactamente un check. Ejecuta
   `uv run orchestration-score .local/mi-guia.md`.
3. Repite con otro cambio hasta haber roto tres checks distintos, uno cada vez.

**Resultado esperado:** cada cambio produce `checks=8/9` y la línea `NO` señala el check que rompiste.

<details>
<summary>Tres cambios posibles</summary>

| Cambio | Check que falla |
|---|---|
| Renombrar `## Pasos` a `## Procedimiento` | `has_pasos` |
| Borrar la frase que contiene `/salir` | `has_stop_condition` |
| Añadir «o usa ChatGPT si prefieres» | `no_cloud_fallback` |

Observa que el gate no entiende sinónimos: «Procedimiento» es razonable para una persona, pero el
contrato exige «Pasos». Esa rigidez es el precio de un veredicto repetible.
</details>

## Intermedio 1 — quitar la línea base

1. Desmarca **Agente único**.
2. Lanza de nuevo la misma tarea.
3. Lee el texto del ganador.

**Resultado esperado:** si la orquestada aprueba, `winner=orchestrated` con la nota «Sin linea base
no se afirma una mejora»; si no aprueba, `winner=incomplete`.

**Reflexión:** ¿qué afirmación ya no puedes hacer?

<details>
<summary>Solución</summary>

Puedes decir «la orquestada aprobó el gate», pero no «la orquestación mejoró el resultado». Mejorar
es una comparación: sin la línea base no sabes si un solo agente habría aprobado igual, en menos
tiempo y con menos tokens. El [ejemplo 5](EXAMPLES.md#ejemplo-5--la-regla-de-comparación) muestra el
escenario D.
</details>

## Intermedio 2 — predecir el ganador (sin Ollama)

Para cada caso, escribe el `winner` antes de abrir la solución:

1. Agente único 8/9 sin aprobar; orquestada 8/9 sin aprobar.
2. Agente único 9/9 aprobado en 3 s; orquestada 9/9 aprobada en 30 s.
3. Agente único 9/9 aprobado; orquestada 7/9 tras usar la corrección.

<details>
<summary>Solución</summary>

1. `tie`: ninguna aprueba y suman igual.
2. `tie`: la latencia se registra, pero no desempata.
3. `baseline`: aprobar gana a no aprobar, aunque la orquestada tuviera una segunda oportunidad.

El caso 3 es la lección más importante: más roles y una corrección no garantizan un resultado mejor.
</details>

## Avanzado — experimento observable

1. Ejecuta tres corridas con la misma entrada.
2. Valida cada JSONL con `uv run orchestration-validate`.
3. Compara `prompt_tokens`, `output_tokens` y `wall_duration_ms` de `model.completed`.
4. Mira si el revisor LLM y el gate determinista discreparon (`llm_review_available` frente a
   `passed`).
5. Vuelve a puntuar los borradores con `uv run orchestration-score ".\.local\artifacts\*\*.md"`.

**Resultado esperado:** las tres trazas terminan y se reimportan. La orquestada suele emitir más
eventos y más tokens que el agente único. Eso no implica peor calidad: implica más trabajo.

<details>
<summary>Cómo resumir el experimento</summary>

Construye una tabla por corrida con: checks de cada variante, `winner`, suma de `prompt_tokens` y de
`output_tokens` por variante, y si el revisor opinó distinto del gate. Una discrepancia frecuente es
que el revisor LLM apruebe una guía a la que le falta `/salir`: el gate la rechaza porque busca la
evidencia literal. Si en tus tres corridas la orquestada gana una vez y empata dos, tu conclusión
honesta es «no hay evidencia suficiente de mejora con este modelo», no «orquestar es mejor».
</details>

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un experimento. El nodo activo debe pasar a `failed` con un diagnóstico de
conexión. No debe aparecer un proveedor cloud.

<details>
<summary>Qué comprobar</summary>

El snapshot termina con `status=failed` y `error` con el mensaje de conexión; el JSONL termina en
`run.failed`. No hay reintentos: el orquestador no sabe si el modelo llegó a empezar.
</details>

## Fallo didáctico B — plan inválido

En las pruebas, `test_invalid_plan_fails_only_the_orchestrated_variant` simula un planificador que
no devuelve JSON. La línea base sigue puntuable. Reproduce la idea con el
[ejemplo 4](EXAMPLES.md#ejemplo-4--leer-un-handoff-plan): un texto sin JSON produce
`JsonParseError` antes de que el autor reciba nada.

Nunca uses datos personales en la tarea. El fixture sintético basta.

## Autoevaluación

<details>
<summary>1. ¿Por qué el revisor LLM no decide el aprobado?</summary>

Porque un modelo puede ser inconsistente o complaciente. El gate en código da siempre el mismo
veredicto para el mismo texto; el revisor queda como opinión registrada (`llm_review_passed`).
</details>

<details>
<summary>2. ¿Qué es un handoff y por qué es un JSON y no un párrafo?</summary>

Es la entrega tipada de un rol al siguiente. Un JSON con campos obligatorios se valida antes de
seguir; un párrafo libre obligaría al autor a interpretar y ocultaría errores del planificador.
</details>

<details>
<summary>3. ¿Por qué solo hay una corrección y no un bucle?</summary>

Porque este laboratorio aísla la orquestación. Repetir hasta un umbral con presupuesto es otro tema
con sus propios riesgos; se estudia en [05-agent-loops](../../../05-agent-loops/README.md).
</details>

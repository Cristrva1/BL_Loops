# Ejercicios

Antes de comenzar, deja el backend en `8015` y el frontend en `5176`, o usa
`uv run agent-loops-demo`. Los ejercicios marcados **sin Ollama** solo necesitan
`uv run agent-loops-score` o el modelo guionizado del [ejemplo 3](EXAMPLES.md#ejemplo-3--un-loop-completo-sin-gpu).
Cada uno tiene una solución plegada.

## Básico 1 — una corrida guiada

1. Pulsa **Cargar caso I-LOOP-003**.
2. Deja el prompt inicial débil.
3. Lanza el loop y espera el evento terminal.
4. Anota score inicial, mejor score, número de iteraciones y motivo de salida.

**Resultado esperado:** el grafo termina con un `stop_reason` visible. El JSONL aparece como ruta
relativa. El prompt completo no se pega en la bitácora.

<details>
<summary>Cómo interpretarlo</summary>

Con el prompt débil, el score inicial suele ser 0/5 o 1/5: el modelo responde con prosa. Si el loop
llega a 5/5, el motivo será `threshold_reached` y el número de iteraciones te dice cuántas
reescrituras hicieron falta. Si se agotan las cinco vueltas, el panel muestra el mejor candidato
aunque no apruebe: es el mejor resultado *conocido*, no un éxito.
</details>

## Básico 2 — subir una salida de 2/5 a 5/5 (sin Ollama)

1. Copia `examples/outputs/salida-parcial.json` a `.local/mi-salida.json`.
2. Ejecuta `uv run agent-loops-score .local/mi-salida.json`.
3. Corrige **una** assertion por vez y vuelve a puntuar hasta llegar a 5/5.

<details>
<summary>Solución</summary>

Hacen falta tres cambios, cada uno sube un punto:

1. Añadir un tercer elemento a `steps` → `has_steps`.
2. Añadir a `limits` algo como `"Solo usa Ollama local"` → `has_limits`.
3. Añadir `"stop_condition": "Termina con /salir"` → `has_stop_condition`.

`salida-completa.json` es una solución completa. Fíjate en que «No prometas descuentos» es un buen
límite de negocio, pero no cumple la regla del caso, que pide un límite **local**.
</details>

## Intermedio 1 — prompt ya bueno

1. Sustituye el prompt inicial por uno que pida explícitamente JSON con `title`, `steps`, `limits`
   (Ollama local) y `stop_condition` con `/salir`.
2. Lanza de nuevo la misma tarea.
3. Compara el número de llamadas con la corrida débil.

**Resultado esperado:** una sola iteración y `threshold_reached`. El nodo *Mejorar prompt* permanece
inactivo o se salta.

**Reflexión:** ¿el loop sigue siendo útil cuando el prompt ya cumple el contrato?

<details>
<summary>Solución</summary>

El loop sigue siendo útil como **verificación**: confirma con evidencia que la primera salida
cumple y se detiene sin gastar más. Un buen loop cuesta casi nada cuando no hace falta; un mal loop
seguiría iterando «para mejorar» sin un criterio de parada.
</details>

## Intermedio 2 — predecir el motivo de parada (sin Ollama)

Para cada secuencia, di el `stop_reason` y qué iteración se entrega. Presupuesto por defecto:
5 iteraciones, 2 errores, umbral 5.

1. Puntuaciones 1, 3, 5.
2. Puntuaciones 2, 2, 4, 4, 3.
3. Puntuación 2, error de Ollama, puntuación 3, reescritura inválida.

<details>
<summary>Solución</summary>

1. `threshold_reached` en la iteración 3, que es la que se entrega.
2. `max_iterations`; se entrega la **iteración 3** (el primer 4). La 4 empata y no sustituye; la 5
   empeora.
3. `max_errors`: al segundo error el loop se detiene. Se entrega la iteración con 3 checks.

Puedes comprobar la 2 adaptando el guion del ejemplo 3 con cinco salidas y
`Budget(max_iterations=5, ...)`.
</details>

## Avanzado — experimento observable

1. Ejecuta tres corridas con el prompt débil.
2. Valida cada JSONL con `uv run agent-loops-validate`.
3. Compara `prompt_tokens`, `output_tokens` y el número de eventos `iteration.recorded`.
4. Mira si alguna corrida conservó un mejor candidato distinto del último.

**Resultado esperado:** las tres trazas terminan y se reimportan. Más vueltas implican más tokens.
Eso no implica peor calidad: implica más trabajo hasta el umbral o el presupuesto.

<details>
<summary>Qué concluir</summary>

Registra por corrida: vueltas, motivo de salida, mejor score y tokens totales. Si una corrida
necesitó cinco vueltas y otra dos, el costo puede multiplicarse por más de dos para la misma tarea:
la variabilidad del modelo es parte del resultado. Si alguna conservó un mejor candidato anterior,
acabas de ver por qué «quedarse con el último» habría sido un error.
</details>

## Fallo didáctico A — Ollama detenido

Cierra Ollama y lanza un loop. Los nodos *Generar* o *Mejorar* deben pasar a `failed`. Al segundo
error el loop para con `max_errors`. No debe aparecer un proveedor cloud.

## Fallo didáctico B — reescritura inválida

En las pruebas, `test_invalid_rewrite_counts_as_error_and_jsonl_is_sanitized` simula un mejorador que
no devuelve JSON. El prompt anterior se conserva y el error cuenta para el presupuesto.

Nunca uses datos personales en la tarea. El fixture sintético basta.

## Autoevaluación

<details>
<summary>1. ¿Qué cuatro cosas se declaran antes de la primera llamada?</summary>

Objetivo (cinco assertions), score inicial (se mide en la primera vuelta), presupuesto (iteraciones,
errores y tiempo) y condición de parada (umbral o agotamiento del presupuesto).
</details>

<details>
<summary>2. ¿Por qué el evaluador es código y no el mismo modelo?</summary>

Separar *maker* y *checker* evita que el loop se felicite a sí mismo. Un modelo que puntúa su propia
salida tiende a aprobarse; el código cuenta assertions igual en cada vuelta.
</details>

<details>
<summary>3. ¿Por qué la última iteración no reescribe el prompt?</summary>

Porque ya no habrá otra generación que lo use: reescribirlo gastaría una llamada sin efecto.
</details>

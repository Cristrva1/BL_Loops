# Ejemplos resueltos · Agentes en paralelo

> Los ejemplos 1 a 4 se ejecutan **sin Ollama** y su salida es exactamente reproducible. El ejemplo 5
> depende del modelo y de tu hardware: se muestra la forma esperada. Ejecuta todo desde
> `04-parallel-agents`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Qué exige cada fuente | Hechos obligatorios por rama |
| 2 | El checker de una rama | Procedencia y valor esperado |
| 3 | Unir con una rama caída | Fan-in que no rellena huecos |
| 4 | Calcular un speedup | Tiempo de pared, no tiempo de CPU |
| 5 | Concurrencia limitada | Lo dibujado frente a lo que realmente ocurre |

---

## Ejemplo 1 · Qué exige cada fuente

```powershell
@'
from parallel_agents.sources import load_sources
for fuente in load_sources():
    requeridos = ", ".join(f"{h.fact_id}~{h.expected_contains}" for h in fuente.required_facts)
    print(f"{fuente.source_id} ({fuente.filename}): {requeridos}")
'@ | uv run python -
```

```text
source-a (source-a-precios.md): precio_basico~29, plan_taller~49
source-b (source-b-horario.md): apertura_semana~09, cierre_semana~18
source-c (source-c-garantia.md): garantia_meses~24, recambios~locales
```

**Qué observar:** cada fuente tiene dos hechos obligatorios y el valor debe **contener** el texto
esperado. Las ramas no se necesitan entre sí: por eso este caso puede paralelizarse.

## Ejemplo 2 · El checker de una rama

Tres respuestas posibles del extractor, puntuadas con `score_bundle()`:

```powershell
@'
from parallel_agents.contracts import FactBundle
from parallel_agents.scoring import score_bundle
from parallel_agents.sources import load_sources

fuentes = {f.source_id: f for f in load_sources()}
correcto = FactBundle.model_validate({"source_id": "source-a", "facts": [
    {"fact_id": "precio_basico", "topic": "precio", "value": "29 EUR al mes", "evidence": "El plan basico tiene precio_basico 29 EUR al mes."},
    {"fact_id": "plan_taller", "topic": "precio", "value": "49 EUR al mes", "evidence": "El plan taller tiene plan_taller 49 EUR al mes."}]})
mezclado = FactBundle.model_validate({"source_id": "source-b", "facts": [
    {"fact_id": "apertura_semana", "topic": "horario", "value": "10:00", "evidence": "El sabado abre a las 10:00."}]})
ajeno = FactBundle.model_validate({"source_id": "source-a", "facts": [
    {"fact_id": "garantia_meses", "topic": "garantia", "value": "24", "evidence": "La garantia_meses de reparacion es 24 meses."}]})
print("A correcto:", score_bundle(fuentes["source-a"], correcto))
print("B mezclado:", score_bundle(fuentes["source-b"], mezclado))
print("C con source_id ajeno:", score_bundle(fuentes["source-c"], ajeno))
'@ | uv run python -
```

```text
A correcto: (True, [])
B mezclado: (False, ['apertura_semana!=09', 'cierre_semana'])
C con source_id ajeno: (False, ['source_id esperado source-c'])
```

**Por qué:**

- **B** tomó la hora del **sábado** (10:00) en lugar de la de lunes a viernes (09:00) y olvidó el
  cierre. Es el error típico de un extractor que «suena bien»: el checker lo detecta porque compara
  contra el valor esperado, no contra la confianza del modelo.
- **C** devolvió un hecho correcto **con la procedencia equivocada**. Mezclar fuentes es un error de
  unión, no un detalle estético: el checker se detiene en `source_id` antes de mirar los hechos.

## Ejemplo 3 · Unir con una rama caída

La rama B superó su timeout; A y C terminaron:

```powershell
@'
from parallel_agents.contracts import BranchView, FactRowView
from parallel_agents.scoring import join_branches, render_table

ramas = [
    BranchView(source_id="source-a", node_id="parallel_a", title="Precios", status="completed",
               facts=[FactRowView(fact_id="precio_basico", topic="precio", value="29 EUR", source_id="source-a")]),
    BranchView(source_id="source-b", node_id="parallel_b", title="Horario", status="timeout",
               error="La rama supero el timeout."),
    BranchView(source_id="source-c", node_id="parallel_c", title="Garantia", status="completed",
               facts=[FactRowView(fact_id="garantia_meses", topic="garantia", value="24 meses", source_id="source-c")]),
]
tabla = join_branches(ramas)
print("completed_sources =", tabla.completed_sources)
print("failed_sources    =", tabla.failed_sources)
print(render_table(tabla.rows))
'@ | uv run python -
```

```text
completed_sources = ['source-a', 'source-c']
failed_sources    = ['source-b']
| fact_id | topic | value | source_id |
|---|---|---|---|
| precio_basico | precio | 29 EUR | source-a |
| garantia_meses | garantia | 24 meses | source-c |
```

**Qué observar:** la tabla no contiene ninguna fila de horario. El agregador **no inventa** los
hechos de B ni copia los de otra fuente: deja constancia en `failed_sources` y el dashboard pinta la
rama en rojo. Un fan-in honesto prefiere un hueco visible a un dato fabricado.

## Ejemplo 4 · Calcular un speedup

El laboratorio calcula `speedup = sequential.wall_ms / parallel.wall_ms`, redondeado a dos decimales.

| Secuencial | Paralelo | Speedup | Lectura |
|---|---|---|---|
| 9 000 ms | 3 100 ms | 2.9 | Casi el ideal de 3 ramas: hubo solapamiento real |
| 9 000 ms | 4 500 ms | 2.0 | Mejora parcial: Ollama atendió parte de las llamadas en cola |
| 9 000 ms | 8 800 ms | 1.02 | Sin mejora: con `max_in_flight=1` o un modelo que serializa |

**Qué aprender:** el tiempo de pared es lo que espera la persona. Tres ramas «en paralelo» nunca
bajan del tiempo de la rama más lenta, y si el servidor atiende una llamada a la vez el ahorro
desaparece.

## Ejemplo 5 · Concurrencia limitada a propósito

```powershell
$env:PARALLEL_MAX_IN_FLIGHT = "1"
uv run parallel-agents-demo
Remove-Item Env:PARALLEL_MAX_IN_FLIGHT
```

Forma esperada (los milisegundos dependen del equipo):

```text
max_in_flight=1
...
Secuencial: 3 fuentes, passed=True  <ms> ms
Paralelo: 3 fuentes, passed=True  overlap=False  <ms parecidos al secuencial> ms
Comparacion: winner=<...> speedup=<cercano a 1>
```

**Qué observar:** el grafo puede dibujar las tres ramas en `queued` y `running`, pero
`overlap_observed=False` y `overlap_peak=1` en el JSONL dicen la verdad: nunca hubo dos llamadas a la
vez. Con `PARALLEL_MAX_IN_FLIGHT=3` vuelve a observarse solapamiento si Ollama lo permite.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

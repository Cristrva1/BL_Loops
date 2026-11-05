# Ejemplos resueltos · Orquestación con línea base

> Los ejemplos 1 a 5 se ejecutan **sin Ollama** y su salida es exactamente reproducible. El
> ejemplo 6 depende del modelo: se muestra la forma esperada. Ejecuta todo desde `03-orchestration`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Una guía que aprueba | Qué mide cada uno de los nueve checks |
| 2 | Una guía con dos fallos | El gate señala la evidencia exacta |
| 3 | Un texto fuera de caso | El gate es específico de `I-ORCH-001` |
| 4 | Leer un handoff `Plan` | Contrato entre planificador y autor |
| 5 | La regla de comparación | Cómo se elige ganador sin opiniones |
| 6 | Volver a puntuar lo que escribió el modelo | Reproducir el veredicto del laboratorio |

---

## Ejemplo 1 · Una guía que aprueba el gate

```powershell
uv run orchestration-score .\examples\guides\guia-aprobada.md
```

```text
guia-aprobada.md: passed=True checks=9/9 palabras=88
  OK  has_objetivo         ## Objetivo
  OK  has_pasos            ## Pasos
  OK  has_limites          ## Límites
  OK  has_exito            ## Cómo saber que funcionó
  OK  mentions_ollama      Aparece 'Ollama'.
  OK  has_powershell       Hay un comando local.
  OK  has_stop_condition   Hay /salir o Ctrl+C.
  OK  no_cloud_fallback    Sin marcas cloud.
  OK  length_ok            88 palabras.
```

**Qué mide cada check:**

| Check | Regla en `scoring.py` |
|---|---|
| `has_objetivo`, `has_pasos`, `has_limites`, `has_exito` | Un heading `#`, `##` o `###` con ese texto (acepta «Limites» sin tilde y «Resultado esperado») |
| `mentions_ollama` | La palabra «ollama» en cualquier parte |
| `has_powershell` | Un bloque ` ```powershell `, `Set-Location` o `uv run` |
| `has_stop_condition` | `/salir`, `Ctrl+C` o `Ctrl-C` |
| `no_cloud_fallback` | Ninguno de `openai`, `anthropic`, `chatgpt`, `claude api`, `gemini api`, `gpt-4`, `gpt-5` |
| `length_ok` | Entre 40 y 800 palabras |

## Ejemplo 2 · Dos fallos con su evidencia

```powershell
uv run orchestration-score .\examples\guides\guia-con-fallos.md
```

```text
guia-con-fallos.md: passed=False checks=7/9 palabras=90
  ...
  NO  has_stop_condition   Falta /salir o Ctrl+C.
  NO  no_cloud_fallback    Aparece 'openai'.
  OK  length_ok            90 palabras.
```

**Por qué:** la guía dice «al cerrar la ventana» en vez de `/salir`, y sugiere «usar OpenAI como
respaldo», que contradice la regla de inferencia local. En una corrida real, el orquestador
enviaría al autor exactamente estos `check_id` para su **única** corrección.

## Ejemplo 3 · Un texto fuera de caso

```powershell
uv run orchestration-score .\examples\guides\poema-fuera-de-caso.md
```

```text
poema-fuera-de-caso.md: passed=False checks=1/9 palabras=14
  NO  has_objetivo         Heading ausente.
  ...
  OK  no_cloud_fallback    Sin marcas cloud.
  NO  length_ok            14 palabras.
```

**Qué aprender:** el gate no mide «calidad literaria»; mide si el texto cumple el contrato de
`I-ORCH-001`. Si escribes en el dashboard una tarea distinta (por ejemplo, un poema), el gate
seguirá exigiendo una guía de ejecución local y la variante fallará. Cambiar de caso exige cambiar
de gate.

## Ejemplo 4 · Leer un handoff `Plan`

El planificador debe devolver un objeto con `title`, `audience`, `outline` (3 a 8 secciones) y
`success_checks` (3 a 8). El código acepta que venga dentro de una valla de código, pero no acepta
texto sin JSON ni campos que falten. Prueba el contrato con tres respuestas:

```powershell
@'
from pydantic import ValidationError
from orchestration.contracts import Plan
from orchestration.json_parse import JsonParseError, extract_json_object

respuestas = {
    "plan con valla de codigo": """```json
{"title": "Guia de agente local", "audience": "Estudiante de BL_Loops",
 "outline": [
  {"section_id": "objetivo", "heading": "Objetivo", "must_include": ["Ollama"]},
  {"section_id": "pasos", "heading": "Pasos", "must_include": ["uv run"]},
  {"section_id": "limites", "heading": "Limites", "must_include": ["solo local"]}],
 "success_checks": ["has_objetivo", "has_pasos", "has_limites"]}
```""",
    "plan sin success_checks": '{"title": "Guia", "audience": "Estudiante", "outline": []}',
    "texto sin JSON": "Claro, aqui tienes un plan: primero objetivo, luego pasos.",
}
for nombre, texto in respuestas.items():
    try:
        plan = Plan.model_validate(extract_json_object(texto))
        print(f"{nombre}: Plan valido con {len(plan.outline)} secciones")
    except JsonParseError as exc:
        print(f"{nombre}: JsonParseError -> {exc}")
    except ValidationError as exc:
        campos = sorted({".".join(str(p) for p in e["loc"]) for e in exc.errors()})
        print(f"{nombre}: ValidationError en {campos}")
'@ | uv run python -
```

```text
plan con valla de codigo: Plan valido con 3 secciones
plan sin success_checks: ValidationError en ['outline', 'success_checks']
texto sin JSON: JsonParseError -> No hay un objeto JSON en la respuesta.
```

**Qué observar:** un `Plan` inválido tumba **solo la variante orquestada**; la línea base sigue siendo
puntuable (lo comprueba `test_invalid_plan_fails_only_the_orchestrated_variant`).

## Ejemplo 5 · La regla de comparación

`compare_variants()` decide con este orden: primero quién **aprueba** el gate; después quién suma
**más checks**; si siguen iguales, `tie`. La latencia se registra pero **no desempata**. Resultado de
ejecutar la función con cuatro escenarios sintéticos:

| Escenario | Agente único | Orquestada | `winner` | Nota |
|---|---|---|---|---|
| A | 7/9, falla, 4 000 ms | 9/9, aprueba, 15 000 ms | `orchestrated` | Aprobar gana a no aprobar |
| B | 6/9, falla | 8/9, falla | `orchestrated` | Ninguna aprueba: decide el número de checks |
| C | 9/9, aprueba, 4 000 ms | 9/9, aprueba, 15 000 ms | `tie` | 11 s más lenta, pero la latencia no desempata |
| D | no se ejecutó | 9/9, aprueba | `orchestrated` | Explicación: «Sin linea base no se afirma una mejora.» |

**Qué aprender:** en el escenario C la orquestación costó casi cuatro veces más tiempo para el mismo
resultado. «Más agentes» no es mejor por sí mismo: la evidencia decide.

## Ejemplo 6 · Volver a puntuar lo que escribió el modelo

Después de `uv run orchestration-demo` (o de una corrida en el dashboard), los borradores completos
quedan en `.local/artifacts/<run_id>/`:

```powershell
uv run orchestration-score ".\.local\artifacts\*\*.md"
```

Forma esperada (el contenido depende del modelo):

```text
baseline.md: passed=<True|False> checks=<n>/9 palabras=<n>
  ...
orchestrated.md: passed=<True|False> checks=<n>/9 palabras=<n>
  ...
```

**Qué observar:** el veredicto coincide con el que mostró el dashboard porque es la misma función.
Puedes editar un borrador a mano, volver a puntuarlo y ver qué check cambia; el JSONL de la corrida
original no se modifica.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

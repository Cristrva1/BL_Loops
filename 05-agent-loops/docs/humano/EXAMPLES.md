# Ejemplos resueltos · Loops acotados

> Los ejemplos 1 a 4 se ejecutan **sin Ollama** y su salida es exactamente reproducible; el 3 usa un
> modelo *guionizado* que responde siempre lo mismo para que veas el loop completo sin GPU. El
> ejemplo 5 depende del modelo real: se muestra la forma esperada. Ejecuta todo desde `05-agent-loops`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | La escalera de assertions | Qué separa 0/5 de 5/5 |
| 2 | Cada assertion por dentro | Reglas exactas del evaluador |
| 3 | Un loop completo sin GPU | El mejor candidato no es el último |
| 4 | Los cuatro motivos de parada | Cómo termina un loop acotado |
| 5 | Volver a puntuar el mejor candidato | Reproducir el veredicto del laboratorio |

---

## Ejemplo 1 · La escalera de assertions

```powershell
uv run agent-loops-score ".\examples\outputs\*"
```

```text
salida-completa.json: passed=True checks=5/5
  OK  is_json_object       Hay un objeto JSON.
  OK  has_title            title tiene 38 caracteres.
  OK  has_steps            3 pasos utilizables.
  OK  has_limits           Aparece 'Solo usa el modelo local de Ollama'.
  OK  has_stop_condition   Aparece '/salir'.
salida-debil.txt: passed=False checks=0/5
  NO  is_json_object       No hay un objeto JSON en la respuesta.
  NO  has_title            Falta title o es demasiado corto.
  NO  has_steps            Falta el arreglo steps.
  NO  has_limits           No hay limits locales o no mencionan Ollama.
  NO  has_stop_condition   Falta stop_condition o no declara una parada.
salida-parcial.json: passed=False checks=2/5
  OK  is_json_object       Hay un objeto JSON.
  OK  has_title            title tiene 8 caracteres.
  NO  has_steps            2 pasos utilizables.
  NO  has_limits           No hay limits locales o no mencionan Ollama.
  NO  has_stop_condition   Falta stop_condition o no declara una parada.
```

**Qué observar:** `salida-debil.txt` es lo que suele producir el prompt inicial «Escribe algo útil.»:
prosa amable sin estructura. Si la salida no es JSON, las otras cuatro assertions fallan en cadena,
porque no hay campos que revisar. `salida-parcial.json` tiene forma correcta, pero solo dos pasos, un
límite que no es local y ninguna condición de parada.

## Ejemplo 2 · Cada assertion por dentro

| Assertion | Regla en `scoring.py` |
|---|---|
| `is_json_object` | Hay un objeto JSON (también dentro de una valla de código) |
| `has_title` | `title` es texto de al menos 8 caracteres |
| `has_steps` | `steps` es una lista con al menos 3 textos no vacíos |
| `has_limits` | algún elemento de `limits` contiene «ollama» o «local» |
| `has_stop_condition` | `stop_condition` contiene `/salir`, «presupuesto», «iteración», «timeout» o «parada» |

**Qué aprender:** son reglas **estructurales**. No juzgan si el briefing es persuasivo; juzgan si se
puede usar y verificar. Por eso el umbral es 5 y no «me parece bueno».

## Ejemplo 3 · Un loop completo sin GPU

Este fragmento ejecuta el motor real (`run_loop`) con un modelo guionizado: la primera salida es
prosa, la segunda casi cumple y la tercera empeora. El presupuesto se reduce a tres iteraciones.
Todo se escribe en una carpeta temporal que se borra al terminar.

```powershell
@'
import tempfile
from pathlib import Path
from agent_loops.config import Settings
from agent_loops.engine import Budget, LoopRequest, run_loop
from agent_loops.ollama_client import ChatResult
from agent_loops.prompts import DEFAULT_TASK, INITIAL_PROMPT
from agent_loops.run_log import RunLogger

REESCRITURA = '{"prompt": "Devuelve JSON con title, steps (3+), limits (Ollama local) y stop_condition con /salir.", "rationale": "El prompt debil no pedia estructura."}'
GUION = [
    "Aqui tienes un texto util para vender mas.",
    REESCRITURA,
    '{"title": "Briefing operativo local", "steps": ["Confirmar Ollama", "Cargar briefing", "Responder local"], "limits": ["Ollama local"], "stop_condition": ""}',
    REESCRITURA,
    '{"title": "Briefing operativo local", "steps": ["solo uno"], "limits": ["nada"], "stop_condition": ""}',
]

class ModeloGuionizado:
    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
    def chat(self, messages, *, response_format=None):
        return ChatResult(content=self.respuestas.pop(0), model="guion", total_duration_ms=1.0,
                          prompt_tokens=10, output_tokens=10)

with tempfile.TemporaryDirectory() as carpeta:
    raiz = Path(carpeta)
    ajustes = Settings(root=raiz, base_url="http://127.0.0.1:11434", model="guion", timeout_seconds=5,
                       runs_dir=raiz / "runs", artifacts_dir=raiz / "artifacts")
    registro = RunLogger(ajustes.runs_dir, ajustes.model, ajustes.base_url, "bounded-loop", run_id="run-guion")
    peticion = LoopRequest(task=DEFAULT_TASK, initial_prompt=INITIAL_PROMPT,
                           budget=Budget(max_iterations=3, max_errors=2, timeout_seconds=180, threshold=5))
    resultado = run_loop(peticion, ajustes, ModeloGuionizado(GUION), registro)
    print("Motivo de salida:", resultado.stop_reason)
    for vuelta in resultado.iterations:
        print(f"- iter {vuelta.iteration}: {vuelta.checks_passed}/{vuelta.checks_total}" + (" mejor" if vuelta.is_best else ""))
    print("Mejor candidato: iteracion", resultado.best.iteration, "con", resultado.best.checks_passed, "checks")
'@ | uv run python -
```

```text
Motivo de salida: max_iterations
- iter 1: 0/5
- iter 2: 4/5 mejor
- iter 3: 2/5
Mejor candidato: iteracion 2 con 4 checks
```

**Por qué:** cada vuelta consume dos llamadas (generar y reescribir el prompt), salvo la última, que
solo genera. La iteración 3 empeoró de 4 a 2, pero el loop **entrega la iteración 2**. Ante un
empate se conserva el primero en alcanzar ese puntaje: solo un score *estrictamente* mayor sustituye
al mejor. Es el mismo escenario que verifica `test_keeps_best_candidate_not_the_last`.

## Ejemplo 4 · Los cuatro motivos de parada

| `stop_reason` | Se activa cuando… | Ejemplo |
|---|---|---|
| `threshold_reached` | una salida alcanza las 5 assertions | El prompt ya era bueno: una sola vuelta |
| `max_iterations` | se completan 5 vueltas sin llegar al umbral | Ejemplo 3, con el presupuesto reducido a 3 |
| `max_errors` | hay 2 errores (Ollama caído, reescritura inválida…) | Fallo didáctico A de los ejercicios |
| `timeout` | pasan 180 segundos desde el inicio | Un modelo muy lento en un equipo modesto |

**Qué aprender:** el primero que se cumple gana. Los cuatro están declarados **antes** de la primera
llamada y quedan en el snapshot y en el JSONL; un loop nunca termina «porque sí».

## Ejemplo 5 · Volver a puntuar el mejor candidato

Después de `uv run agent-loops-demo`, el mejor prompt y su salida quedan en
`.local/artifacts/<run_id>/`:

```powershell
uv run agent-loops-score ".\.local\artifacts\*\best-output.txt"
```

Forma esperada (el contenido depende del modelo):

```text
best-output.txt: passed=<True|False> checks=<n>/5
  ...
```

**Qué observar:** el número coincide con «Mejor score» de la demo porque es la misma función. Abre
también `best-prompt.txt` y compáralo con «Escribe algo útil.»: ahí ves qué aprendió el loop.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

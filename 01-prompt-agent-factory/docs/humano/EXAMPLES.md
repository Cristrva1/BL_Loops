# Ejemplos resueltos · Fábrica de prompts, agentes y skills

> Seis recorridos completos con su salida real. Ejecuta cada comando desde la raíz del laboratorio
> (`01-prompt-agent-factory`). Ninguno necesita Ollama ni red. Los identificadores (`prompt_…`) y
> las huellas cambian en cada ejecución porque incluyen un UUID y la fecha de creación; lo demás es
> idéntico.

| # | Ejemplo | Concepto que enseña |
|---|---|---|
| 1 | Listar los briefings | Qué hace que un briefing esté “listo” |
| 2 | Briefing incompleto | La fábrica pregunta en vez de inventar |
| 3 | Agente sin herramientas | Una lista vacía confirmada es una decisión de seguridad |
| 4 | Skill portable | Disparadores, procedimiento y revelado progresivo |
| 5 | Huella alterada | Validar la forma no es lo mismo que verificar la integridad |
| 6 | La misma lógica por HTTP | La API devuelve los mismos estados que pinta el dashboard |

---

## Ejemplo 1 · Listar los briefings de ejemplo

**Objetivo:** ver de un vistazo qué briefings existen y cuál falta completar.

```powershell
uv run factory-demo --list
```

**Salida:**

```text
Briefings de ejemplo en examples/intakes:
- agent_local_reader.json · agent · Agente lector local · listo para construir
- agent_ticket_triage.json · agent · Clasificador de tickets sin tools · listo para construir
- incomplete_agent_brief.json · agent · Organizador de descargas · incompleto: 7 preguntas pendientes
- prompt_duplicate_finder.json · prompt · Detector seguro de duplicados · listo para construir
- prompt_rag_citation_checker.json · prompt · Verificador de citas RAG · listo para construir
- skill_meeting_minutes.json · skill · Minuta trazable de reunión · listo para construir

Construye uno con: uv run factory-demo --intake <archivo.json>
```

**Qué observar:** “listo” no significa “bueno”; significa que no quedan **campos obligatorios**
vacíos. La calidad del contenido sigue siendo responsabilidad humana.

## Ejemplo 2 · Un briefing incompleto produce preguntas, no un artefacto

**Objetivo:** comprobar que la fábrica no rellena huecos con suposiciones.

**Entrada** (`examples/intakes/incomplete_agent_brief.json`, resumida):

```json
{
  "artifact_type": "agent",
  "idea": "Quiero un agente que me ayude a organizar mis archivos de la carpeta de descargas.",
  "title": "Organizador de descargas",
  "allowed_tools": ["local_file_reader"],
  "tools_confirmed": false
}
```

```powershell
uv run factory-demo --intake incomplete_agent_brief.json
```

**Salida** (primeras preguntas):

```text
Briefing incompleto: incomplete_agent_brief.json (22% listo)
La fábrica no inventa los huecos; antes necesita estas decisiones:
  ? [audience] ¿Quién usará o leerá el resultado?
    Por qué importa: La audiencia cambia el vocabulario, la profundidad y los supuestos permitidos.
    Ejemplo: Persona con conocimientos básicos de PowerShell
  ? [context] ¿En qué situación se ejecutará y qué información ya conocemos?
    Por qué importa: El contexto reduce huecos que un modelo podría rellenar inventando.
    Ejemplo: Se revisa una carpeta local en modo solo lectura y con datos sintéticos.
  ...
  ? [tools_confirmed] ¿Confirmas explícitamente la lista de herramientas, aunque esté vacía?
    Por qué importa: Una lista vacía confirmada es segura; una lista olvidada es un hueco de autoridad.
    Ejemplo: Sí: únicamente local_file_reader en modo simulado.
No se construyó ni exportó ningún artefacto.
```

**Por qué ocurre:** un agente necesita nueve campos obligatorios (los ocho comunes más
`tools_confirmed`). Hay dos completos: `2 / 9 = 0.222`, es decir, 22 %. El comando termina con código
de salida `1` para que un script sepa que no se exportó nada.

**Qué aprender:** el briefing pide un agente que “organice” descargas, pero no dice si puede mover o
borrar. Esa ambigüedad es exactamente la que un modelo resolvería inventando permisos.

## Ejemplo 3 · Un agente sin herramientas

**Objetivo:** ver qué contiene un `AgentSpec` cuando la lista de tools está vacía **y confirmada**.

```powershell
uv run factory-demo --intake agent_ticket_triage.json
```

**Salida:**

```text
Briefing: agent_ticket_triage.json
Artefacto: agent_d4ca5983e702
Tipo: agent
Huella: 1df70f3274f873d6f37727a281dc0d7ee5cd950280b4f3daa35ca26cc0f1541d
Exportado: .local/exports/agent_d4ca5983e702.json
IA utilizada: no; plantilla determinista de la Parte 1
```

Campos clave del JSON exportado:

```text
tools = []
max_steps = 4
human_approval = True
permissions = {"default_effect": "deny", "runtime_network": false, "external_writes": false, "rules": []}
memory = {"short_term": true, "long_term": false, "stores_raw_pii": false, "retention": "run_only"}
stop_conditions = success_criteria_met->done, missing_information->blocked,
                  unsafe_or_unauthorized->blocked, step_budget_reached->failed
```

**Qué observar:**

- `default_effect: deny` y `rules: []`: sin reglas, todo está prohibido.
- `step_budget_reached → failed`: el agente tiene un presupuesto de cuatro pasos; agotarlo es un
  fallo visible, no un “sigue intentando”.
- La memoria dura una corrida (`run_only`) y no guarda PII cruda.

## Ejemplo 4 · Una skill portable

**Objetivo:** distinguir una skill de un prompt.

```powershell
uv run factory-demo --intake skill_meeting_minutes.json
```

Del JSON exportado (`.local/exports/skill_*.json`):

```text
triggers = ["Cuando la solicitud requiera: Crear una skill portable que convierta una transcripción
            sintética de reunión en una minuta con decisiones, responsables y fechas, sin inventar
            compromisos."]

progressive_disclosure = [
  "Leer primero el objetivo y las restricciones.",
  "Abrir solo la referencia necesaria para la tarea actual.",
  "Cargar ejemplos o scripts únicamente cuando el procedimiento los solicite."
]
```

Y su `instruction_template` empieza así:

```markdown
# Skill generada

## Objetivo
Crear una skill portable que convierta una transcripción sintética de reunión en una minuta ...

## Procedimiento
1. Validar entradas y autoridad.
2. Leer únicamente los recursos necesarios.
3. Producir la salida según el contrato.
4. Verificar criterios de éxito y condiciones de parada.
```

**Qué observar:** las tres restricciones del briefing aparecen en `constraints` **junto a** tres
restricciones que la fábrica añade siempre: no inventar datos, declarar la incertidumbre y no
realizar efectos externos. Un prompt dice *qué pedir*; una skill dice además *cuándo activarse* y
*qué leer primero*.

> Conexión: el laboratorio [25-meeting-summarizer](../../../25-meeting-summarizer/README.md) resuelve
> esta misma tarea con un modelo real. Esta skill es su especificación portable.

## Ejemplo 5 · Huella alterada

**Objetivo:** demostrar que un JSON puede ser válido y, aun así, haber sido manipulado.

Después del ejemplo 4, ejecuta en PowerShell:

```powershell
@'
import json
from pathlib import Path
from prompt_agent_factory.contracts import SkillSpec
from prompt_agent_factory.hashing import has_valid_content_hash

path = sorted(Path(".local/exports").glob("skill_*.json"))[0]
data = json.loads(path.read_text(encoding="utf-8"))
print("Huella original valida:", has_valid_content_hash(SkillSpec.model_validate(data)))
data["title"] = "Minuta editada a mano"
print("Huella tras editar el titulo valida:", has_valid_content_hash(SkillSpec.model_validate(data)))
'@ | uv run python -
```

**Salida:**

```text
Huella original valida: True
Huella tras editar el titulo valida: False
```

**Por qué ocurre:** Pydantic acepta el JSON editado porque sigue teniendo la **forma** correcta. La
huella SHA-256 se calculó sobre el contenido original; al cambiar el título ya no coincide. Por eso
`/api/v1/artifacts/export` responde `422 content_hash_mismatch` y el exportador se niega a escribir.

## Ejemplo 6 · La misma lógica por HTTP

**Objetivo:** ver que el dashboard solo dibuja lo que la API devuelve.

Terminal A:

```powershell
uv run uvicorn prompt_agent_factory.main:app --host 127.0.0.1 --port 8011
```

Terminal B:

```powershell
Invoke-RestMethod http://127.0.0.1:8011/api/v1/health
$brief = Get-Content -Raw .\examples\intakes\incomplete_agent_brief.json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8011/api/v1/factory/questions `
    -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($brief))
```

**Salida resumida:**

```text
health    → status=ok, phase=part-1-contracts, llm_used=False, configuration_scope=defaults
questions → ready=False, readiness=0.222, completed_fields=[idea, title]
events    → capture=done, clarify=waiting, contract=idle, validate=idle, export=idle
```

Si envías el mismo briefing a `/api/v1/factory/draft`, la respuesta es `HTTP 422` con
`detail.code = "incomplete_intake"` y la misma lista de preguntas.

**Qué observar:** los cinco estados (`done`, `waiting`, `idle`…) son exactamente los colores que el
grafo React Flow pinta. `configuration_scope` dice de dónde salió la configuración (`lab`,
`workspace` o `defaults`) sin revelar ningún valor del `.env`.

---

Siguiente paso: practica con [EXERCISES.md](EXERCISES.md). Si algo no coincide, consulta
[TROUBLESHOOTING.md](TROUBLESHOOTING.md).

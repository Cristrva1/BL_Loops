# 01 · Fábrica de prompts, agentes y skills

> **Pregunta:** ¿cómo se convierte una idea incompleta en un artefacto claro, validado y reutilizable?
> **Nivel:** 1 · **Tiempo:** ~45 min · **Necesita Ollama:** no

Primera aplicación de BL_Loops. Recibe un *briefing* (lo que quieres conseguir), detecta qué
decisiones faltan, construye un `PromptSpec`, `AgentSpec` o `SkillSpec` validado con Pydantic, le
calcula una huella SHA-256 y lo exporta como JSON portable. Todo es determinista: la interfaz, la
API, los contratos y la exportación son reales, pero todavía no se llama a ningún modelo.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops, en PowerShell:

```powershell
Set-Location .\01-prompt-agent-factory
uv sync --all-groups                                          # crea la .venv propia del laboratorio
uv run factory-demo --list                                    # lista los briefings de ejemplo
uv run factory-demo --intake incomplete_agent_brief.json      # ve qué preguntas faltan
uv run factory-demo --intake skill_meeting_minutes.json       # construye y exporta una skill
uv run factory-demo --all                                     # procesa todos los ejemplos
```

Dashboard visual (dos terminales):

```powershell
uv run uvicorn prompt_agent_factory.main:app --host 127.0.0.1 --port 8011 --reload
npm --prefix frontend install
npm --prefix frontend run dev                                 # abre http://127.0.0.1:5173
```

## Qué deberías ver

```text
Briefing incompleto: incomplete_agent_brief.json (22% listo)
La fábrica no inventa los huecos; antes necesita estas decisiones:
  ? [audience] ¿Quién usará o leerá el resultado?
  ...
No se construyó ni exportó ningún artefacto.
```

Con un briefing completo aparece `Exportado: .local/exports/<id>.json` y la línea
`IA utilizada: no; plantilla determinista de la Parte 1`.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/prompt_agent_factory/` | Contratos, preguntas guiadas, fábrica, API y exportador |
| `backend/tests/` | Pruebas deterministas: no necesitan red ni modelo |
| `examples/intakes/` | Seis briefings sintéticos: prompt, agente, skill y uno incompleto |
| `contracts/generated/` | JSON Schema regenerable con `uv run factory-export-schemas` |
| `frontend/` | Dashboard React + React Flow |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/exports/` | Artefactos exportados (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): comandos explicados y resultado esperado.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): seis recorridos con salidas reales.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [contratos](docs/humano/CONTRACTS.md),
   [metodología](docs/humano/METHODOLOGY.md), [evaluación](docs/humano/EVALUATION.md) y
   [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** la [guía maestra](../docs/humano/maestro/RUTA_DE_APRENDIZAJE.md).
**Sigue con:** [02-single-agent](../02-single-agent/README.md), donde un modelo real responde.

## Estado y límites

- **Implementado:** contratos estrictos, preguntas guiadas, API, dashboard, exportación con huella,
  demo CLI con seis briefings.
- **Aplazado a la Parte 2:** generación y crítica con Ollama, SQLite, SSE y ejecución de tools.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

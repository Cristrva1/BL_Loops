# 03 · Orquestación: planificador, autor y revisor frente a un agente único

> **Pregunta:** ¿qué mejora realmente al separar una tarea entre agentes especializados?
> **Nivel:** 2 · **Tiempo:** ~60 min · **Necesita Ollama:** sí, con `qwen3.5:4b` (el gate funciona sin él)

La misma tarea entra en dos variantes: un **agente único** (la línea base) y un **pipeline de tres
roles** donde el planificador entrega un `Plan` JSON, el autor escribe Markdown y el revisor opina.
El aprobado no lo decide ningún modelo: lo decide un **gate determinista** de nueve checks en código.
Si el gate falla, el autor tiene una sola corrección. El dashboard pinta cada nodo con eventos SSE
reales y la corrida queda en un JSONL sanitizado.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\03-orchestration
uv sync --all-groups
uv run orchestration-score ".\examples\guides\*.md"   # el gate, sin modelo
uv run orchestration-demo                             # experimento completo con Ollama
uv run orchestration-validate                         # importa el JSONL de la corrida
```

Dashboard (dos terminales):

```powershell
uv run uvicorn orchestration.main:app --host 127.0.0.1 --port 8012 --reload
npm --prefix frontend install
npm --prefix frontend run dev                         # abre http://127.0.0.1:5172
```

## Qué deberías ver

`orchestration-score` puntúa las tres guías de ejemplo:

```text
guia-aprobada.md: passed=True checks=9/9 palabras=88
guia-con-fallos.md: passed=False checks=7/9 palabras=90
  NO  has_stop_condition   Falta /salir o Ctrl+C.
  NO  no_cloud_fallback    Aparece 'openai'.
poema-fuera-de-caso.md: passed=False checks=1/9 palabras=14
```

`orchestration-demo` imprime los checks de cada variante, si se usó la corrección, el ganador y la
ruta del JSONL. El texto generado cambia en cada corrida; la regla para decidir no cambia.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/orchestration/` | Orquestador, gate (`scoring.py`), cliente Ollama, API, store y JSONL |
| `backend/tests/` | Pruebas con un modelo guionizado: no necesitan Ollama |
| `examples/i-orch-001.json` | Caso de evaluación `I-ORCH-001` |
| `examples/guides/` | Tres guías para practicar con el gate: aprobada, con fallos y fuera de caso |
| `contracts/` | JSON Schema de eventos y de los handoffs `Plan` y `Review` |
| `frontend/` | Dashboard React Flow alimentado por SSE |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | JSONL en `runs/` y borradores completos en `artifacts/<run_id>/` (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): requisitos, dashboard y demo.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): gate, handoffs y regla de comparación con salidas reales.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [02-single-agent](../02-single-agent/README.md), que aquí actúa como línea base.
**Sigue con:** [04-parallel-agents](../04-parallel-agents/README.md), donde las ramas corren a la vez.

## Estado y límites

- **Implementado (corte A0):** orquestador propio y secuencial, una corrección máxima, línea base,
  gate determinista, `orchestration-score`, dashboard SSE y JSONL sanitizado.
- **Aplazado:** LangGraph, CrewAI, AG2, paralelismo y comparación de los cuatro modelos.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

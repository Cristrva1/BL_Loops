# 05 · Loops acotados: mejorar un prompt sin quedar atrapado

> **Pregunta:** ¿cómo se diseña un ciclo que mejore resultados sin gastar recursos indefinidamente?
> **Nivel:** 2 · **Tiempo:** ~45 min · **Necesita Ollama:** sí, con `qwen3.5:4b` (las assertions funcionan sin él)

Un prompt deliberadamente débil («Escribe algo útil.») produce una salida. Un evaluador en código
cuenta **cinco assertions** estructurales. Si no se alcanza el umbral, otra llamada reescribe el
prompt y se vuelve a intentar. El loop declara antes de empezar su objetivo, su presupuesto (cinco
iteraciones, dos errores o 180 segundos) y su condición de parada, y al terminar entrega el **mejor
candidato visto**, no necesariamente el último.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\05-agent-loops
uv sync --all-groups
uv run agent-loops-score ".\examples\outputs\*"   # las cinco assertions, sin modelo
uv run agent-loops-demo                           # loop completo con Ollama
uv run agent-loops-validate                       # importa el JSONL de la corrida
```

Dashboard (dos terminales):

```powershell
uv run uvicorn agent_loops.main:app --host 127.0.0.1 --port 8015 --reload
npm --prefix frontend install
npm --prefix frontend run dev                     # abre http://127.0.0.1:5176
```

## Qué deberías ver

```text
salida-completa.json: passed=True checks=5/5
salida-debil.txt: passed=False checks=0/5
salida-parcial.json: passed=False checks=2/5
```

`agent-loops-demo` imprime el motivo de salida, el score inicial, el mejor score y una línea por
iteración, marcando cuál fue la mejor. Una corrida que alcanza el umbral en la segunda vuelta tiene
esta forma:

```text
Motivo de salida: threshold_reached
Score inicial: 0/5
Mejor score: 5/5
- iter 1: 0/5
- iter 2: 5/5 mejor
```

Los números dependen del modelo; la forma y los motivos posibles (`threshold_reached`,
`max_iterations`, `max_errors`, `timeout`) no.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/agent_loops/` | Motor del loop, assertions (`scoring.py`), cliente Ollama, API, store y JSONL |
| `backend/tests/` | Pruebas con un modelo guionizado: no necesitan Ollama |
| `examples/i-loop-003.json` | Caso `I-LOOP-003` con su presupuesto |
| `examples/outputs/` | Tres salidas para practicar: débil (0/5), parcial (2/5) y completa (5/5) |
| `contracts/` | JSON Schema de eventos, declaración del loop y reescritura de prompt |
| `frontend/` | Dashboard React Flow alimentado por SSE |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | JSONL en `runs/`; mejor prompt y salida en `artifacts/<run_id>/` (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): requisitos, dashboard y demo.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): assertions, mejor candidato y motivos de parada.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [04-parallel-agents](../04-parallel-agents/README.md).
**Sigue con:** [06-naive-rag](../06-naive-rag/README.md), donde el agente empieza a buscar evidencia.

## Estado y límites

- **Implementado (corte A0):** loop Python tipado, cinco assertions, presupuesto de iteraciones,
  errores y tiempo, conservación del mejor candidato, `agent-loops-score`, dashboard SSE y JSONL.
- **Aplazado:** LangGraphJS, OpenEvolve y el runtime de `loop-engineering`.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

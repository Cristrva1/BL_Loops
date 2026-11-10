# 04 · Agentes en paralelo: fan-out, fan-in y procedencia

> **Pregunta:** ¿cuándo el paralelismo reduce tiempo sin degradar coherencia ni agotar la VRAM?
> **Nivel:** 2 · **Tiempo:** ~45 min · **Necesita Ollama:** sí, con `qwen3.5:4b` (el checker funciona sin él)

Tres documentos independientes del «Taller Norte» (precios, horario y garantía) alimentan la misma
tarea de extracción. La variante **secuencial** procesa A, luego B, luego C; la **paralela** lanza
las tres ramas a la vez contra un solo modelo compartido, con un tope `max_in_flight` y un timeout
por rama. El agregador une los hechos conservando su `source_id` y **nunca** presenta como completa
una rama fallida. El dashboard mide el tiempo de pared y si hubo solapamiento real.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\04-parallel-agents
uv sync --all-groups
uv run parallel-agents-demo        # secuencial frente a paralelo con Ollama
uv run parallel-agents-validate    # importa el JSONL de la corrida
```

Dashboard (dos terminales):

```powershell
uv run uvicorn parallel_agents.main:app --host 127.0.0.1 --port 8014 --reload
npm --prefix frontend install
npm --prefix frontend run dev      # abre http://127.0.0.1:5175
```

## Qué deberías ver

La demo informa, para cada variante, el tiempo de pared (`wall_ms`), las fuentes completas y
fallidas, el `speedup` y `overlap_observed`. Con un solo modelo compartido es normal un speedup
menor que 3: Ollama puede atender las llamadas en cola. El laboratorio lo muestra en lugar de
esconderlo.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/parallel_agents/` | Orquestador `asyncio`, checker (`scoring.py`), fuentes, API, store y JSONL |
| `backend/tests/` | Pruebas con un modelo guionizado: no necesitan Ollama |
| `examples/sources/` | Las tres fuentes sintéticas del caso `I-PARALLEL-002` |
| `examples/i-parallel-002.json` | Definición del caso |
| `contracts/` | JSON Schema de eventos y del handoff `FactBundle` |
| `frontend/` | Dashboard React Flow alimentado por SSE |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): requisitos, dashboard y demo.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): checker, unión con una rama caída y speedup.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [03-orchestration](../03-orchestration/README.md), donde los pasos dependen uno del otro.
**Sigue con:** [05-agent-loops](../05-agent-loops/README.md), donde el mismo paso se repite con presupuesto.

## Estado y límites

- **Implementado (corte A):** fan-out con `asyncio.gather` y tope `max_in_flight`, timeout por rama,
  agregador determinista, comparación de tiempos, dashboard SSE y JSONL sanitizado.
- **Aplazado:** LangGraphJS, CrewAI/AG2 y varios modelos simultáneos en VRAM.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

# 04-parallel-agents

Laboratorio autónomo para observar cuándo un fan-out/fan-in de tres fuentes independientes reduce el tiempo de pared sin degradar la coherencia ni presentar una rama fallida como completa.

## Ejecutar

```powershell
uv sync --all-groups
npm --prefix frontend install
```

Backend:

```powershell
uv run uvicorn parallel_agents.main:app --host 127.0.0.1 --port 8014 --reload
```

Frontend, en otra terminal:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5175`. El grafo deriva de eventos SSE reales. Carga el caso `I-PARALLEL-002` para comparar la línea secuencial con el fan-out.

Demostración CLI sin interfaz:

```powershell
uv run parallel-agents-demo
uv run parallel-agents-validate
```

## Organización

- `AGENTS.md`: reglas portables para futuras sesiones.
- `backend/`: orquestador asyncio, cliente de Ollama, API y pruebas.
- `frontend/`: dashboard React Flow.
- `contracts/`: JSON Schema de eventos y del `FactBundle`.
- `examples/`: fixture sintético `I-PARALLEL-002` y tres fuentes independientes.
- `docs/humano/`: guía didáctica. El runtime no la lee.

> Estado: corte A. Un modelo Ollama compartido, `asyncio.gather` y un agregador determinista. LangGraph, CrewAI, AG2 y varios modelos simultáneos quedan aplazados.

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md).

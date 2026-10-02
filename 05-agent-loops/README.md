# 05-agent-loops

Laboratorio autónomo para observar cómo un ciclo mejora un prompt con un score determinista, un presupuesto visible y un mejor candidato, sin ejecutarse indefinidamente.

## Ejecutar

```powershell
uv sync --all-groups
npm --prefix frontend install
```

Backend:

```powershell
uv run uvicorn agent_loops.main:app --host 127.0.0.1 --port 8015 --reload
```

Frontend, en otra terminal:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5176`. El grafo deriva de eventos SSE reales. Carga el caso `I-LOOP-003` para ver score inicial, iteraciones y motivo de parada.

Demostración CLI sin interfaz:

```powershell
uv run agent-loops-demo
uv run agent-loops-validate
```

## Organización

- `AGENTS.md`: reglas portables para futuras sesiones.
- `backend/`: loop tipado, cliente de Ollama, API y pruebas.
- `frontend/`: dashboard React Flow.
- `contracts/`: JSON Schema de eventos y declaración del loop.
- `examples/`: fixture sintético `I-LOOP-003`.
- `docs/humano/`: guía didáctica. El runtime no la lee.

> Estado: corte A0. Loop Python propio con evaluador determinista, máximo cinco iteraciones, dos errores o tres minutos. LangGraph, OpenEvolve y `loop-engineering` como runtime quedan aplazados.

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md).

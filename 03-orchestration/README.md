# 03-orchestration

Laboratorio autónomo para observar qué cambia al separar una tarea entre un planificador, un autor y un revisor, comparado con un agente único que recibe la misma entrada.

## Ejecutar

```powershell
uv sync --all-groups
npm --prefix frontend install
```

Backend:

```powershell
uv run uvicorn orchestration.main:app --host 127.0.0.1 --port 8012 --reload
```

Frontend, en otra terminal:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5172`. El grafo deriva de eventos SSE reales. Carga el caso `I-ORCH-001` para comparar las dos variantes.

Demostración CLI sin interfaz:

```powershell
uv run orchestration-demo
uv run orchestration-validate
```

## Organización

- `AGENTS.md`: reglas portables para futuras sesiones.
- `backend/`: orquestador, cliente de Ollama, API y pruebas.
- `frontend/`: dashboard React Flow.
- `contracts/`: JSON Schema de eventos y handoffs generados.
- `examples/`: fixture sintético `I-ORCH-001`.
- `docs/humano/`: guía didáctica. El runtime no la lee.

> Estado: corte A0. Orquestador propio, secuencial, con una corrección máxima y línea base de agente único. LangGraph, CrewAI, AG2 y el paralelismo quedan aplazados.

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md).

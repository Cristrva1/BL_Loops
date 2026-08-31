# 01-prompt-agent-factory

Primera aplicación autónoma de BL_Loops: API FastAPI, contratos Pydantic, exportación local y dashboard React Flow para construir `PromptSpec`, `AgentSpec` y `SkillSpec`.

## Ejecutar

```powershell
uv sync --all-groups
npm --prefix frontend install
```

Backend:

```powershell
uv run uvicorn prompt_agent_factory.main:app --host 127.0.0.1 --port 8011 --reload
```

Frontend, en otra terminal:

```powershell
npm --prefix frontend run dev
```

## Organización

- `AGENTS.md`: instrucciones operativas del laboratorio para futuras sesiones de Codex.
- `backend/`: código Python y pruebas.
- `frontend/`: aplicación React/Vite.
- `contracts/generated/`: JSON Schema regenerable.
- `examples/`: fixtures sintéticos.
- `docs/humano/`: guía didáctica, metodología, ejercicios, arquitectura explicada, evaluación y diagnóstico.

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md). El inicio guiado está en [docs/humano/QUICKSTART.md](docs/humano/QUICKSTART.md).

> Estado: Parte 1 terminada. Esta base es determinista y no invoca Ollama; la generación con IA local corresponde a la Parte 2.

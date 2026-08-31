# 13-sales-knowledge-curator

Fábrica local de conocimiento confiable de ventas. Audita fuentes de solo lectura, extrae afirmaciones trazables, muestra conflictos y publica un `KnowledgeRelease` versionado después de una decisión humana sobre un hash exacto.

## Ejecutar

```powershell
uv sync --all-groups
npm --prefix frontend install
```

Backend:

```powershell
uv run uvicorn sales_curator.api.main:app --host 127.0.0.1 --port 8013 --reload
```

Frontend, en otra terminal:

```powershell
npm --prefix frontend run dev
```

Demo de un corte:

```powershell
uv run sales-curator demo --fixture .\fixtures\corpus --reviewer operador-local --reason "Aprobacion didactica del operador"
```

## Organización

- `AGENTS.md`: instrucciones operativas del laboratorio.
- `backend/`: contratos, orquestador, SQLite, API y pruebas.
- `frontend/`: React Flow con estados reales.
- `fixtures/corpus/`: fuentes sintéticas (vigente, obsoleta, contradictoria, sindicada, inyección, vacía, derechos inciertos).
- `contracts/generated/`: JSON Schema regenerable.
- `docs/humano/`: guía didáctica.

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md). El inicio guiado está en [docs/humano/QUICKSTART.md](docs/humano/QUICKSTART.md).

> Estado: fase 1, corte vertical local. No hay navegación web real ni integración con `09-agentic-rag`.

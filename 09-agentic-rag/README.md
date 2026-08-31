# 09 · Agente experto en ventas con RAG

Laboratorio autónomo y copiable de un agente local de ventas. `qwen3.5:4b` decide cómo
formular una consulta, el runtime ejecuta **como máximo una** herramienta
`search_sales_library` y la respuesta se apoya en un índice privado SQLite FTS5 +
`qwen3-embedding:latest`.

No convierte automáticamente una colección débil en conocimiento experto: el corpus actual
contiene sobre todo metadatos y descripciones editoriales, algunas no revisadas. El agente
expone ese límite, filtra secciones conocidas como contaminadas y cita archivo y líneas.

## Inicio rápido

```powershell
cd C:\Users\criss\Desktop\Claude\BL_Loops\09-agentic-rag
uv sync
uv run sales-agent index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
uv run sales-agent ask "¿Cómo vender una vivienda sin presionar?"
uv run sales-agent chat
```

Comandos adicionales:

```powershell
uv run sales-agent stats
uv run sales-agent-validate
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

En `chat`, usa `/estado`, `/limpiar` o `/salir`. La conversación vive solo en RAM. Cada
turno exporta una traza JSONL sanitizada en `.local/runs/`; ni la pregunta, ni la respuesta,
ni los fragmentos crudos se guardan allí.

## Documentación

- [Guía humana](docs/humano/README.md)
- [Quickstart explicado](docs/humano/QUICKSTART.md)
- [Arquitectura](docs/humano/ARCHITECTURE.md)
- [Metodología y límites](docs/humano/METHODOLOGY.md)
- [Ejercicios](docs/humano/EXERCISES.md)
- [Diagnóstico](docs/humano/TROUBLESHOOTING.md)
- [Evaluación](docs/humano/EVALUATION.md)
- [Contrato JSONL](contracts/run-event.schema.json)

El runtime no importa otros laboratorios ni archivos de `docs/humano/`. Su `.venv`, lock,
índice y corridas son propios. Solo se conecta por HTTP a Ollama local y no dispone de CRM,
navegador, correo, mensajería ni fallback cloud.


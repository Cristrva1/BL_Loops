# Instrucciones de trabajo de 03-orchestration

Estas reglas se aplican a todo este laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; al copiar el laboratorio, conservan sus límites esenciales.

## Objetivo y estado

- Este corte enseña la diferencia observable entre un agente único y un pipeline planificador → autor → revisor.
- El revisor modelo puede emitir un JSON de opinión; el gate de aprobado es una lista determinista.
- Si el gate falla, el autor corrige una sola vez. Eso no es el laboratorio de loops.
- La línea base de agente único forma parte del experimento. Sin ella no se afirma una mejora.
- No presentar LangGraph, CrewAI, AG2, paralelismo, tools, RAG ni conectores como capacidades existentes.

## Separación y seguridad

- `backend/`, `frontend/`, `contracts/` y `examples/` son operativos; `docs/humano/` nunca es una dependencia del runtime.
- No importar código, bases de datos ni servicios de otro laboratorio.
- Toda escritura se limita a `.local/runs/` y `.local/artifacts/` dentro de este proyecto.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`.
- No añadir fallbacks cloud, telemetría ni conectores reales.
- El JSONL no guarda prompts ni el Markdown completo.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se lee el `.env` de la raíz; fuera del repositorio se admite un `.env` local creado desde `.env.example`.
- Las rutas relativas se resuelven contra la raíz de este laboratorio.
- Backend en `127.0.0.1:8012`. Frontend en `127.0.0.1:5172`.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md`, `docs/humano/EXAMPLES.md` y el documento humano relacionado con la tarea.
3. Mantener una única ruta de ejecución fácil de explicar: tarea → variantes → handoffs → gate → JSONL.
4. Actualizar documentación y pruebas en el mismo cambio.
5. Distinguir lo implementado de lo aplazado.
6. No hacer commit, push, publicación ni descargas sin solicitud explícita.

## Verificación

Ejecutar desde esta carpeta:

```powershell
uv sync --all-groups
uv run pytest
uv run ruff check .
npm --prefix frontend run build
uv run orchestration-score ".\examples\guides\*.md"
uv run orchestration-demo
uv run orchestration-validate
```

Las pruebas usan dobles locales y no invocan Ollama. La demostración sí requiere el modelo configurado.

## Reglas al tocar el gate o el store

- Si cambias `scoring.py`, revisa los veredictos esperados de `examples/guides/` (9/9, 7/9 y 1/9),
  sus pruebas y `docs/humano/EXAMPLES.md` en el mismo cambio.
- Los eventos `run.completed` y `run.failed` se publican mediante `STORE.finish` o `STORE.fail`,
  nunca antes de guardar el resultado. El stream SSE debe leer con `STORE.read_since`.

# Instrucciones de trabajo de 04-parallel-agents

Estas reglas se aplican a todo este laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; al copiar el laboratorio, conservan sus límites esenciales.

## Objetivo y estado

- Este corte enseña la diferencia observable entre extraer tres fuentes en serie y extraerlas en fan-out con un fan-in posterior.
- El agregador espera resultados o un timeout explícito. Una rama fallida no se presenta como completa.
- Cada hecho conserva `source_id`. Sin procedencia no hay tabla válida.
- Se comparan tiempos de pared. Un único modelo compartido puede serializar en Ollama; el reloj manda.
- No presentar LangGraph, CrewAI, AG2, varios modelos en VRAM, loops, tools ni RAG como capacidades existentes.

## Separación y seguridad

- `backend/`, `frontend/`, `contracts/` y `examples/` son operativos; `docs/humano/` nunca es una dependencia del runtime.
- No importar código, bases de datos ni servicios de otro laboratorio.
- Toda escritura se limita a `.local/runs/` y `.local/artifacts/` dentro de este proyecto.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`.
- No añadir fallbacks cloud, telemetría ni conectores reales.
- El JSONL no guarda prompts ni el Markdown de las fuentes.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se lee el `.env` de la raíz; fuera del repositorio se admite un `.env` local creado desde `.env.example`.
- Las rutas relativas se resuelven contra la raíz de este laboratorio.
- Backend en `127.0.0.1:8014`. Frontend en `127.0.0.1:5175`.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Mantener una única ruta de ejecución fácil de explicar: fuentes → secuencial → fan-out → unión → JSONL.
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
uv run parallel-agents-demo
uv run parallel-agents-validate
```

Las pruebas usan dobles locales y no invocan Ollama. La demostración sí requiere el modelo configurado.

# Instrucciones de trabajo de 05-agent-loops

Estas reglas se aplican a todo este laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; al copiar el laboratorio, conservan sus límites esenciales.

## Objetivo y estado

- Este corte enseña un loop acotado: generar, puntuar, decidir, mejorar y conservar el mejor candidato.
- El gate de aprobado es una lista determinista de cinco assertions estructurales.
- El modelo no se aprueba a sí mismo. El código puntúa. El mejorador solo reescribe el prompt.
- Una corrección única de otro laboratorio no es este loop: aquí hay presupuesto, score por iteración y motivo de salida.
- No presentar LangGraph, OpenEvolve ni el CLI de `loop-engineering` como capacidades existentes.

## Separación y seguridad

- `backend/`, `frontend/`, `contracts/` y `examples/` son operativos; `docs/humano/` nunca es una dependencia del runtime.
- No importar código, bases de datos ni servicios de otro laboratorio.
- Toda escritura se limita a `.local/runs/` y `.local/artifacts/` dentro de este proyecto.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`.
- No añadir fallbacks cloud, telemetría ni conectores reales.
- El JSONL no guarda prompts ni la salida completa.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se lee el `.env` de la raíz; fuera del repositorio se admite un `.env` local creado desde `.env.example`.
- Las rutas relativas se resuelven contra la raíz de este laboratorio.
- Backend en `127.0.0.1:8015`. Frontend en `127.0.0.1:5176`.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Mantener una única ruta de ejecución fácil de explicar: tarea → prompt → score → presupuesto → JSONL.
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
uv run agent-loops-demo
uv run agent-loops-validate
```

Las pruebas usan dobles locales y no invocan Ollama. La demostración sí requiere el modelo configurado.

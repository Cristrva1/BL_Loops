# Instrucciones de trabajo de 13-sales-knowledge-curator

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; si el laboratorio se copia, este archivo conserva sus límites esenciales.

## Objetivo y estado

- Enseña a convertir una biblioteca débil en un `KnowledgeRelease` trazable: fuentes, afirmaciones, evidencia, conflictos y aprobación humana.
- El corte vertical de la fase 1 es local y determinista. La red, PDF/DOCX reales, Crawl4AI, CrewAI, ArchiveBox y Langfuse no están instalados.
- Ollama es opcional y queda detrás de un contrato: una salida malformada se rechaza, no se repara.
- No modificar `09-agentic-rag`. Un release se copia o importa a mano; nunca hay una llamada en vivo entre laboratorios.

## Separación

- `backend/`, `frontend/`, `contracts/` y `fixtures/` contienen archivos operativos.
- `docs/humano/` contiene enseñanza y nunca puede ser una dependencia del runtime.
- No importar código, bases, servicios o estado de otro laboratorio.
- Los artefactos viven en `.local/` dentro de este proyecto.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se usa el `.env` de la raíz; si se copia, se crea un `.env` local desde `.env.example`.
- `NETWORK_ENABLED=false` por defecto. No hay fallback cloud ni telemetría.
- Si `CURATOR_MODEL` está definido y no existe en Ollama, el extractor LLM debe fallar con un mensaje claro.

## Forma de trabajar

1. Revisar `git status --short` y preservar cambios existentes.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Construir el corte vertical más pequeño que enseñe la capacidad nueva.
4. Mantener contratos estrictos, permisos denegados por defecto y salidas dentro del laboratorio.
5. Actualizar la guía, arquitectura, metodología, ejercicios, diagnóstico o evaluación afectados.
6. Distinguir capacidad implementada, límite deliberado y trabajo futuro.
7. No modificar ni instalar dependencias en repositorios bajo `Repositorios_Prueba`.
8. No hacer commit, push o publicación salvo solicitud explícita.

## Verificación

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q backend/src backend/tests
npm --prefix frontend test
npm --prefix frontend run build
uv run sales-curator demo --fixture .\fixtures\corpus
uv run sales-curator validate --release <release_id>
uv run sales-curator export-run --run <run_id>
```

Si cambia la interfaz, verificar el recorrido real en navegador. El grafo no puede marcar `done` si el backend no emitió el estado correspondiente.

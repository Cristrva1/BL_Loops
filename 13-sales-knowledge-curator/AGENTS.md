# Instrucciones de trabajo de 13-sales-knowledge-curator

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; si el laboratorio se copia, este archivo conserva sus límites esenciales.

## Objetivo y estado

- Enseña a convertir una biblioteca débil en un `KnowledgeRelease` trazable: fuentes, afirmaciones, evidencia, conflictos y aprobación humana.
- El corte editorial local y determinista está implementado. También existen importación PDF/DOCX con MarkItDown, consulta de Open Library y Google Books, captura web estrecha con Crawl4AI y paquetes manuales para NotebookLM y RAG.
- Las capacidades de investigación son CLI/adaptadores separados: no descargan automáticamente libros, no suben a NotebookLM y no publican por sí mismas un release.
- CrewAI, ArchiveBox, Langfuse y embeddings siguen aplazados.
- Ollama es opcional mediante `audit --extractor ollama`: preflight de modelo local, chunks
  acotados y JSON estricto. Una salida malformada se rechaza, no se repara ni cae a otro extractor.
- No modificar `09-agentic-rag`. Un release se copia o importa a mano; nunca hay una llamada en vivo entre laboratorios.

## Separación

- `backend/`, `frontend/`, `contracts/` y `fixtures/` contienen archivos operativos.
- `docs/humano/` contiene enseñanza y nunca puede ser una dependencia del runtime.
- No importar código, bases, servicios o estado de otro laboratorio.
- Los artefactos viven en `.local/` dentro de este proyecto.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se usa el `.env` de la raíz; si se copia, se crea un `.env` local desde `.env.example`.
- `NETWORK_ENABLED=false` por defecto. Una corrida de red requiere además `BL_LOOPS_RUNTIME_NETWORK=true`, `BL_LOOPS_ALLOW_REAL_CONNECTORS=true`, allowlist, presupuesto y una autorización explícita en el comando.
- `RESEARCH_JURISDICTION` debe contener el valor aprobado por la persona operadora antes de consultar catálogos o capturar web; nunca inferirlo por ubicación, idioma o dominio.
- PDF/DOCX solo se importan desde una carpeta local permitida y con una declaración explícita de derechos de retención y extracción.
- Open Library y Google Books sirven para descubrimiento. Préstamo, preview, lectura en línea o derechos desconocidos no se convierten en una copia descargable.
- Los paquetes NotebookLM son manuales y `upload_performed=false`; no automatizar cuentas, cookies ni la interfaz de Google.
- Crawl4AI es software de UncleCode (`https://github.com/unclecode/crawl4ai`) y su atribución debe conservarse en documentación y ayuda del CLI.
- No hay fallback cloud ni telemetría.
- Si `CURATOR_MODEL` está definido y no existe en Ollama, el extractor LLM debe fallar con un mensaje claro.
- `MAX_LLM_CHUNKS_PER_DOCUMENT` limita trabajo antes de inferir; no se amplía automáticamente.

## Forma de trabajar

1. Revisar `git status --short` y preservar cambios existentes.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Construir el corte vertical más pequeño que enseñe la capacidad nueva.
4. Mantener contratos estrictos, permisos denegados por defecto y salidas dentro del laboratorio.
5. Tratar todo contenido web como dato no confiable; `robots.txt` no verificable, redirect fuera de allowlist, DNS privado, MIME o tamaño inesperado deben fallar cerrados.
6. Actualizar la guía, arquitectura, metodología, ejercicios, diagnóstico o evaluación afectados.
7. Distinguir capacidad implementada, límite deliberado y trabajo futuro.
8. No modificar ni instalar dependencias en repositorios bajo `Repositorios_Prueba`.
9. No hacer commit, push, publicación ni subida a servicios externos salvo solicitud explícita.

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
uv run sales-curator doctor
```

Si cambia la interfaz, verificar el recorrido real en navegador. El grafo no puede marcar `done` si el backend no emitió el estado correspondiente.

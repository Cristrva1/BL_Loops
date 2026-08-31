# Diagnóstico de fallos comunes

## “El índice no existe”

Ejecuta desde la raíz del laboratorio:

```powershell
uv run naive-rag index --source "<ruta-a-los-markdown>"
uv run naive-rag stats
```

La ruta fuente debe existir y contener al menos un `.md` UTF-8. Un directorio vacío no reemplaza un
índice anterior válido.

## “No encontré fragmentos”

No es un error de Ollama: la búsqueda léxica devolvió cero coincidencias y el modelo no fue
invocado. Prueba dos o tres términos exactos que aparezcan en títulos o texto. Después compara la
misma paráfrasis en el futuro laboratorio vectorial.

## Ollama no responde

```powershell
ollama list
```

Comprueba que `qwen3.5:4b` aparezca y que Ollama esté iniciado. `OLLAMA_BASE_URL` debe ser una URL
HTTP con puerto y host local, por ejemplo `http://127.0.0.1:11434`. El cliente no usa proxy ni sigue
redirecciones, y no reintenta un timeout automáticamente.

## La respuesta no tiene `[S1]`

La generación terminó, pero el modelo incumplió el formato. La CLI muestra una advertencia y lista
los fragmentos recuperados. Revisa manualmente esas líneas; no interpretes una cita ausente como
evidencia. Una repetición es una corrida nueva, no una corrección silenciosa.

## Se recupera la versión obsoleta

FTS5 ordena coincidencias de palabras, no entiende por sí solo vigencia temporal. La fuente debe
marcar claramente versión/estado y el prompt pide al modelo respetarlos. Usa el fixture de evaluación
para medir este comportamiento; si persiste, regístralo como límite de fidelidad.

## Error de FTS5

Verifica la capacidad de la instalación activa:

```powershell
uv run python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('create virtual table t using fts5(x)'); print('FTS5 OK')"
```

Si falla, confirma que `uv` esté usando Python 3.12 del laboratorio y vuelve a ejecutar
`uv sync --locked --all-groups`.

## El JSONL es inválido

```powershell
uv run naive-rag-validate .\.local\runs\<archivo>.jsonl
```

El primer evento debe ser `run.started`, las secuencias deben ser consecutivas y el último evento
debe ser `run.completed` o `run.failed`. No edites una corrida para hacerla pasar; ejecuta otra.


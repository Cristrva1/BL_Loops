# Inicio rápido en PowerShell

## 1. Preparar el entorno aislado

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\06-naive-rag
uv sync --locked --all-groups
```

Resultado esperado: `uv` usa Python 3.12 y crea únicamente `06-naive-rag\.venv`.

## 2. Importar los libros Markdown

```powershell
uv run naive-rag index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
```

El comando lee recursivamente archivos `.md`, omite duplicados byte a byte y reemplaza el índice
solo cuando la nueva proyección está completa. No modifica la carpeta de libros. Los PDF no se
procesan en esta variante.

Comprueba el resultado:

```powershell
uv run naive-rag stats
```

## 3. Hacer una pregunta

```powershell
uv run naive-rag ask "¿Qué explica SPIN Selling sobre la venta consultiva?"
```

La terminal muestra estados reales:

```text
[1/3 buscar] queued -> running -> done | ... fragmentos
[2/3 aumentar] running -> done | ... fuentes
[3/3 generar] waiting -> done | ... ms
Respuesta > ... [S1]
Fuentes recuperadas:
- [S1] ventas/SPIN_Selling.md:L...-L...
```

Una advertencia de citas significa que Ollama respondió, pero no respetó el contrato `[S#]`; las
fuentes se muestran igualmente para revisión humana.

## 4. Importar la corrida JSONL

```powershell
uv run naive-rag-validate
```

Resultado esperado: secuencia consecutiva, un solo `run_id` y evento terminal
`run.completed`. La traza contiene estados y métricas, no la pregunta ni la respuesta.

## 5. Probar la abstención

```powershell
uv run naive-rag ask "xilófono cuántico ultravioleta"
```

Si no hay coincidencias, el paso de generación queda `skipped`: Ollama no se invoca y el sistema
explica que no encontró fragmentos.


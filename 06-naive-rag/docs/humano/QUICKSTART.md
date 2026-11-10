# Inicio rápido en PowerShell

## 1. Preparar el entorno aislado

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\06-naive-rag
uv sync --locked --all-groups
```

Resultado esperado: `uv` usa Python 3.12 y crea únicamente `06-naive-rag\.venv`.

## 2. Empezar por el corpus sintético

```powershell
uv run naive-rag index --source .\fixtures\evaluation-corpus
uv run naive-rag search "¿Cuál es el plazo vigente para el primer seguimiento LUNA?"
```

Resultado esperado: `Indice listo: 5/5 documentos, 5 fragmentos` y una lista `[S1]…[S4]` encabezada
por `01-politica-vigente.md`. `search` no llama al modelo: muestra el contexto que recibiría. Los
cinco documentos están diseñados para enseñar una trampa de vigencia y otra léxica; el recorrido
completo está en [EXAMPLES.md](EXAMPLES.md).

## 3. Importar los libros Markdown

```powershell
uv run naive-rag index --source ..\docs\humano\Libros
```

El comando lee recursivamente archivos `.md`, omite duplicados byte a byte y reemplaza el índice
solo cuando la nueva proyección está completa. No modifica la carpeta de libros. Los PDF no se
procesan en esta variante.

Comprueba el resultado:

```powershell
uv run naive-rag stats
```

## 4. Hacer una pregunta

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

## 5. Importar la corrida JSONL

```powershell
uv run naive-rag-validate
```

Resultado esperado: secuencia consecutiva, un solo `run_id` y evento terminal
`run.completed`. La traza contiene estados y métricas, no la pregunta ni la respuesta.

## 6. Probar la abstención

```powershell
uv run naive-rag ask "xilófono cuántico ultravioleta"
```

Si no hay coincidencias, el paso de generación queda `skipped`: Ollama no se invoca y el sistema
explica que no encontró fragmentos.


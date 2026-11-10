# Inicio rápido

## Resultado esperado

Tendrás un índice híbrido local, compararás los tres modos de búsqueda con la misma paráfrasis y
validarás la traza JSONL de una respuesta citada.

## 1. Requisitos

```powershell
Set-Location .\07-vector-rag          # desde la raíz de BL_Loops
uv --version
ollama list                            # deben aparecer qwen3-embedding:latest y qwen3.5:4b
```

Si falta el modelo de embeddings y autorizas la descarga de sus pesos:

```powershell
ollama pull qwen3-embedding:latest
```

## 2. Entorno e índice del corpus sintético

```powershell
uv sync --locked --all-groups
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag stats
```

Resultado esperado: `Indice listo: 4/5 docs, 4 vectores, 2 secciones excluidas, 0 fuentes no
revisadas.` La ficha `04-ruido.md` queda vacía tras el filtro y no se indexa. Los cinco documentos
son pequeños: la indexación tarda segundos.

## 3. Índice del corpus de libros (opcional)

```powershell
uv run vector-rag index --source ..\docs\humano\Libros
uv run vector-rag stats
```

La primera indexación puede tardar porque crea un embedding local para cada fragmento. El progreso
aparece cada 10 %. El resultado se publica mediante reemplazo atómico: un fallo no deja medio índice.

## 4. Comparar recuperadores

Compara la misma paráfrasis:

```powershell
uv run vector-rag search --mode lexical "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode vector "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode hybrid "¿Cómo comprender sus prioridades sin lanzarme a vender?"
```

## 5. Generar una respuesta

Genera una respuesta con el modo predeterminado (híbrido):

```powershell
uv run vector-rag ask "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag-validate
```

Cada fuente muestra estado, posición léxica y similitud vectorial. `unreviewed` no significa falsa,
pero exige cautela; `generated` tampoco equivale a validación humana.

Si algo no coincide, el recorrido explicado está en [EXAMPLES.md](EXAMPLES.md) y los fallos comunes
en [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

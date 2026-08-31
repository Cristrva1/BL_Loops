# Inicio rápido

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\07-vector-rag
uv sync --locked --all-groups
uv run vector-rag index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
uv run vector-rag stats
```

La primera indexación puede tardar porque crea un embedding local para cada fragmento. El progreso
aparece cada 10 %. El resultado se publica mediante reemplazo atómico: un fallo no deja medio índice.

Compara la misma paráfrasis:

```powershell
uv run vector-rag search --mode lexical "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode vector "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode hybrid "¿Cómo comprender sus prioridades sin lanzarme a vender?"
```

Genera una respuesta con el modo predeterminado:

```powershell
uv run vector-rag ask "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag-validate
```

Cada fuente muestra estado, posición léxica y similitud vectorial. `unreviewed` no significa falsa,
pero exige cautela; `generated` tampoco equivale a validación humana.

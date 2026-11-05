# Inicio rápido en Windows 11

## Resultado esperado

Abrirás el dashboard, lanzarás el caso `I-LOOP-003` contra `qwen3.5:4b` y verás un score por iteración, el mejor candidato y un motivo de parada. Después importarás el JSONL.

## 1. Abrir el laboratorio

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\05-agent-loops
```

Todos los comandos siguientes se ejecutan desde esta carpeta.

## 2. Comprobar los requisitos

```powershell
uv --version
node --version
ollama --version
ollama list
```

En la última salida debe aparecer `qwen3.5:4b`. Si no está y autorizas la descarga:

```powershell
ollama pull qwen3.5:4b
```

## 3. Crear los entornos aislados

```powershell
uv sync --all-groups
npm --prefix frontend install
```

El resultado esperado es `05-agent-loops/.venv` y `frontend/node_modules`.

## 4. Probar las assertions sin modelo

```powershell
uv run agent-loops-score ".\examples\outputs\*"
```

Resultado esperado: `salida-debil.txt` con `checks=0/5`, `salida-parcial.json` con `checks=2/5` y
`salida-completa.json` con `checks=5/5`. Es la misma vara que usará el loop en cada iteración.

## 5. Arrancar API y dashboard

Terminal A:

```powershell
uv run uvicorn agent_loops.main:app --host 127.0.0.1 --port 8015 --reload
```

Terminal B:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5176`. Pulsa **Cargar caso I-LOOP-003** y **Lanzar loop**.

Qué debes ver:

- El nodo *Tarea y presupuesto* pasa a completado.
- *Generar* y *Puntuar* se activan en cada iteración.
- *Mejorar prompt* se salta si el umbral ya se alcanzó.
- El panel derecho muestra score inicial, mejor candidato y la ruta relativa del JSONL.

La primera llamada puede tardar mientras Ollama carga el modelo. El presupuesto de tres minutos cubre toda la corrida, no cada llamada.

## 6. Demostración CLI

Si prefieres no abrir el navegador:

```powershell
uv run agent-loops-demo
uv run agent-loops-validate
```

El resultado esperado comienza con `JSONL valido` e informa eventos, motivo de salida y scores.

## 7. Verificar el proyecto

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

Las pruebas usan dobles locales y no necesitan Ollama. El paso 4 o 5 es la demostración real.

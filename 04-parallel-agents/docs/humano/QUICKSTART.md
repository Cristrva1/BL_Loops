# Inicio rápido en Windows 11

## Resultado esperado

Abrirás el dashboard, lanzarás el caso `I-PARALLEL-002` contra `qwen3.5:4b` y verás una línea secuencial y un fan-out de tres fuentes. Después importarás el JSONL.

## 1. Abrir el laboratorio

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\04-parallel-agents
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

El resultado esperado es `04-parallel-agents/.venv` y `frontend/node_modules`.

## 4. Arrancar API y dashboard

Terminal A:

```powershell
uv run uvicorn parallel_agents.main:app --host 127.0.0.1 --port 8014 --reload
```

Terminal B:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5175`. Pulsa **Cargar caso I-PARALLEL-002** y **Lanzar experimento**.

Qué debes ver:

- El nodo *Tarea* pasa a completado.
- *Secuencial A → B → C* se encienden uno detrás de otro.
- *Paralelo A, B y C* pasan a `queued` y pueden coincidir en `running` o `waiting`.
- *Unión paralela* espera a las tres. Una fallida no aparece como completa.
- El panel derecho muestra tiempos, overlap y la ruta relativa del JSONL.

La primera llamada puede tardar mientras Ollama carga el modelo. Un único modelo puede serializar las tres peticiones; el laboratorio registra el tiempo real, no un speedup teórico.

## 5. Demostración CLI

Si prefieres no abrir el navegador:

```powershell
uv run parallel-agents-demo
uv run parallel-agents-validate
```

El resultado esperado comienza con `JSONL valido` e informa eventos, evento terminal y `run_id`.

## 6. Verificar el proyecto

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

Las pruebas usan dobles locales y no necesitan Ollama. El paso 4 o 5 es la demostración real.

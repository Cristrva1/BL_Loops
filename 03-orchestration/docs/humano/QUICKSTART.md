# Inicio rápido en Windows 11

## Resultado esperado

Abrirás el dashboard, lanzarás el caso `I-ORCH-001` contra `qwen3.5:4b` y verás dos variantes puntuadas con la misma lista de checks. Después importarás el JSONL.

## 1. Abrir el laboratorio

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\03-orchestration
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

El resultado esperado es `03-orchestration/.venv` y `frontend/node_modules`.

## 4. Probar el gate sin modelo

```powershell
uv run orchestration-score ".\examples\guides\*.md"
```

Resultado esperado: `guia-aprobada.md` con `checks=9/9`, `guia-con-fallos.md` con `checks=7/9` y
`poema-fuera-de-caso.md` con `checks=1/9`. Así conoces la vara de medir antes de llamar al modelo.

## 5. Arrancar API y dashboard

Terminal A:

```powershell
uv run uvicorn orchestration.main:app --host 127.0.0.1 --port 8012 --reload
```

Terminal B:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5172`. Pulsa **Cargar caso I-ORCH-001** y **Lanzar experimento**.

Qué debes ver:

- El nodo *Tarea* pasa a completado.
- *Agente único* y *Planificador* se activan en secuencia, no a la vez.
- *Corrección* permanece inactiva si el gate ya aprobó el primer borrador.
- El panel derecho muestra checks y la ruta relativa del JSONL.

La primera llamada puede tardar mientras Ollama carga el modelo. No hay reintento automático.

## 6. Demostración CLI

Si prefieres no abrir el navegador:

```powershell
uv run orchestration-demo
uv run orchestration-validate
```

El resultado esperado comienza con `JSONL valido` e informa eventos, evento terminal y `run_id`.

## 7. Verificar el proyecto

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

Las pruebas usan dobles locales y no necesitan Ollama. El paso 4 o 5 es la demostración real.

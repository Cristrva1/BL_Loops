# Quickstart explicado

Todos los comandos se ejecutan en PowerShell. No copies `.env` reales ni imprimas secretos.

## 1. Entrar y crear el entorno aislado

```powershell
cd C:\Users\criss\Desktop\Claude\BL_Loops\13-sales-knowledge-curator
uv sync --all-groups
npm --prefix frontend install
```

Resultado esperado: `.venv`, `uv.lock`, `package-lock.json` y `node_modules` pertenecen únicamente a este laboratorio.

## 2. Demostración reproducible

```powershell
uv run sales-curator demo --fixture .\fixtures\corpus --reviewer operador-local --reason "Aprobacion didactica del operador"
```

Resultado esperado:

- `state=published`
- al menos un hueco (`after-sales`), un duplicado sindicado, una afirmación obsoleta y un conflicto de precio
- un `release_id` y una ruta JSONL
- las afirmaciones disputadas, inyectadas o sin evidencia **no** salen en el paquete publicado

El operador de la demo es la persona que ejecuta el comando, no el modelo.

## 3. Validar el release y la corrida

Copia el `release_id` y el `run_id` impresos y ejecuta:

```powershell
uv run sales-curator validate --release <release_id>
uv run sales-curator export-run --run <run_id>
```

El validador comprueba hashes, ausencia de PII/secretos y que el conocimiento no incluya claims no aprobados. El JSONL debe empezar por `run.started` y terminar en `run.completed`.

## 4. Abrir el dashboard

Terminal 1:

```powershell
uv run uvicorn sales_curator.api.main:app --host 127.0.0.1 --port 8013 --reload
```

Terminal 2:

```powershell
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5174`. Pulsa **Auditar fixtures**. El grafo debe pasar a `review_pending`. Aprueba hashes visibles y construye el release. Si el backend no corre, la interfaz lo dice: no inventa actividad.

## 5. Comprobar que la red sigue apagada

En `/api/health` debe verse `"network_enabled": false`. Una pregunta de postventa queda como rama inconclusa, no como silencio.

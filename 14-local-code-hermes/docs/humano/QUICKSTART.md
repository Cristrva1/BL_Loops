# Inicio rápido en Windows 11

## Resultado esperado

Validarás el laboratorio sin inferencia, producirás un diagnóstico real de solo lectura y, si el host está autorizado, ejecutarás una única corrida aislada. Si faltan recursos, modelo, evidencia o un worktree limpio, el resultado correcto es `run.blocked`.

## 1. Preparar el entorno propio

```powershell
Set-Location .\14-local-code-hermes
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

El laboratorio conserva su propio `.venv`; estas pruebas no invocan servicios reales.

## 2. Diagnosticar el host

```powershell
uv run hermes-preflight --mode exploratory
$LASTEXITCODE
```

`0` significa que los checks terminaron sin bloqueo; `2` indica prerrequisitos faltantes; `1` indica configuración inválida o fallo interno. El modo exploratorio puede dejar warnings de red, perfil o Git y nunca produce una corrida comparable.

## 3. Referenciar evidencia formal

Después de cerrar/liberar LM Studio, aplicar el perfil autorizado de Ollama y capturar evidencia real de firewall/perfil:

```powershell
uv run hermes-preflight --mode formal `
  --network-proof firewall-authorized --firewall-proof-id FW-LOCAL-20260830 `
  --server-profile-proof operator-authorized --server-profile-proof-id OLLAMA-PROFILE-20260830
```

Los IDs deben corresponder a evidencia existente. El JSONL guarda únicamente hashes de referencia; no los valores sensibles.

## 4. Validar cualquier corrida

```powershell
$runFile = Get-ChildItem .local\runs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

El archivo es UTF-8, compacto, termina en newline y no contiene stdout, stderr, prompts ni respuestas.

## 5. Preparar el fixture

```powershell
uv run hermes-fixture-verify prepare practica-001
uv run hermes-fixture-verify verify practica-001
```

El primer comando copia `B-CODE-003` a `.local/workspaces/`. La verificación inicial falla intencionalmente porque el proyecto aún tiene el defecto de frontera.

## 6. Ejecutar Hermes en Docker

El operador debe confirmar antes que `lms ps --json` devuelva una lista vacía, que Ollama esté en loopback con el alias creado y que Docker responda. La imagen `nikolaik/python-nodejs:python3.11-nodejs20` debe existir localmente.

```powershell
uv run hermes-benchmark --execute
```

El runner crea una configuración temporal bajo `.local/`, selecciona explícitamente `provider: custom`, usa `/v1` de Ollama, monta solo el workspace en `/workspace` y desactiva la red del contenedor. No usa el proveedor Hermes configurado por el usuario ni hace fallback a nube.

Si el checkout está sucio por la tanda de desarrollo, el único override disponible es explícito y no puntuable:

```powershell
uv run hermes-benchmark --execute --allow-dirty-worktree
```

Ese flag no convierte `git.head` en verde; el JSONL conserva `dirty_worktree_override=true` y `scored=false`.

## 7. Revisar el resultado

```powershell
$runFile = Get-ChildItem .local\runs\benchmark-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

`run.completed` solo significa que el proceso terminó; el score oficial requiere contexto efectivo, GPU, logs sin truncación/HTTP 500, fixture correcto, cero egress independiente y repeticiones comparables.

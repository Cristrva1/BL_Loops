# Inicio rápido en Windows 11

## Resultado esperado

Validarás el laboratorio sin inferencia y producirás un diagnóstico real de solo lectura. Si faltan modelo, recursos, `HEAD` o evidencias autorizadas, el resultado esperado es `run.blocked`, no un falso aprobado.

## 1. Abrir el laboratorio

```powershell
# Desde la raíz de BL_Loops
Set-Location .\14-local-code-hermes
```

Si copiaste el laboratorio, abre PowerShell en su carpeta y omite `Set-Location`.

## 2. Crear el entorno aislado

```powershell
uv sync --locked --all-groups
```

Se crea `.venv` solo para este laboratorio.

## 3. Ejecutar el gate hermético

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

No se invocan servicios reales.

## 4. Diagnosticar el host sin modificarlo

```powershell
uv run hermes-preflight --mode exploratory
$LASTEXITCODE
```

Códigos:

- `0`: todos los checks iniciales pasaron.
- `2`: el gate quedó bloqueado por uno o más prerrequisitos.
- `1`: configuración inválida o fallo interno.

El modo exploratorio permite warnings por evidencia de red, perfil del servidor o `HEAD`, pero siempre exporta `comparable=false`.

Solo después de obtener y custodiar evidencia real, el modo formal referencia sus IDs así:

```powershell
uv run hermes-preflight --mode formal `
  --network-proof firewall-authorized --firewall-proof-id FW-LOCAL-001 `
  --server-profile-proof operator-authorized --server-profile-proof-id OLLAMA-PROFILE-001
```

Los IDs de ejemplo no son evidencia. Sustitúyelos únicamente por referencias autorizadas; el
programa no carga `.env.example`, no crea la evidencia y no configura el host.

## 5. Validar la exportación

```powershell
$runFile = Get-ChildItem .local\runs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

El archivo debe terminar en `run.completed`, `run.blocked` o `run.failed`, sin stdout, prompts ni secretos.

## 6. Preparar el fixture sintético

```powershell
uv run hermes-fixture-verify prepare practica-001
```

Esto copia `B-CODE-003` a `.local/workspaces/practica-001`. No inicia Hermes. El proyecto contiene un error de borde intencional y una prueba que ya lo demuestra.

## Preparación futura, solo con autorización

Cuando haya terminado toda sesión activa y exista VRAM suficiente, el operador podrá crear el alias local:

```powershell
ollama create local-code-9b-64k -f .\Modelfile
```

Las variables `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1` y `OLLAMA_NO_CLOUD=1` deben aplicarse al proceso servidor de Ollama y verificarse por evidencia independiente. Este laboratorio no las cambia ni reinicia el servidor.

No ejecutes Ollama y LM Studio con modelos cargados al mismo tiempo durante el benchmark.

# 14-local-code-hermes

Laboratorio didáctico para preparar y ejecutar una corrida controlada de Hermes contra Ollama local. El corte incluye el preflight, el alias `local-code-9b-64k`, un sandbox Docker sin red, la reparación del fixture `B-CODE-003` y la exportación JSONL sanitaria.

## Qué existe

```text
preflight formal
  -> diez gates + evidencia de firewall/perfil + estado Git
  -> JSONL F-LOCAL-CODE-004 (no puntuado)

benchmark autorizado
  -> Hermes -z + Ollama loopback
  -> Docker por sesión, solo workspace, --network=none
  -> tests unitarios, semánticos y de mutación
  -> JSONL B-CODE-003 (una corrida; no comparable todavía)
```

La corrida viva requiere `--execute`. `--allow-dirty-worktree` solo habilita un smoke de desarrollo explícito; conserva el bloqueo de Git en la evidencia y fuerza `scored=false` y `comparable=false`. No hay fallback cloud silencioso.

## Verificación hermética

Desde PowerShell:

```powershell
Set-Location .\14-local-code-hermes
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Estas pruebas no llaman a Ollama, Hermes, LM Studio ni internet.

## Preflight

```powershell
uv run hermes-preflight --mode exploratory
$runFile = Get-ChildItem .local\runs\preflight-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

El modo formal exige referencias previamente autorizadas:

```powershell
uv run hermes-preflight --mode formal `
  --network-proof firewall-authorized --firewall-proof-id FW-LOCAL-20260830 `
  --server-profile-proof operator-authorized --server-profile-proof-id OLLAMA-PROFILE-20260830
```

Los IDs solo son referencias; la evidencia real se obtiene fuera del JSONL y nunca se imprimen secretos.

## Corrida viva controlada

Después de verificar que LM Studio no tiene modelos cargados, que Ollama está configurado y que Docker está disponible:

```powershell
uv run hermes-benchmark --execute --allow-dirty-worktree
$runFile = Get-ChildItem .local\runs\benchmark-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

El flag de worktree sucio es deliberado para este checkout de desarrollo y no convierte la corrida en release. Para una corrida puntuable, el preflight debe terminar `run.completed` con worktree limpio y se requieren las repeticiones/cohortes definidas en `docs/humano/EVALUATION.md`.

## Organización

- `src/local_code_hermes/`: configuración, preflight, runner, sandbox, benchmark y validadores.
- `cases/B-CODE-003/`: proyecto sintético congelado, sin PII.
- `contracts/`: schemas estructurales de preflight y benchmark, ambos en versión `1.1`.
- `tests/`: pruebas deterministas con dobles.
- `docs/humano/`: explicación, práctica, diagnóstico y evaluación.
- `.local/`: corridas, uso y workspaces ignorados por Git.

> Estado: preflight y harness de una corrida implementados. La comparación entre clientes, el score oficial y la prueba independiente de cero egress siguen siendo fases posteriores.

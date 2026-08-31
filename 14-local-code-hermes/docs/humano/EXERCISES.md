# Ejercicios

## Básico — leer una corrida bloqueada

1. Ejecuta el preflight exploratorio.
2. Valida el JSONL.
3. Cuenta nodos `passed`, `warning` y `blocked`.
4. Explica por qué un terminal `run.blocked` puede significar que el programa funcionó correctamente.

**Aprobado:** distingues un bloqueo de prerrequisitos de un fallo interno.

## Intermedio — probar una frontera sin servicios

1. Copia el fixture con un identificador nuevo.
2. Ejecuta el verificador y observa que falla.
3. Cambia solo la condición que rechaza 100 % y añade `test_discount_above_100_is_rejected`.
4. Ejecuta de nuevo el verificador.

**Aprobado:** solo cambian `src/pricing.py` y `tests/test_pricing.py`, las cuatro pruebas pasan y 101 % sigue rechazado.

## Avanzado — razonar sobre el sandbox

1. Ejecuta `uv run pytest tests/test_benchmark.py`.
2. Localiza `--network=none`, `--cap-drop=ALL`, `no-new-privileges` y el único mount.
3. Explica por qué Docker protege los comandos del agente, pero no convierte por sí solo al proceso padre en evidencia de firewall.
4. Explica por qué `--allow-dirty-worktree` no debe producir un score.

**Aprobado:** puedes distinguir aislamiento de comandos, inferencia local y cero egress del host.

## Experimento controlado — una corrida Hermes

Con el operador autorizado y el host preparado:

```powershell
uv run hermes-benchmark --execute --allow-dirty-worktree
$runFile = Get-ChildItem .local\runs\benchmark-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

Revisa el workspace generado, los conteos de uso y el delta de logs. No copies respuestas al reporte ni declares score si `comparable=false`.

## Diseño posterior — A/B de runtime

Solo después de completar una cohorte Ollama, diseña el mismo caso con LM Studio. Mantén modelo, cuantización, contexto, SHA y permisos; nunca cargues ambos runtimes simultáneamente. OpenCode y Claude Code siguen siendo laboratorios independientes.

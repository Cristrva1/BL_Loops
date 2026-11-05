# Ejercicios

Los tres primeros funcionan sin Ollama, Hermes ni Docker. Cada uno tiene una solución plegada; los
recorridos con salidas reales están en [EXAMPLES.md](EXAMPLES.md).

## Básico — leer una corrida bloqueada

1. Ejecuta el preflight exploratorio.
2. Valida el JSONL.
3. Cuenta nodos `passed`, `warning` y `blocked`.
4. Explica por qué un terminal `run.blocked` puede significar que el programa funcionó correctamente.

**Aprobado:** distingues un bloqueo de prerrequisitos de un fallo interno.

<details>
<summary>Solución</summary>

En una máquina sin Ollama ni Hermes (ver el [ejemplo 1](EXAMPLES.md#ejemplo-1--preflight-en-una-máquina-incompleta))
pasan `python.runtime` y `network.endpoint`, quedan en aviso exploratorio el firewall y el perfil del
servidor, y fallan cerrados el modelo, Hermes, LM Studio, Git y los recursos. `run.blocked` es la
conclusión correcta: el programa hizo su trabajo, que era **no** autorizar una corrida sin evidencia.
Un fallo interno, en cambio, terminaría con un error del propio harness y sin la secuencia completa de
gates.
</details>

## Intermedio — probar una frontera sin servicios

1. Copia el fixture con un identificador nuevo.
2. Ejecuta el verificador y observa que falla.
3. Cambia solo la condición que rechaza 100 % y añade `test_discount_above_100_is_rejected`.
4. Ejecuta de nuevo el verificador.

En comandos:

```powershell
uv run hermes-fixture-verify prepare mi-intento
uv run hermes-fixture-verify verify mi-intento
```

El workspace queda en `.local/workspaces/mi-intento/`.

**Aprobado:** solo cambian `src/pricing.py` y `tests/test_pricing.py`, las cuatro pruebas pasan y 101 % sigue rechazado.

<details>
<summary>Solución</summary>

El [ejemplo 3](EXAMPLES.md#ejemplo-3--la-reparación-correcta) muestra los dos cambios: `>= 100` pasa a
`> 100` y se añade `test_discount_above_100_is_rejected`. El verificador responde
`Fixture aprobado; archivos permitidos y pruebas verificadas.` Si solo cambias el código sin añadir la
prueba, sigue fallando `required_tests_missing`; si la prueba nueva no detecta un mutante, falla
`test_quality_check_failed`.
</details>

## Avanzado — razonar sobre el sandbox

1. Ejecuta `uv run pytest tests/test_benchmark.py`.
2. Localiza `--network=none`, `--cap-drop=ALL`, `no-new-privileges` y el único mount.
3. Explica por qué Docker protege los comandos del agente, pero no convierte por sí solo al proceso padre en evidencia de firewall.
4. Explica por qué `--allow-dirty-worktree` no debe producir un score.

**Aprobado:** puedes distinguir aislamiento de comandos, inferencia local y cero egress del host.

<details>
<summary>Solución</summary>

- **Inferencia local:** las peticiones de lenguaje van a Ollama en loopback.
- **Aislamiento de comandos:** lo que el agente ejecuta corre en Docker con `--network=none`,
  `--cap-drop=ALL`, `no-new-privileges` y un único mount del workspace.
- **Cero egress del host:** exige evidencia de red independiente (firewall o captura) sobre Hermes y
  su árbol de procesos, que corren **fuera** del contenedor. Docker no la aporta.

`--allow-dirty-worktree` permite un smoke con cambios sin confirmar: el punto de partida no es un SHA
reproducible, así que la corrida queda `scored=false` y `comparable=false`.
</details>

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

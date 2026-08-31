# Evaluación

## Fase 1: F-LOCAL-CODE-004@0.1.0

El preflight comprueba Python 3.12, endpoint loopback, referencias formales de firewall y perfil Ollama, identidad del alias, versión de Hermes, LM Studio, SHA exacto, worktree limpio, RAM/commit y VRAM.

Sus terminales son `run.completed`, `run.blocked` y `run.failed`; nunca puntúa ni compara.

## Fase 2: B-CODE-003@0.1.0

El runner crea una copia aislada del fixture, fuerza Hermes `provider: custom` hacia Ollama local y ejecuta los comandos del agente con Docker sin red. Después verifica:

- cambios únicamente en `src/pricing.py` y `tests/test_pricing.py`;
- cuatro pruebas requeridas, fronteras 0/25/100 y negativos/mayores a 100;
- ejecución unitaria, semántica oculta y comprobación por mutación;
- digest común del alias y modelo fuente;
- `ollama ps` con alias, `100% GPU` y contexto efectivo 65,536;
- delta de logs sin `truncating input prompt` ni HTTP 500;
- uso normalizado de Hermes sin persistir respuesta, prompt, stdout o stderr.

El JSONL conserva conteos y estados, no contenido. Una salida `run.completed` indica que el proceso terminó; `scored=false` y `comparable=false` siguen siendo obligatorios para esta corrida única y para cualquier smoke con worktree sucio.

## Criterio de corrida oficial

Para puntuar se requiere todo lo anterior, worktree limpio, evidencia contemporánea de inferencia local y cero egress, y tres corridas válidas por cliente. La comparación exige el mismo SHA, fixture, permisos, modelo, digest, contexto, hardware y cohorte. Un warning, un `SKIPPED`, una evidencia de otro SHA o una salida sin terminal validado invalida la comparación.

## Métricas exportadas

El benchmark registra duración, contadores de entrada/salida/total/API, residencia y contexto observados, conteos de truncación/HTTP 500, estado del fixture y estado del sandbox. El score oficial queda fuera hasta que la evidencia de red y las repeticiones lo permitan.

## Verificación

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run hermes-run-validate <ruta-jsonl>
```

Para importar en el comparador central se entrega únicamente el JSONL validado; el comparador no consulta laboratorios en vivo.

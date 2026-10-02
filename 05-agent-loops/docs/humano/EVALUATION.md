# Evaluación del loop A0

## Caso base

**ID:** `I-LOOP-003@0.1.0`  
**Entrada:** `examples/i-loop-003.json`

Tarea: mejorar un prompt para que una salida cumpla cinco assertions estructurales. Presupuesto: cinco iteraciones, dos errores o tres minutos.

## Ejecutar

```powershell
uv run agent-loops-demo
uv run agent-loops-validate
```

O el recorrido visual de [QUICKSTART.md](QUICKSTART.md). Realiza una ronda de calentamiento no puntuada y luego tres corridas nuevas si vas a comparar modelos.

## Criterios de aprobado

- Guarda score inicial y por iteración.
- Conserva el mejor candidato, no necesariamente el último.
- Se detiene al alcanzar el umbral o agotar presupuesto.
- Explica el motivo de salida (`threshold_reached`, `max_iterations`, `max_errors` o `timeout`).
- Declara objetivo, presupuesto, condición de mejora y condición de parada.
- El grafo refleja eventos reales.
- El JSONL se reimporta y no contiene el prompt ni la salida completa.
- No hay fallback cloud, ni escrituras fuera de `.local/`, ni reintentos ocultos.

## Qué verifican las pruebas

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

La suite cubre configuración local, parseo JSON, scoring, motor del loop con dobles, API, contrato de Ollama, JSONL e independencia de otros laboratorios y de `docs/humano/`.

## Métricas disponibles

| Métrica | Fuente | Significado |
|---|---|---|
| `initial_score` | primera iteración | punto de partida del prompt débil |
| `best_known_score` | motor | máximo checks_passed visto |
| `checks_passed` / `checks_total` | `scoring.py` | cumplimiento del caso |
| `stop_reason` | motor | por qué paró el ciclo |
| `iteration` | `iteration.recorded` | vuelta actual |
| `wall_duration_ms` | reloj monotónico | tiempo de cada llamada |
| `prompt_tokens` / `output_tokens` | Ollama | costo de tokens |

No se calcula un score normalizado de eficiencia sin una cohorte comparable. Un solo laboratorio no afirma que “hacer más vueltas siempre gana”.

## Exportación e importación

Cada experimento crea `.local/runs/*.jsonl` conforme a `contracts/run-event.schema.json`. `agent-loops-validate` simula la importación futura al comparador central.

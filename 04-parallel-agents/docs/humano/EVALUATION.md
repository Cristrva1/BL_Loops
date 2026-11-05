# Evaluación del fan-out A

## Caso base

**ID:** `I-PARALLEL-002@0.1.0`  
**Entrada:** `examples/i-parallel-002.json`  
**Fuentes:** `examples/sources/source-a-precios.md`, `source-b-horario.md`, `source-c-garantia.md`

Tarea: extraer hechos de tres documentos independientes y crear una tabla consolidada. Obligatorio comparar la línea secuencial con el fan-out.

## Ejecutar

```powershell
uv run parallel-agents-demo
uv run parallel-agents-validate
```

O el recorrido visual de [QUICKSTART.md](QUICKSTART.md). Realiza una ronda de calentamiento no puntuada y luego tres corridas nuevas si vas a comparar modelos.

## Criterios de aprobado

- Tres ramas pueden ejecutarse concurrentemente (`max_in_flight` hasta 3).
- Cada rama mantiene su propia procedencia (`source_id`).
- El agregador espera resultados o timeouts explícitos.
- Una rama fallida no se presenta como completa ni aporta filas a la tabla.
- Se miden `wall_ms` secuencial y paralelo.
- El grafo refleja eventos reales.
- El JSONL se reimporta y no contiene documentos ni prompts.
- No hay fallback cloud, ni escrituras fuera de `.local/`, ni reintentos ocultos.

## Qué verifican las pruebas

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

La suite cubre configuración local, parseo JSON, scoring, overlap con dobles, timeout de rama, API, contrato de Ollama, JSONL e independencia de otros laboratorios y de `docs/humano/`.

También comprueba que el evento terminal nunca se publica antes que el resultado, ni en el snapshot ni en el stream SSE.

## Métricas disponibles

| Métrica | Fuente | Significado |
|---|---|---|
| `completed_sources` | agregador | fuentes que aportan filas |
| `failed_sources` | agregador | timeout o JSON inválido |
| `wall_ms` | reloj monotónico | tiempo de cada variante |
| `speedup` | comparación | secuencial / paralelo |
| `overlap_observed` | semáforo | dos o más ramas a la vez |
| `max_in_flight` | settings | tope de concurrencia |
| `winner` | comparación | sequential, parallel, tie o incomplete |

No se afirma que “el paralelo siempre gana”. Un modelo compartido puede serializar.

## Exportación e importación

Cada experimento crea `.local/runs/*.jsonl` conforme a `contracts/run-event.schema.json`. `parallel-agents-validate` simula la importación futura al comparador central.

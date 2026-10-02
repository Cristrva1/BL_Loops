# Evaluación de la orquestación A0

## Caso base

**ID:** `I-ORCH-001@0.1.0`  
**Entrada:** `examples/i-orch-001.json`

Tarea: producir una guía breve para ejecutar un agente local. Roles mínimos: planificador, autor y revisor. Obligatorio comparar contra un agente único.

## Ejecutar

```powershell
uv run orchestration-demo
uv run orchestration-validate
```

O el recorrido visual de [QUICKSTART.md](QUICKSTART.md). Realiza una ronda de calentamiento no puntuada y luego tres corridas nuevas si vas a comparar modelos.

## Criterios de aprobado

- Cada handoff del planificador es un `Plan` JSON válido.
- El revisor modelo, si responde, usa el schema `Review`.
- El gate determinista comprueba headings, Ollama, PowerShell, parada, extensión y ausencia de marcas cloud.
- Si el gate falla, hay como máximo una corrección.
- La línea base usa la misma tarea y la misma lista.
- El grafo refleja eventos reales.
- El JSONL se reimporta y no contiene el Markdown completo ni prompts.
- No hay fallback cloud, ni escrituras fuera de `.local/`, ni reintentos ocultos.

## Qué verifican las pruebas

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

La suite cubre configuración local, parseo JSON, scoring, orquestador con dobles, API, contrato de Ollama, JSONL e independencia de otros laboratorios y de `docs/humano/`.

## Métricas disponibles

| Métrica | Fuente | Significado |
|---|---|---|
| `checks_passed` / `checks_total` | `scoring.py` | cumplimiento del caso |
| `passed` | todos los checks | gate binario |
| `revision_used` | orquestador | si hubo corrección única |
| `llm_review_passed` | JSON del revisor | opinión del modelo, no el gate |
| `wall_duration_ms` | reloj monotónico | tiempo de cada llamada |
| `prompt_tokens` / `output_tokens` | Ollama | costo de tokens |
| `winner` | comparación | baseline, orchestrated, tie o incomplete |

No se calcula un score normalizado de eficiencia sin una cohorte comparable. Un solo laboratorio no afirma que “orquestar siempre gana”.

## Exportación e importación

Cada experimento crea `.local/runs/*.jsonl` conforme a `contracts/run-event.schema.json`. `orchestration-validate` simula la importación futura al comparador central.

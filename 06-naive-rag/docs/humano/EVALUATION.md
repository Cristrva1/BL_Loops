# Evaluación del RAG léxico

## Caso base

**ID:** `I-RAG-NAIVE-004@0.1.0`  
**Corpus:** cinco Markdown sintéticos en `fixtures/evaluation-corpus/`.

Pregunta:

```text
¿Cuál es el plazo vigente de seguimiento LUNA y qué dato debe confirmarse antes de enviar una propuesta?
```

La respuesta comprobable combina dos fuentes: 24 horas en la política vigente y presupuesto en el
documento de calificación. Existe una política de 72 horas marcada como obsoleta y un distractor con
otro significado de “luna”.

## Ejecutar

```powershell
uv run naive-rag index --source .\fixtures\evaluation-corpus
uv run naive-rag ask "¿Cuál es el plazo vigente de seguimiento LUNA y qué dato debe confirmarse antes de enviar una propuesta?"
uv run naive-rag-validate
```

Realiza una ronda de calentamiento no puntuada y luego tres corridas nuevas con la misma entrada si
vas a comparar modelos.

## Criterios de aprobado

- Solo usa fragmentos del corpus sintético.
- Indica 24 horas, no 72, y distingue la versión vigente de la obsoleta.
- Indica que debe confirmarse el presupuesto.
- Cada afirmación verificable lleva una cita `[S#]` existente.
- Las rutas y líneas mostradas contienen la evidencia citada.
- No usa el documento distractor como regla comercial.
- La traza termina, se reimporta y no contiene la pregunta ni respuesta crudas.
- No invoca cloud, no escribe fuera del laboratorio y no realiza reintentos ocultos.

## Qué verifican las pruebas

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

La suite cubre configuración local, rutas confinadas, proyección exacta, preservación ante una fuente
vacía, deduplicación, líneas citables, puntuación segura, abstención, contrato de Ollama, falta de
citas, sanitización JSONL e independencia de otros laboratorios y de la documentación humana.

## Métricas disponibles

| Métrica | Fuente | Significado |
|---|---|---|
| `wall_duration_ms` | reloj monotónico | tiempo de recuperación o generación |
| `ollama_duration_ms` | Ollama | duración interna reportada |
| `prompt_tokens` | Ollama | tokens enviados al modelo |
| `output_tokens` | Ollama | tokens generados |
| `matches` / `sources` | FTS5 y pipeline | cantidad de evidencia recuperada |
| `context_chars` | construcción local | tamaño del contexto textual |
| `citation_valid` | validador local | existencia de al menos una cita y ausencia de IDs desconocidos |

No se calcula todavía un score normalizado sin una cohorte comparable. La fidelidad semántica exige
comprobar el contenido citado; `citation_valid=true` solo valida IDs.

## Exportación e importación

Cada pregunta crea `.local/runs/*.jsonl` conforme a `contracts/run-event.schema.json`. El archivo
incluye nodos, estados, conteos, tiempos y tokens, pero no texto crudo. `naive-rag-validate` simula la
importación futura al comparador central.


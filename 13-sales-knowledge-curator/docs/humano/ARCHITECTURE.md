# Arquitectura

El runtime, no el LLM, controla permisos, presupuestos, transiciones y publicación.

## Nodos visibles

| Nodo | Qué hace | Qué no puede hacer |
|---|---|---|
| Ingesta | Lee Markdown/TXT, calcula hash, cuarentena | Modificar la fuente |
| Registro | Deduplica y conserva `origin_source_id` | Declarar verdad por reputación |
| Investigación | Planea huecos; local sí, web no | Abrir la red |
| Extracción | Bloques `CLAIM` deterministas | Fusionar afirmaciones incompatibles |
| Verificación | Cita, fecha, sindicación, conflicto | Aprobar por confianza del modelo |
| Revisión | Persona + hash exacto | `--approve=true` |
| Staging / gate | Paquete reproducible | Publicar si el hash cambió |
| Release | Reemplazo atómico de `current.json` | Borrar el release anterior |

## Estados

```text
scope_draft → inventory_running → gaps_ready → research_planned
  → awaiting_external_authorization | collecting_local
  → sources_normalized → claims_extracted → verification_running
  → conflicts_open | review_pending
  → approved → staging → validating → published | failed
```

## Contratos

La unidad central es `ClaimRecord`. Cada afirmación publicable necesita localizador, derechos, fecha o razón de su ausencia, y aprobación humana contemporánea. `corroborated` no equivale a `human_approved`. Tres copias sindicadas cuentan como una cadena.

Las dimensiones `authority`, `evidence_proximity`, `recency`, `independence`, `applicability`, `extraction_integrity` y `rights_clarity` van de 0 a 4. No existe un `truth_score` que publique.

## Persistencia

- SQLite: `.local/data/curator.sqlite`
- Staging: `.local/data/staging/<run_id>/`
- Releases: `.local/data/releases/<release_id>/` más `current.json`
- JSONL: `.local/runs/<run_id>.jsonl`

Si el staging falla, `current.json` no se toca.

## Límites de este corte

- Sin web real, PDF/DOCX, embeddings, CrewAI ni escritura hacia otros laboratorios.
- El extractor Ollama existe como contrato (`parse_candidates`) y rechaza JSON inválido.
- El adaptador de red lanza `NetworkDisabled` aunque alguien active la bandera: no hay crawler instalado.

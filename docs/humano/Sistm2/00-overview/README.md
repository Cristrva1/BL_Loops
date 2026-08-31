# Orquestación Auto-Mejorante — Índice de documentación

> **Status**: `draft` | Última revisión: 2026-05-07 | Dueño: Christian

Sistema central modular al que se le agregan progresivamente agentes de IA (herramientas, subsistemas, utilidades) que él mismo coordina, registra y con los que aprende.

---

## Mapa de lectura recomendado

### Para entender QUÉ es el sistema
1. [`00-overview/system-context.md`](./system-context.md) — diagrama C4 nivel 1 (el sistema y sus usuarios externos)
2. [`10-architecture/rings-topology.md`](../10-architecture/rings-topology.md) — geometría de 3 anillos
3. [`10-architecture/three-flows.md`](../10-architecture/three-flows.md) — los 3 flujos cardinales

### Para entender CÓMO está construido
4. [`10-architecture/c4-containers.md`](../10-architecture/c4-containers.md) — servicios y relaciones
5. [`30-contracts/conventions.md`](../30-contracts/conventions.md) — naming, eventos, versionado
6. [`40-data/event-store.md`](../40-data/event-store.md) — log inmutable (columna vertebral)

### Para entender QUÉ hace cada parte
7. [`20-modules/`](../20-modules/) — fichas de módulo (empezar por `core/meta-orchestrator.md`)

### Para entender el ciclo de vida de una petición
8. [`50-flows/request-flow.md`](../50-flows/request-flow.md) — end-to-end
9. [`50-flows/learning-loop.md`](../50-flows/learning-loop.md) — cómo el sistema mejora
10. [`50-flows/federation-loop.md`](../50-flows/federation-loop.md) — local → global

### Para tomar decisiones
11. [`70-adr/`](../70-adr/) — por qué se eligió cada diseño (empezar por ADR-0001)

### Para operar y medir
12. [`60-governance/`](../60-governance/) — RACI, OKRs, KPIs, rituales

### Para construir
13. [`90-roadmap/construction-order.md`](../90-roadmap/construction-order.md) — 9 fases ordenadas

---

## Árbol de documentación

```
docs/
├── 00-overview/           ← estás aquí
│   ├── README.md
│   ├── glossary.md
│   └── system-context.md
├── 10-architecture/
│   ├── rings-topology.md
│   ├── three-flows.md
│   ├── deployment-topology.md
│   └── c4-containers.md
├── 20-modules/
│   ├── core/              (6 módulos C-Level)
│   ├── guilds/            (7 coordinadores de guild)
│   ├── specialists/       (interfaz genérica)
│   └── transverse/        (5 roles transversales)
├── 30-contracts/
│   ├── conventions.md
│   ├── events/            (JSON Schema por evento)
│   ├── ports/             (JSON Schema por puerto)
│   └── api/openapi.yaml
├── 40-data/
│   ├── postgres-schema.sql
│   ├── event-store.md
│   ├── projections.md
│   └── memory-layers.md
├── 50-flows/
│   ├── request-flow.md
│   ├── learning-loop.md
│   ├── federation-loop.md
│   └── escalation-rules.md
├── 60-governance/
│   ├── raci-matrix.md
│   ├── okrs-template.md
│   ├── kpis-catalog.md
│   └── rituals.md
├── 70-adr/
│   ├── 0001-rings-topology.md
│   ├── 0002-event-sourcing-cqrs.md
│   ├── 0003-nats-over-kafka.md
│   ├── 0004-federated-learning-shape.md
│   ├── 0005-three-coexistent-hierarchies.md
│   ├── 0006-llm-gateway-abstraction.md
│   └── 0007-anonymizer-mandatory-edge.md
└── 90-roadmap/
    ├── construction-order.md
    └── readiness-checklist.md
```

---

## Convenciones de estado de documentos

| Status    | Significado                                    |
|-----------|------------------------------------------------|
| `draft`   | En redacción, puede cambiar radicalmente       |
| `review`  | Listo para revisión de pares                   |
| `approved`| Aprobado, cambios requieren ADR o justificación|
| `implemented` | Ya se construyó la fase correspondiente   |
| `deprecated`  | Reemplazado por otro documento            |

---

## Stack de referencia

| Capa              | Tecnología                          |
|-------------------|-------------------------------------|
| API HTTP (borde)  | FastAPI (Python 3.11+)              |
| Event bus         | NATS JetStream                      |
| Log inmutable     | PostgreSQL 16 (append-only)         |
| Memoria semántica | PostgreSQL 16 + pgvector            |
| Caché efímero     | Redis                               |
| Observabilidad    | OpenTelemetry + Grafana             |
| LLM gateway       | LiteLLM (abstracción multi-proveedor)|
| Contratos         | Pydantic v2 + JSON Schema           |

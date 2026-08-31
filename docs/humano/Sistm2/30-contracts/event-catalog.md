# Catálogo de eventos

> **Status**: `draft` | Última revisión: 2026-05-07 | Ver también: `conventions.md`

Registro de todos los eventos del sistema con su versión, productor, consumidores y ruta al JSON Schema.

---

## Convención de columnas

- **Evento**: nombre canónico (`dominio.accion.vN`)
- **Stream**: stream NATS donde se publica
- **Productor**: módulo que emite el evento
- **Consumidores principales**: módulos que reaccionan a él
- **Schema**: ruta al archivo JSON Schema

---

## Eventos del ciclo de petición

| Evento | Stream | Productor | Consumidores | Schema |
|---|---|---|---|---|
| `request.received.v1` | REQUESTS | API Gateway | Meta-Orchestrator, Compliance Officer, Telemetry | `events/request.received.v1.json` |
| `request.classified.v1` | REQUESTS | Router/Triage | Meta-Orchestrator, Telemetry | `events/request.classified.v1.json` *(pendiente)* |
| `plan.created.v1` | REQUESTS | Meta-Orchestrator | Resource Allocator, Telemetry | `events/plan.created.v1.json` *(pendiente)* |
| `task.dispatched.v1` | TASKS | Meta-Orchestrator | Guild destinatario, Telemetry | `events/task.dispatched.v1.json` |
| `task.completed.v1` | TASKS | Guild | Meta-Orchestrator, Telemetry | `events/task.completed.v1.json` |
| `task.failed.v1` | TASKS | Guild | Meta-Orchestrator, Telemetry | `events/task.failed.v1.json` *(pendiente)* |
| `response.synthesized.v1` | REQUESTS | Meta-Orchestrator | Guild QA, Compliance Officer | `events/response.synthesized.v1.json` *(pendiente)* |
| `response.delivered.v1` | REQUESTS | Meta-Orchestrator | User Profiler, Guild Memoria, Telemetry | `events/response.delivered.v1.json` *(pendiente)* |
| `guardrail.triggered.v1` | REQUESTS | Compliance Officer | Meta-Orchestrator, Telemetry, Auditor | `events/guardrail.triggered.v1.json` *(pendiente)* |

---

## Eventos de memoria

| Evento | Stream | Productor | Consumidores | Schema |
|---|---|---|---|---|
| `user.profile.updated.v1` | MEMORY | User Profiler | Meta-Orchestrator (invalidar caché) | `events/user.profile.updated.v1.json` *(pendiente)* |
| `user.preference.inferred.v1` | MEMORY | User Profiler | Guild Memoria | `events/user.preference.inferred.v1.json` *(pendiente)* |
| `memory.write.committed.v1` | MEMORY | Guild Memoria | Meta-Orchestrator | `events/memory.write.committed.v1.json` *(pendiente)* |

---

## Eventos del ciclo de aprendizaje

| Evento | Stream | Productor | Consumidores | Schema |
|---|---|---|---|---|
| `pattern.detected.v1` | LEARNING | Pattern Miner | Knowledge Officer | `events/pattern.detected.v1.json` *(pendiente)* |
| `doctrine.proposed.v1` | LEARNING | Pattern Miner | Knowledge Officer, Compliance Officer | `events/doctrine.proposed.v1.json` *(pendiente)* |
| `experiment.started.v1` | LEARNING | Doctrine Publisher | Auditor, Telemetry | `events/experiment.started.v1.json` *(pendiente)* |
| `experiment.concluded.v1` | LEARNING | Doctrine Publisher | Knowledge Officer, Telemetry | `events/experiment.concluded.v1.json` *(pendiente)* |
| `doctrine.published.v1` | LEARNING | Doctrine Publisher | Todos los módulos (broadcast) | `events/doctrine.published.v1.json` |
| `doctrine.rolled_back.v1` | LEARNING | Doctrine Publisher | Todos los módulos (broadcast), Auditor | `events/doctrine.rolled_back.v1.json` *(pendiente)* |

---

## Eventos de auditoría y telemetría

| Evento | Stream | Productor | Consumidores | Schema |
|---|---|---|---|---|
| `audit.finding.opened.v1` | AUDIT | Auditor | Meta-Orchestrator, Telemetry, Operador | `events/audit.finding.opened.v1.json` *(pendiente)* |
| `audit.finding.resolved.v1` | AUDIT | Auditor / Operador | Telemetry | `events/audit.finding.resolved.v1.json` *(pendiente)* |
| `drift.detected.v1` | AUDIT | Auditor | Doctrine Publisher, Telemetry | `events/drift.detected.v1.json` *(pendiente)* |
| `slo.breached.v1` | TELEMETRY | Telemetry/SRE | Meta-Orchestrator (modo degradado), Operador | `events/slo.breached.v1.json` *(pendiente)* |

---

## Estado del catálogo

- **Schemas completos**: `request.received.v1`, `task.dispatched.v1`, `task.completed.v1`, `doctrine.published.v1`
- **Schemas pendientes (fase 1–2)**: `request.classified`, `plan.created`, `task.failed`, `response.synthesized`, `response.delivered`, `guardrail.triggered`
- **Schemas pendientes (fase 7–8)**: todos los eventos de LEARNING y AUDIT

**Prioridad de creación**: los schemas marcados como "fase 1" deben completarse antes de comenzar la implementación de la Fase 1 del roadmap.

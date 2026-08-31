# Convenciones de contratos y eventos

> **Status**: `draft` | Última revisión: 2026-05-07

Reglas que gobiernan todo el catálogo de eventos, puertos y APIs. **Ante conflicto, estas convenciones ganan**.

---

## 1. Naming de eventos

**Patrón**: `<dominio>.<entidad>.<verbo_pasado>`

```
request.received
request.classified
plan.created
task.dispatched
task.completed
task.failed
response.synthesized
response.delivered
memory.write.requested
memory.write.committed
memory.read.served
user.profile.updated
user.preference.inferred
pattern.detected
experiment.started
experiment.concluded
doctrine.proposed
doctrine.published
doctrine.rolled_back
guardrail.triggered
slo.breached
drift.detected
audit.finding.opened
```

**Reglas de naming:**
- Todo en minúsculas, separado por puntos.
- Máximo 4 segmentos.
- El verbo siempre en tiempo pasado (hecho ocurrido, no comando).
- No usar nombres de módulos concretos en el tipo de evento (evita acoplamiento).

---

## 2. Estructura canónica de un evento

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "event_id",
    "event_type",
    "event_version",
    "occurred_at",
    "producer",
    "correlation_id",
    "causation_id",
    "tenant_id",
    "payload"
  ],
  "properties": {
    "event_id":       { "type": "string", "format": "uuid" },
    "event_type":     { "type": "string", "pattern": "^[a-z]+(\\.([a-z]+\\.?)){1,3}[a-z]+$" },
    "event_version":  { "type": "string", "pattern": "^v[0-9]+$", "default": "v1" },
    "occurred_at":    { "type": "string", "format": "date-time" },
    "producer":       { "type": "string", "description": "Identificador del módulo que emitió el evento" },
    "correlation_id": { "type": "string", "format": "uuid", "description": "ID de la petición raíz" },
    "causation_id":   { "type": "string", "format": "uuid", "description": "ID del evento padre que causó este" },
    "tenant_id":      { "type": "string", "description": "ID del usuario o organización" },
    "payload":        { "type": "object", "description": "Datos específicos del evento" }
  }
}
```

---

## 3. Versionado de eventos

- **Cambios aditivos** (nuevo campo opcional en `payload`): mismo `event_version`. Los consumidores deben ignorar campos desconocidos.
- **Cambios incompatibles** (campo obligatorio nuevo, cambio de tipo, eliminación): nuevo `vN+1`. Ambas versiones coexisten durante el período de migración.
- **Política de deprecación**: mínimo 30 días de coexistencia antes de retirar una versión.
- **Contract testing**: cada consumidor tiene un test que valida el esquema del evento que consume (consumer-driven contracts).

---

## 4. NATS Subjects y Streams

### Convención de subjects

```
<stream>.<dominio>.<entidad>.<accion>
```

Ejemplos:
- `REQUESTS.request.incoming.new`
- `TASKS.task.guild-research.dispatched`
- `LEARNING.pattern.aggregate.detected`
- `AUDIT.finding.compliance.opened`

### Streams definidos

| Stream | Subjects | Retention | Descripción |
|---|---|---|---|
| REQUESTS | `REQUESTS.>` | 7 días | Ciclo de vida de peticiones |
| TASKS | `TASKS.>` | 7 días | Tareas delegadas a guilds |
| MEMORY | `MEMORY.>` | 30 días | Operaciones de memoria |
| LEARNING | `LEARNING.>` | 90 días | Patrones, experimentos, doctrinas |
| AUDIT | `AUDIT.>` | 365 días | Hallazgos de auditoría e incidentes |
| TELEMETRY | `TELEMETRY.>` | 3 días | Métricas y alertas operativas |

### Consumers

- Todos los consumers son **durables** (nombre estable).
- `AckPolicy: explicit` — el mensaje no se considera procesado hasta que el consumer hace `ack`.
- `MaxDeliver: 3` — tras 3 fallos, va al dead-letter subject `<stream>.dlq`.
- Idempotencia: todo consumer chequea `event_id` contra Redis antes de procesar (TTL = 24h).

---

## 5. API HTTP del borde

Especificada en `api/openapi.yaml`. Convenciones:

- **Base URL**: `/api/v1/`
- **Autenticación**: Bearer token (JWT), validado por el API Gateway antes de llegar al Meta-Orchestrator.
- **Petición mínima**:

```json
POST /api/v1/requests
{
  "content": "texto de la petición",
  "context": {}
}
```

- **Respuesta síncrona** (peticiones simples): HTTP 200 con `response.content`.
- **Respuesta asíncrona** (peticiones complejas): HTTP 202 con `request_id` y endpoint de polling/webhook.
- **Errores**: RFC 7807 Problem Details.

---

## 6. Puertos (contratos de módulos)

Cada módulo define su puerto en `ports/<nombre-modulo>.json`. Estructura mínima:

```json
{
  "module": "meta-orchestrator",
  "ring": "core",
  "methods": [
    {
      "name": "handle_request",
      "input_schema": { "$ref": "events/request.received.v1.json" },
      "output_events": ["plan.created", "response.delivered"]
    }
  ],
  "consumes": ["request.received", "task.completed", "guardrail.triggered"],
  "publishes": ["plan.created", "task.dispatched", "response.synthesized"]
}
```

---

## 7. Reglas generales

- **Nunca PII en eventos** que crucen hacia memoria global. El Anonymizer es la única frontera válida.
- **Todos los módulos** deben emitir al menos un evento de telemetría por operación (para el KR: "100% de interacciones producen ≥1 evento de telemetría").
- **Sin llamadas directas entre módulos** a menos que sea estrictamente síncrono (solo Compliance Officer). Todo lo demás pasa por NATS.
- **Los payloads** no deben superar 1 MB. Para artefactos grandes, almacenar en NATS Object Store y poner la referencia en el evento.
- **Fechas y horas**: siempre ISO 8601 UTC en formato `occurred_at`.

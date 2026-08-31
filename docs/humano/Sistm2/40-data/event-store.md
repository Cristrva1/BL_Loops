# Event Store — Log inmutable

> **Status**: `draft` | Última revisión: 2026-05-07 | Ver también: ADR-0002

---

## Rol en la arquitectura

El event store es **la única fuente de verdad del sistema**. Todo lo demás (proyecciones, perfiles, doctrinas) se deriva de él. Si hay inconsistencia entre el event store y cualquier otra tabla, el event store gana.

---

## Principios

1. **Append-only**: nunca se actualiza ni borra un evento. Solo se insertan nuevos.
2. **Inmutable**: una vez escrito, un evento no cambia. Si un evento fue incorrecto, se escribe un evento de compensación.
3. **Completo**: toda acción relevante del sistema produce al menos un evento en el store.
4. **Auditable**: dado un `correlation_id`, se puede reconstruir el historial completo de una petición.

---

## Estructura de la tabla

Ver `postgres-schema.sql` sección 1. Campos clave:

| Campo | Tipo | Descripción |
|---|---|---|
| `event_id` | UUID | Identificador único del evento |
| `event_type` | VARCHAR | Nombre del evento (ej. `request.received`) |
| `event_version` | VARCHAR | Versión del esquema del evento |
| `occurred_at` | TIMESTAMPTZ | Cuándo ocurrió (siempre UTC) |
| `producer` | VARCHAR | Módulo que emitió el evento |
| `correlation_id` | UUID | ID de la petición raíz |
| `causation_id` | UUID | ID del evento que causó este |
| `tenant_id` | VARCHAR | Usuario u organización |
| `payload` | JSONB | Datos específicos del evento |

---

## Particionado

La tabla está particionada por mes (`PARTITION BY RANGE (occurred_at)`). Beneficios:

- Consultas recientes son rápidas (solo barren la partición activa).
- Las particiones antiguas se pueden archivar o comprimir sin afectar las recientes.
- `pg_partman` gestiona la creación automática de particiones futuras.

**Política de retención**: particiones > 12 meses se archivan (no borran) a almacenamiento frío.

---

## Cadena de causalidad

Para reconstruir el historial completo de una petición:

```sql
WITH RECURSIVE causal_chain AS (
    -- Evento raíz
    SELECT * FROM event_store WHERE correlation_id = :correlation_id
    AND event_id = causation_id
    UNION ALL
    -- Eventos causados
    SELECT e.* FROM event_store e
    JOIN causal_chain c ON e.causation_id = c.event_id
)
SELECT * FROM causal_chain ORDER BY occurred_at;
```

---

## Idempotencia de escritura

Antes de escribir un evento, el productor verifica en Redis si `event_id` ya existe (TTL = 24h). Si existe, no escribe. Esto garantiza que re-entregas del event bus no dupliquen eventos.

```
Redis check: GET idempotency:<event_id>
  → Si existe: skip (ya escrito)
  → Si no existe: INSERT + SET idempotency:<event_id> EX 86400
```

---

## Reconstrucción de estado (Event Sourcing)

El estado de cualquier entidad se reconstruye "doblando" (fold) el log:

```
estado_actual = reduce(apply_event, filter(eventos_relevantes, correlation_id), estado_inicial)
```

En la práctica, las **proyecciones materializadas** (`requests_view`, `tasks_view`, etc.) guardan el estado derivado para no reconstruirlo en cada consulta. Las proyecciones se actualizan de forma asíncrona al llegar nuevos eventos.

---

## Eventos de compensación

Si un evento fue incorrecto o una acción debe revertirse, **no se borra el evento original**. Se escribe un evento de compensación:

- `task.failed` compensa un `task.dispatched` que no tuvo `task.completed`.
- `doctrine.rolled_back` compensa un `doctrine.published`.
- `guardrail.triggered` puede acompañar a cualquier evento para registrar el bloqueo.

---

## Consultas frecuentes de referencia

```sql
-- Todos los eventos de una petición (ordenados)
SELECT * FROM event_store
WHERE correlation_id = :correlation_id
ORDER BY occurred_at;

-- Últimas N peticiones de un usuario
SELECT DISTINCT ON (correlation_id)
    correlation_id, event_type, occurred_at
FROM event_store
WHERE tenant_id = :tenant_id
  AND event_type = 'request.received'
ORDER BY correlation_id, occurred_at DESC
LIMIT 20;

-- Tasa de error por guild en las últimas 24h
SELECT
    payload->>'assignee_guild' AS guild,
    COUNT(*) FILTER (WHERE event_type = 'task.failed') AS failures,
    COUNT(*) FILTER (WHERE event_type = 'task.completed') AS successes
FROM event_store
WHERE occurred_at > now() - INTERVAL '24 hours'
  AND event_type IN ('task.completed', 'task.failed')
GROUP BY guild;
```

# Proyecciones y vistas materializadas

> **Status**: `draft` | Última revisión: 2026-05-07

---

## Principio

El event store es la fuente de verdad, pero las proyecciones son el mecanismo que hace el estado consultable de forma eficiente. Las proyecciones **no son el origen de la verdad**, son una vista derivada que se puede reconstruir desde el event store en caso de inconsistencia.

---

## Proyecciones del sistema

### 1. `requests_view` — Estado de peticiones

**Propósito**: consulta rápida del estado actual y métricas de cada petición.

**Construida desde eventos**:

| Evento | Acción en la proyección |
|---|---|
| `request.received` | INSERT con status = 'received' |
| `request.classified` | UPDATE: status = 'classified', classification |
| `plan.created` | UPDATE: status = 'planning', guilds_invoked, plan_created_at |
| `task.dispatched` | UPDATE: status = 'executing' |
| `response.synthesized` | UPDATE: status = 'qa' |
| `response.delivered` | UPDATE: status = 'delivered', delivered_at, total_tokens, total_latency_ms |
| `task.failed` | UPDATE: registra reintento o transición a 'failed' |
| `guardrail.triggered` | UPDATE: fallback_used = true |

**Latencia de actualización**: eventual, < 500ms desde el evento.

---

### 2. `tasks_view` — Estado de tareas

**Propósito**: seguimiento de cada subtarea individual delegada a un guild.

**Construida desde eventos**:

| Evento | Acción |
|---|---|
| `task.dispatched` | INSERT con status = 'dispatched' |
| `task.completed` | UPDATE: status = 'completed', result_content, metrics |
| `task.failed` | UPDATE: status = 'failed' o 'retrying', retry_count++ |

---

### 3. `user_profiles` — Perfil de usuario

**Propósito**: perfil completo para consulta rápida.

**Construida desde eventos**:

| Evento | Acción |
|---|---|
| `user.profile.updated` | UPSERT con diff aplicado, version++ |
| `user.preference.inferred` | UPDATE inferred_data con merge |
| `doctrine.published` | UPDATE active_doctrines[] |

---

### 4. `kpi_rollups` — KPIs agregados

**Propósito**: métricas del dashboard de Telemetry/SRE.

**Construida por**: batch job del módulo Telemetry/SRE cada hora (y diario/semanal para ventanas mayores).

**KPIs calculados** (ver `telemetry-sre.md` sección 9 para lista completa).

---

## Actualización de proyecciones

Las proyecciones se actualizan mediante **event consumers NATS** dedicados por proyección. No en el camino crítico de la petición.

```
NATS consumer (durable, explicit ack)
  → consume evento del stream
  → actualiza proyección en PostgreSQL
  → ack
  → si falla: retry (hasta MaxDeliver=3)
  → si sigue fallando: DLQ → alerta
```

**No hay transacciones distribuidas**: en el peor caso, una proyección puede estar ligeramente desactualizada. Es aceptable porque el event store siempre es consistente.

---

## Reconstrucción de proyecciones

Si una proyección queda en estado inconsistente, se puede reconstruir desde cero:

1. Truncar la tabla de proyección.
2. Replay de todos los eventos del event store en orden.
3. Reconstrucción determinista (el resultado siempre es el mismo dado el mismo log).

Tiempo estimado de reconstrucción completa (1M eventos): < 10 minutos.

---

## Proyecciones futuras (fases posteriores)

- **`guild_performance_view`**: métricas de calidad, latencia y costo por guild por semana.
- **`doctrine_impact_view`**: impacto medido de cada doctrina en los KPIs desde su activación.
- **`pattern_cohort_view`**: segmentación de usuarios por patrones de uso (anónima, para el Pattern Miner).

# ADR-0001 — Event Sourcing como fuente de verdad

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema necesita mantener un historial completo y auditable de todas las acciones. Los módulos son distribuidos y pueden fallar parcialmente. Se requiere capacidad de reconstruir el estado ante fallos y de auditar decisiones post-hoc.

---

## Decisión

**Adoptamos Event Sourcing**: toda acción relevante del sistema produce un evento inmutable que se escribe en el `event_store` de PostgreSQL. El estado de cualquier entidad se deriva de este log, no se almacena directamente como "estado actual".

Las proyecciones (vistas materializadas) son derivados del log para consultas eficientes, pero no son la fuente de verdad.

---

## Consecuencias positivas

- **Auditabilidad total**: cualquier decisión del sistema se puede rastrear hasta el evento que la causó.
- **Reconstrucción de estado**: si una proyección se corrompe, se puede rebuilder desde el log.
- **Debugging simplificado**: dado un `correlation_id`, se puede reproducir exactamente qué pasó y por qué.
- **Cadena de causalidad**: el campo `causation_id` permite trazar el árbol completo de causa y efecto.
- **Compatibilidad natural con CQRS**: las lecturas van a las proyecciones; las escrituras van al log.

---

## Consecuencias negativas

- **Complejidad adicional**: los desarrolladores deben pensar en términos de eventos, no de entidades con estado mutable.
- **Tamaño del log**: el log crece indefinidamente; se requiere particionado y política de archivado.
- **Eventual consistency**: las proyecciones son eventualmente consistentes con el log; hay una ventana de tiempo donde pueden estar desactualizadas.
- **Eventos de compensación**: en lugar de borrar/actualizar, se escriben nuevos eventos. Requiere disciplina de diseño.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Estado mutable directo en PostgreSQL | Sin audit trail; difícil de debuggear; no permite reconstrucción |
| Estado mutable + log separado | Log secundario es ciudadano de segunda clase; puede desincronizarse |
| Solo NATS (sin persistencia) | No es durable; mensajes se pierden ante fallo; no auditable |

---

## Revisión

Esta decisión se revisará si el volumen de eventos supera la capacidad de almacenamiento proyectada (año 1) o si la latencia de escritura al event store impacta los SLOs de petición.

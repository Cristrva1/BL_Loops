# ADR-0002 — NATS JetStream como bus de eventos

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema necesita un bus de mensajes que soporte pub/sub asíncrono entre módulos distribuidos, con garantías de entrega, replay de mensajes y bajo overhead operativo. El stack elegido es Python + FastAPI.

---

## Decisión

**Adoptamos NATS JetStream** como bus de eventos del sistema. Los módulos se comunican publicando y consumiendo eventos vía subjects NATS organizados por stream (`REQUESTS`, `TASKS`, `MEMORY`, `LEARNING`, `AUDIT`, `TELEMETRY`).

NATS KV Store se usa para estado compartido de baja latencia (doctrinas activas, tabla de routing).

---

## Consecuencias positivas

- **Bajo overhead**: NATS es extremadamente liviano comparado con Kafka o RabbitMQ; adecuado para iteraciones tempranas.
- **JetStream = durabilidad**: los mensajes persisten en disco; los consumers pueden hacer replay desde cualquier punto.
- **At-least-once delivery con explicit ack**: los mensajes no se marcan como procesados hasta que el consumer hace ack.
- **Dead-letter automático**: después de `MaxDeliver` intentos, el mensaje va al DLQ del stream.
- **KV Store integrado**: no se necesita un servicio extra para estado compartido ligero.
- **Wildcard subjects**: el módulo Telemetry puede suscribirse a `>` para observar todo el sistema.
- **Single binary**: NATS server es un binario único sin dependencias externas.

---

## Consecuencias negativas

- **No es Kafka**: para volúmenes muy altos (>100K msg/s) o casos de uso de streaming complejo, Kafka sería más adecuado.
- **Retención limitada**: JetStream retiene mensajes según política de tiempo/tamaño, no indefinidamente; el event store en PostgreSQL complementa esto.
- **Ecosistema más pequeño**: menos tooling de observabilidad comparado con Kafka.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Apache Kafka | Overhead operativo alto para un MVP; requiere ZooKeeper o KRaft; complejidad excesiva en fase inicial |
| RabbitMQ | Sin replay nativo de mensajes; no tiene KV Store; menos apto para event sourcing |
| Redis Pub/Sub | No durable; mensajes se pierden si el consumer no está conectado |
| HTTP directo entre módulos | Acoplamiento temporal; no desacoplado; violación del principio de independencia de módulos |
| AWS SQS/SNS | Vendor lock-in; latencia adicional; costo en producción |

---

## Revisión

Esta decisión se revisará si el sistema supera 50K peticiones/hora sostenidas o si la comunidad de NATS JetStream no evoluciona suficientemente el producto. Migrar a Kafka desde NATS requeriría cambiar solo los adaptadores de mensajería, no la lógica de negocio (gracias al patrón de puertos).

# Flujo 4 — Escalación y manejo de incidentes

> **Status**: `draft` | Última revisión: 2026-05-07

Flujo que cubre los escenarios de excepción: vetos de compliance, fallos de SLO, incidentes de auditoría y rollbacks de doctrina.

---

## Diagrama: Escalación completa

```mermaid
flowchart TD
  START([Operación en curso]) --> EVENT{Evento de excepción}

  EVENT -->|guardrail.triggered| GT[Compliance Officer veta]
  GT --> GT1[Entrega respuesta fallback segura]
  GT1 --> GT2[INSERT guardrail_events]
  GT2 --> GT3{¿Patrón repetido?}
  GT3 -->|Sí, >3 en 1h| GT4[audit.finding.opened CRITICAL]
  GT3 -->|No| GT5[Registrar y continuar]
  GT4 --> HUMAN[Alerta operador humano]

  EVENT -->|slo.breached| SB[Telemetry detecta incumplimiento]
  SB --> SB1{¿Qué SLO?}
  SB1 -->|Latencia p95 alta| SB2[MO degrada plan — menos guilds]
  SB1 -->|Error rate > umbral| SB3[MO activa modo degradado]
  SB1 -->|Compliance caído| SB4[GW rechaza TODAS las peticiones]
  SB2 --> SB5[Telemetry monitorea recuperación]
  SB3 --> SB5
  SB4 --> HUMAN

  EVENT -->|drift.detected| DD[Auditor recibe señal de drift]
  DD --> DD1[Auditor evalúa muestra ciega]
  DD1 --> DD2{¿Drift confirmado?}
  DD2 -->|No| DD3[Cierra falsa alarma]
  DD2 -->|Sí| DD4[audit.finding.opened WARNING]
  DD4 --> DD5{¿Doctrina activa sospechosa?}
  DD5 -->|Sí| DD6[Propone doctrine.rolled_back]
  DD5 -->|No| DD7[Reporta al KO para investigación]
  DD6 --> ROLLBACK

  EVENT -->|experiment.concluded winner=control| EXP[Doctrine Publisher]
  EXP --> ROLLBACK[doctrine.rolled_back publicado]
  ROLLBACK --> RB1[Todos los módulos revierten a versión anterior]
  RB1 --> RB2[INSERT doctrine.rolled_back en event store]
  RB2 --> RB3[Telemetry monitorea KPIs post-rollback]
  RB3 --> RB4{¿KPIs se recuperan?}
  RB4 -->|Sí| RB5[Incidente cerrado]
  RB4 -->|No| HUMAN

  HUMAN --> INC[Operador revisa dashboard]
  INC --> INC1[Intervención manual según severidad]
```

---

## Niveles de escalación

| Nivel | Trigger | Receptor | Tiempo de respuesta esperado |
|---|---|---|---|
| P3 - Info | `drift.detected` suave | Auditor (auto) | < 24h |
| P2 - Warning | `slo.breached` no crítico | Telemetry + MO (auto) | < 1h |
| P2 - Warning | `audit.finding.opened` WARNING | Auditor + KO | < 4h |
| P1 - Critical | `audit.finding.opened` CRITICAL | Operador humano | < 15min |
| P0 - Emergency | Compliance caído o múltiples SLOs críticos | Operador humano (alerta inmediata) | Inmediato |

---

## Rollback de doctrina: protocolo detallado

```mermaid
sequenceDiagram
  participant Audit as Auditor
  participant DP as Doctrine Publisher
  participant ES as Event Store
  participant NATS as NATS KV Store
  participant AllModules as Todos los módulos

  Audit->>DP: Señal de rollback (drift confirmado o experimento perdido)
  DP->>DP: Identifica versión anterior válida
  DP->>ES: INSERT doctrine.rolled_back
  DP->>NATS: UPDATE doctrine_kv — restaura versión N-1
  NATS-->>AllModules: Notificación de cambio en KV
  AllModules->>AllModules: Reload de configuración en caliente
  Note over AllModules: Sin reinicio de procesos
  DP->>Audit: Confirma rollback aplicado
  Audit->>ES: UPDATE audit_finding (status=resolved)
```

**Garantías del rollback**:
- Sin downtime: los módulos recargan configuración en caliente desde NATS KV.
- Tiempo de rollback completo: < 30 segundos desde que se publica `doctrine.rolled_back`.
- La doctrina retirada queda en estado `rolled_back` en la tabla `doctrines` (nunca borrada).
- Se mantiene la causalidad en el event store: el `doctrine.rolled_back` referencia al `doctrine.published` original.

---

## Modo degradado del sistema

Cuando el Meta-Orchestrator detecta presión de recursos o fallos múltiples activa el **modo degradado**:

| Modo | Guilds activos | Calidad esperada | Trigger |
|---|---|---|---|
| Normal | Todos los definidos en el plan | Alta | Sin incidentes |
| Degradado leve | Solo guilds críticos (production + communication) | Media | SLO latencia > p95 |
| Degradado severo | Solo production (respuesta directa sin investigación) | Baja | SLO latencia > p99 o error rate > 5% |
| Fallback total | Respuesta estática + log del error | Mínima | Cualquier fallo sistémico |

El usuario siempre recibe una respuesta con una nota indicando el modo si no es Normal.

# Flujo 1 — Ciclo de petición

> **Status**: `draft` | Última revisión: 2026-05-07

Flujo cardinal desde que el usuario envía una petición hasta que recibe la respuesta.

---

## Diagrama

```mermaid
sequenceDiagram
  autonumber
  actor User as Usuario
  participant GW as API Gateway
  participant CO as Compliance Officer
  participant MO as Meta-Orchestrator
  participant RT as Router/Triage
  participant RA as Resource Allocator
  participant UP as User Profiler
  participant Guilds as Guilds (1..N)
  participant QA as Guild QA
  participant ES as Event Store

  User->>GW: POST /api/v1/requests {content, context}
  GW->>GW: Autenticación JWT + rate-limit

  par Evaluación paralela
    GW->>CO: (async) request.received — evaluación de entrada
    GW->>MO: request.received
  end

  CO-->>MO: guardrail.triggered (si viola política)
  Note over MO: Si guardrail → respuesta fallback, fin

  MO->>ES: INSERT request.received
  MO->>RT: request.received
  RT->>RT: Clasificación + políticas
  RT->>ES: INSERT request.classified
  RT->>MO: request.classified

  MO->>UP: get_profile(tenant_id)
  UP-->>MO: UserProfile
  MO->>RA: allocate_budget(plan)
  RA-->>MO: BudgetAllocation

  MO->>MO: Construye plan (guilds y orden)
  MO->>ES: INSERT plan.created

  loop Por cada subtarea del plan
    MO->>Guilds: task.dispatched
    MO->>ES: INSERT task.dispatched
    Guilds->>Guilds: Ejecuta (con especialistas + LLM)
    Guilds->>ES: INSERT task.completed | task.failed
    Guilds->>MO: task.completed | task.failed
  end

  MO->>MO: Sintetiza resultados de guilds
  MO->>ES: INSERT response.synthesized
  MO->>QA: (sync) evaluate_output
  QA-->>MO: pass | fail | pass_with_warnings

  alt QA fail (hasta 2 reintentos)
    MO->>Guilds: task.dispatched (corrección)
  end

  MO->>CO: (sync) evaluate_output
  CO-->>MO: allow | block | allow_with_modifications

  MO->>ES: INSERT response.delivered
  MO->>GW: response.content
  GW->>User: HTTP 200 {response}

  Note over UP: (async, post-entrega)
  MO-->>UP: response.delivered — inferir preferencias
```

---

## Invariantes del flujo

1. **Compliance Officer evalúa SIEMPRE** tanto la entrada como la salida. No hay bypass.
2. **El event store se escribe en cada transición** de estado. Si falla el write al store, la operación falla.
3. **El perfil del usuario se inyecta ANTES de planificar**, nunca después.
4. **El presupuesto de tokens se asigna ANTES de despachar tareas**, nunca optimistamente.
5. **Si el plan falla por completo**, se entrega una respuesta de fallback. La tasa de respuestas entregadas ≥ 99.9%.

---

## Manejo de errores en el flujo

| Escenario | Comportamiento |
|---|---|
| `guardrail.triggered` en entrada | Respuesta fallback segura, no se invocan guilds |
| `task.failed` (guild) | Reintento automático hasta 2 veces; si sigue fallando, plan degrada |
| QA falla 3 veces | Respuesta parcial con advertencia de calidad |
| Timeout del plan | Respuesta parcial con los guilds que completaron |
| Compliance bloquea el output | Respuesta fallback; evento registrado |
| Event store no disponible | Petición rechazada (fail-fast, no hay operación sin audit trail) |

---

## SLO de punta a punta

- p50: < 3s
- p95: < 8s
- p99: < 15s
- Tasa de entrega (con o sin fallback): ≥ 99.9%

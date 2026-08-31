# Los tres flujos cardinales

> **Status**: `draft` | Última revisión: 2026-05-07

Los tres flujos son ortogonales entre sí. Cada componente del sistema vive en una coordenada (anillo, dominio, fase de aprendizaje).

---

## Flujo 1 — Petición (horizontal)

**Dirección**: Usuario → respuesta entregada.
**Naturaleza**: síncrono desde la perspectiva del usuario; internamente asíncrono por eventos.

```
Usuario
  │
  ▼
Recepción (API Gateway)
  │  evento: request.received
  ▼
Router / Triage
  │  evento: request.classified
  ▼
Planificador (Meta-Orchestrator)
  │  evento: plan.created
  ▼
Coordinadores de Guild (paralelo si procede)
  │  evento: task.dispatched (por subtarea)
  ▼
Especialistas
  │  evento: task.completed / task.failed
  ▼
Síntesis (Coord. Producción + Meta-Orchestrator)
  │  evento: response.synthesized
  ▼
QA (Coord. Calidad)
  │  evento: qa.passed / qa.failed
  ▼
Entrega al Usuario
  │  evento: response.delivered
```

**Invariantes del flujo de petición:**
- Todo `request.received` termina en `response.delivered` o en `response.delivered` con fallback.
- El Compliance Officer puede cortar el flujo en cualquier punto emitiendo `guardrail.triggered`.
- El Resource Allocator supervisa tokens y latencia; puede degradar el plan si el presupuesto se agota.

---

## Flujo 2 — Memoria (vertical)

**Dirección**: interacción → persistencia en capas → recuperación futura.
**Naturaleza**: asíncrono; no bloquea el flujo de petición.

```
Interacción (cualquier evento del Flujo 1)
  │
  ▼
Memoria de trabajo (Redis, TTL = duración de la petición)
  │  scope: correlation_id
  │
  ├──► Memoria episódica (PostgreSQL, scope: user_id)
  │    Almacena: resumen de interacción, feedback implícito/explícito,
  │              preferencias inferidas
  │
  └──► Memoria semántica global (PostgreSQL + pgvector)
       Pasa SIEMPRE por Anonymizer antes de llegar aquí
       Almacena: embeddings de patrones, sin PII
```

**Capas de memoria comparadas:**

| Capa | Scope | Motor | TTL | Contiene |
|---|---|---|---|---|
| Trabajo | `correlation_id` | Redis | Petición activa | Estado intermedio |
| Episódica | `user_id` | PostgreSQL | Indefinido | Historial per-usuario |
| Semántica | Global | pgvector | Indefinido | Patrones anonimizados |

**Recuperación:**
- Antes de planificar, el Meta-Orchestrator consulta: (1) memoria de trabajo activa, (2) episódica del usuario, (3) semántica global por similitud.
- Prioridad: trabajo > episódica > semántica.

---

## Flujo 3 — Aprendizaje (circular)

**Dirección**: resultado → mejora → vuelta al Flujo 1.
**Naturaleza**: completamente asíncrono; no interfiere con latencia del usuario.

```
Resultado (evento: response.delivered)
  │
  ▼
Telemetry / SRE
  │  Recoge métricas: latencia, tokens, satisfacción, re-prompts
  │
  ▼
Auditor
  │  Revisa muestra ciega: ¿el output fue correcto? ¿hay drift?
  │  Emite: audit.finding.opened (si detecta problema)
  │
  ▼
Pattern Miner (batch nocturno / streaming suave)
  │  Agrega señales débiles entre usuarios (anonimizados)
  │  Emite: pattern.detected
  │
  ▼
Validator A/B
  │  Diseña experimento: cohorte tratamiento vs. control
  │  Emite: experiment.started
  │  Espera significancia estadística (N días, p < 0.05)
  │  Emite: experiment.concluded
  │
  ▼
Doctrine Publisher
  │  Si el experimento gana: emite doctrine.published
  │  Si pierde: emite doctrine.rolled_back
  │  Archiva experimento siempre (en tabla experiments)
  │
  ▼
Despliegue a todos los módulos afectados
  │  (via evento doctrine.published que consumen Router, Profiler, Guilds)
  │
  └──► vuelve al Flujo 1 mejorado
```

**Guardrails del flujo de aprendizaje:**
- Ninguna doctrina se despliega sin pasar por Validator A/B.
- El Compliance Officer puede vetar el despliegue de una doctrina.
- Toda regresión > 2% en KPIs críticos dispara rollback automático.
- El Auditor usa métricas adversariales para evitar drift silencioso.

---

## Interacciones entre los tres flujos

```
          FLUJO 1 (Petición)
          ─────────────────────────────────►
               │                  │
               │ escribe          │ lee (contexto)
               ▼                  ▲
          FLUJO 2 (Memoria)
          ─────────────────────────────────
               │ señales
               ▼
          FLUJO 3 (Aprendizaje)
          ◄────────────────────────────────
               │ doctrinas mejoradas
               └──────────────────────────► FLUJO 1 siguiente iteración
```

- El **Flujo 1** escribe al Flujo 2 y lee de él.
- El **Flujo 2** alimenta al Flujo 3 con señales anonimizadas.
- El **Flujo 3** actualiza doctrinas que mejoran el Flujo 1 en la próxima iteración.

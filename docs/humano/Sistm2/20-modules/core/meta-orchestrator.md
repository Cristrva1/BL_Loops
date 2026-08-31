# Meta-Orchestrator

> **Status**: `draft` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Recibir intenciones de usuario, construir un plan de ejecución, coordinar a los guilds para llevarlo a cabo y garantizar la entrega de una respuesta de calidad. **No ejecuta trabajo directamente**.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: CEO
- **Patrón de coordinación**: Orquestador (no coreógrafo)

---

## 3. Reporta a / Dirige a

- **Reporta a**: nadie internamente; reporta resultados al usuario (vía API Gateway)
- **Dirige a**: Router/Triage, todos los Coordinadores de Guild
- **Supervisado por**: Auditor (post-hoc), Compliance Officer (veto en tiempo real)

---

## 4. Puerto (interfaz)

```python
class MetaOrchestratorPort:
    async def handle_request(self, event: RequestReceived) -> None:
        """
        Punto de entrada principal. Construye el plan y delega.
        Publica: plan.created, task.dispatched, response.synthesized, response.delivered
        """

    async def handle_task_result(self, event: TaskCompleted | TaskFailed) -> None:
        """
        Recibe resultados de guilds. Decide si sintetizar o redistribuir.
        Publica: response.synthesized | task.dispatched (re-planificación)
        """

    async def handle_guardrail(self, event: GuardrailTriggered) -> None:
        """
        Recibe veto del Compliance Officer.
        Publica: response.delivered (con fallback seguro)
        """

    async def handle_slo_breach(self, event: SloBreach) -> None:
        """
        Recibe alerta de Resource Allocator.
        Acción: degradar plan (menos guilds, respuesta parcial con advertencia).
        """
```

---

## 5. Eventos que publica

| Evento | Cuándo |
|---|---|
| `plan.created` | Tras clasificar la petición y decidir los guilds necesarios |
| `task.dispatched` | Por cada subtarea delegada a un guild |
| `response.synthesized` | Cuando combina todos los resultados de guilds |
| `response.delivered` | Cuando la respuesta final se entrega al usuario (o fallback) |

---

## 6. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `request.received` | API Gateway | Iniciar ciclo de petición |
| `request.classified` | Router/Triage | Actualizar plan con clasificación |
| `task.completed` | Cualquier guild | Agregar resultado al plan |
| `task.failed` | Cualquier guild | Reintentar o degradar |
| `guardrail.triggered` | Compliance Officer | Abortar plan, devolver fallback |
| `slo.breached` | Resource Allocator | Degradar plan en curso |
| `doctrine.published` | Doctrine Publisher | Actualizar políticas de planificación |

---

## 7. Estado que posee

- **Redis** (`work:<correlation_id>`): estado de ejecución de la petición actual (plan, tareas pendientes, resultados parciales). TTL = timeout de petición (default 30s).
- **PostgreSQL** (`event_store`): todos sus eventos publicados (inmutable).
- **Sin estado propio de larga duración**. El estado entre sesiones vive en el User Profiler.

---

## 8. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia p50 del ciclo completo | < 3s |
| Latencia p95 del ciclo completo | < 8s |
| Latencia p99 del ciclo completo | < 15s |
| Tasa de respuestas entregadas (con o sin fallback) | 99.9% |
| Tasa de respuestas sin fallback (calidad) | > 95% |
| Error rate interno | < 0.1% |

---

## 9. Decisiones que puede tomar sin escalar

- Elegir qué guilds invocar y en qué orden/paralelismo.
- Reintentar una tarea fallida hasta 2 veces.
- Degradar el plan (quitar guilds opcionales) si el presupuesto de tokens se agota.
- Sintetizar una respuesta parcial con aviso si alguna tarea no termina a tiempo.

---

## 10. Cuándo escala

- Si la petición implica acceso a datos sensibles o PII → escala a Compliance Officer (síncrono).
- Si el Auditor detecta patrón de degradación sistemática → escala al operador humano via alerta.
- Si hay ambigüedad sobre qué guild es responsable → consulta al Architecture Guardian.

---

## 11. Métricas de calidad propias

- `orchestrator.plan.guilds_invoked` — distribución de guilds por petición (histogram)
- `orchestrator.plan.replan_count` — re-planificaciones por correlación (counter)
- `orchestrator.response.fallback_rate` — % de respuestas que activaron fallback (gauge)
- `orchestrator.latency.total_ms` — latencia end-to-end por petición (histogram)
- `orchestrator.tokens.total` — tokens totales por petición (histogram)

---

## Notas de implementación (no código)

- Internamente implementa el patrón **Saga orquestada**: mantiene el estado de cada paso en Redis y recupera desde el event store en caso de fallo.
- La planificación puede ser tan simple como una tabla de routing estático (fase 2) o tan compleja como un planner LLM (fases posteriores).
- El sintetizador puede ser también un LLM que combina los outputs de todos los guilds.

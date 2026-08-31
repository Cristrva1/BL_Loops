# Resource Allocator (CFO)

> **Status**: `stub` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Controlar el presupuesto de tokens, latencia y costo por petición. Evitar que el sistema consuma recursos ilimitados. Alertar cuando el plan en curso excede el presupuesto asignado.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: CFO / Resource Allocator
- **Patrón**: Token Bucket + Budget Enforcer

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator
- **Informa a**: Telemetry/SRE (con métricas de consumo)

---

## 4. Puerto (interfaz) — pendiente de especificar

```python
class ResourceAllocatorPort:
    async def allocate_budget(self, plan: PlanCreated) -> BudgetAllocation:
        """
        Asigna presupuesto de tokens y latencia a cada subtarea del plan.
        """

    async def check_budget(self, task: TaskDispatched) -> BudgetCheck:
        """
        Verifica si hay presupuesto disponible antes de ejecutar una tarea.
        """

    async def record_consumption(self, event: TaskCompleted) -> None:
        """
        Registra el consumo real de una tarea completada.
        """
```

---

## 5. Estado que posee

- **Redis** (`budget:<correlation_id>`): presupuesto activo por petición (TTL = timeout).
- **PostgreSQL** (`consumption_log`): registro de consumo para análisis de eficiencia.

---

> **TODO**: Completar secciones 5–11. Prioridad: fase 5 (telemetría + dashboard).

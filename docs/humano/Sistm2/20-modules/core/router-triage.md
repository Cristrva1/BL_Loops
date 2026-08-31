# Router / Triage

> **Status**: `draft` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Clasificar cada petición entrante con la mayor rapidez posible, aplicar políticas de routing, y publicar la clasificación para que el Meta-Orchestrator construya el plan correcto.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: Chief of Staff
- **Patrón**: Clasificador + Policy Engine

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator
- **Dirige a**: nada directamente; publica clasificación para que MO decida
- **Informa a**: Compliance Officer (en peticiones de alta sensibilidad)

---

## 4. Puerto (interfaz)

```python
class RouterTriagePort:
    async def classify_request(self, event: RequestReceived) -> None:
        """
        Clasifica la petición y publica request.classified.
        Categorías: trivial | planning_required | sensitive | tool_required | complex
        Subtipo: research | production | analysis | communication | memory | multi_guild
        """

    async def apply_policies(self, classification: RequestClassified) -> PolicyDecision:
        """
        Aplica políticas activas (doctrinas vigentes) sobre la clasificación.
        Retorna: guild assignment, priority adjustments, compliance flags
        """

    async def update_routing_table(self, event: DoctrinePublished) -> None:
        """
        Actualiza las reglas de routing cuando llega una nueva doctrina.
        """
```

---

## 5. Eventos que publica

| Evento | Cuándo |
|---|---|
| `request.classified` | Después de analizar la petición |
| `guardrail.triggered` | Si la clasificación detecta violación de política antes de llegar al Compliance Officer |

---

## 6. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `request.received` | API Gateway | Clasificar petición |
| `doctrine.published` | Doctrine Publisher | Actualizar tabla de routing |

---

## 7. Estado que posee

- **NATS KV Store** (`routing_table`): tabla de routing activa con doctrinas vigentes. Lectura en tiempo real durante clasificación.
- **Sin estado de larga duración** en la ruta principal (clasificación es stateless por petición).

---

## 8. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia de clasificación p95 | < 200ms |
| Latencia de clasificación p99 | < 500ms |
| Precisión de clasificación (guild correcto) | > 90% (medido por Auditor) |
| Disponibilidad | 99.95% |

---

## 9. Decisiones que puede tomar sin escalar

- Clasificar la petición en cualquiera de las 5 categorías.
- Asignar prioridad (low/normal/high) basada en perfil del usuario y tipo de petición.
- Rechazar peticiones malformadas (HTTP 400) antes de consumir recursos.
- Aplicar rate-limit por tenant según políticas del Resource Allocator.

---

## 10. Cuándo escala

- Petición con flag `sensitive = true` → notifica al Compliance Officer en paralelo.
- Ambigüedad de clasificación (confianza < 0.7) → escala a Meta-Orchestrator para decisión.
- Petición que excede budget estimado → alerta al Resource Allocator antes de publicar.

---

## 11. Métricas de calidad propias

- `router.classification.category_dist` — distribución de categorías (histogram)
- `router.classification.confidence` — confianza promedio por categoría (gauge)
- `router.classification.latency_ms` — latencia de clasificación (histogram)
- `router.policy.doctrine_version` — versión de doctrina activa en routing table (gauge)
- `router.reclassification_rate` — % de peticiones re-clasificadas post-hoc (gauge, medido por Auditor)

---

## Notas de implementación

- En fase 2 (MVP), la clasificación puede ser un modelo liviano (reglas + embeddings) o incluso una tabla de keywords.
- En fases posteriores, el Router puede usar un LLM pequeño (< 1B params) para clasificación semántica.
- La tabla de routing debe ser recargable en caliente sin reinicio del servicio.
- La clasificación `sensitive` debe ser **conservadora**: ante duda, marcar como sensible.

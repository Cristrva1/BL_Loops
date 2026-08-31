# Compliance Officer (Guardrails)

> **Status**: `draft` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Bloquear acciones inseguras, ilegales o que violen las políticas del sistema antes de que se ejecuten o entreguen al usuario. Es el único módulo con **poder de veto absoluto y suplantación**.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: Compliance Officer / Legal
- **Patrón**: Interceptor síncrono + Monitor asíncrono

---

## 3. Reporta a / Dirige a

- **Reporta a**: nadie (independiente). En incidentes graves, alerta directamente al operador humano.
- **Dirige a**: puede forzar acciones a cualquier módulo en cualquier anillo (veto y suplantación)
- **Única excepción a la jerarquía**: puede interrumpir al Meta-Orchestrator

---

## 4. Puerto (interfaz)

```python
class ComplianceOfficerPort:
    async def evaluate_request(self, event: RequestReceived | RequestClassified) -> ComplianceDecision:
        """
        Evaluación síncrona EN LA RUTA CRÍTICA.
        Retorna: allow | block | allow_with_modifications
        Si block: publica guardrail.triggered inmediatamente.
        Latencia máxima: 100ms.
        """

    async def evaluate_output(self, event: ResponseSynthesized) -> ComplianceDecision:
        """
        Evaluación síncrona del output ANTES de entregar al usuario.
        Puede modificar o bloquear la respuesta.
        """

    async def evaluate_doctrine(self, event: DoctrineProposed) -> ComplianceDecision:
        """
        Evaluación de doctrinas candidatas antes de publicarse.
        Puede bloquear una doctrina que viole políticas de seguridad/fairness.
        """

    async def handle_audit_finding(self, event: AuditFindingOpened) -> None:
        """
        Recibe hallazgos del Auditor. Decide si escalar a operador o iniciar rollback.
        """
```

---

## 5. Eventos que publica

| Evento | Cuándo |
|---|---|
| `guardrail.triggered` | Al bloquear cualquier acción en cualquier punto |
| `audit.finding.opened` | Al detectar patrón de violación sistémica |

---

## 6. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `request.received` | API Gateway | Evaluación de entrada (async paralela) |
| `request.classified` | Router/Triage | Verificación de clasificación sensitive |
| `response.synthesized` | Meta-Orchestrator | Evaluación de output antes de entrega |
| `doctrine.proposed` | Doctrine Publisher | Aprobación/bloqueo de doctrina |
| `audit.finding.opened` | Auditor | Escalamiento o rollback |

---

## 7. Estado que posee

- **PostgreSQL** (`compliance_rules`): catálogo de reglas y políticas vigentes. Versionado.
- **PostgreSQL** (`guardrail_events`): historial de todos los vetos (auditable).
- **Redis** (`compliance_cache:<hash_rule_set>`): caché de evaluaciones recientes idénticas (TTL = 1min).

---

## 8. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia de evaluación síncrona p99 | < 100ms |
| Disponibilidad | 99.99% (más alto del sistema) |
| Tasa de falsos positivos (bloqueos indebidos) | < 0.5% (medida por Auditor) |
| Tasa de falsos negativos (outputs peligrosos entregados) | 0% idealmente; alerta si > 0 |

---

## 9. Decisiones que puede tomar sin escalar

- Bloquear cualquier petición o output que viole las políticas activas.
- Modificar un output para quitar información sensible (en lugar de bloquear).
- Bloquear el despliegue de una doctrina que viole fairness o seguridad.
- Emitir `guardrail.triggered` sin consultar a nadie.

---

## 10. Cuándo escala

- Incidente grave (patrón de bypass, falla de políticas críticas) → alerta directa al operador humano.
- Ambigüedad sobre si una acción viola política → falla conservadoramente (bloquea) y registra para revisión.
- **Nunca**: el Compliance Officer no pide permiso para vetar. Veta y notifica.

---

## 11. Métricas de calidad propias

- `compliance.guardrail.trigger_rate` — % de peticiones vetadas (gauge)
- `compliance.guardrail.by_category` — distribución de vetos por categoría de violación (histogram)
- `compliance.evaluation.latency_ms` — latencia de evaluación (histogram, p50/p95/p99)
- `compliance.false_positive_rate` — estimado mensual por Auditor (gauge)
- `compliance.doctrine_blocks` — doctrinas bloqueadas en el mes (counter)

---

## Notas de implementación

- La evaluación síncrona en ruta crítica **debe estar cacheada para casos comunes**. El vector de ataque más peligroso es una avalancha de peticiones que saturen este módulo.
- Las reglas de compliance deben estar en un formato declarativo (YAML/JSON), no en código, para que el operador pueda actualizar sin redeploy.
- Dos modos de falla: (1) falla abierta (permite paso) — PROHIBIDO para compliance; (2) falla cerrada (bloquea) — OBLIGATORIO.
- En caso de que el servicio de compliance esté caído, el API Gateway debe bloquear todas las peticiones. No hay degradación graceful aquí.

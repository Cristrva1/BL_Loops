# Guild de Calidad (QA)

> **Status**: `draft` | Anillo: Guild (2) | Última revisión: 2026-05-07

---

## 1. Propósito

Evaluar cada output antes de entregarlo al usuario, asegurando que cumple los estándares de calidad definidos (corrección, completitud, coherencia con el perfil del usuario y ausencia de alucinaciones detectables).

---

## 2. Anillo y rol

- **Anillo**: 2 — Guilds
- **Rol análogo**: Coordinador de Calidad / QA Lead
- **Patrón**: Gate síncrono en la ruta de respuesta + evaluador asíncrono post-entrega

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator
- **Dirige a**: especialistas de evaluación (fact-checker, coherence-checker, style-checker)
- **Alimenta a**: Auditor (envía evaluaciones para análisis post-hoc)

---

## 4. Puerto (interfaz)

```python
class QAGuildPort:
    async def evaluate_output(self, event: ResponseSynthesized) -> QADecision:
        """
        Evaluación pre-entrega. Síncrona, en ruta crítica.
        Retorna: pass | fail | pass_with_warnings
        Si fail: publica task.dispatched hacia el guild que generó el output para corrección.
        Latencia objetivo: < 1s para QA liviano; < 3s para QA profundo.
        """

    async def evaluate_task_result(self, event: TaskCompleted) -> QADecision:
        """
        Evaluación de resultados intermedios de guilds antes de pasar a síntesis.
        Puede rechazar y solicitar re-trabajo al guild origen.
        """

    async def post_delivery_eval(self, event: ResponseDelivered) -> None:
        """
        Evaluación asíncrona post-entrega. Más profunda. No bloquea al usuario.
        Publica: audit.finding.opened si detecta problema grave.
        """
```

---

## 5. Criterios de evaluación

| Criterio | Peso | Método de evaluación |
|---|---|---|
| Corrección factual | 30% | LLM evaluador + fact-checking contra fuentes |
| Completitud | 20% | Cobertura de la petición original |
| Coherencia con perfil | 20% | Comparación con preferencias del User Profiler |
| Formato correcto | 15% | Validación estructural (markdown, código, etc.) |
| Ausencia de alucinaciones | 15% | Grounding check contra contexto provisto |

**Umbral de aprobación**: score ≥ 0.75 (configurable por doctrina).

---

## 6. Eventos que publica

| Evento | Cuándo |
|---|---|
| `task.completed` | Al aprobar un output (pasa la evaluación) |
| `task.failed` | Al rechazar un output (solicita corrección) |
| `audit.finding.opened` | Al detectar patrón de calidad baja sistemática |

---

## 7. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `response.synthesized` | Meta-Orchestrator | Evaluación pre-entrega |
| `task.completed` | Cualquier guild | Evaluación intermedia (si está habilitada) |
| `doctrine.published` | Doctrine Publisher | Actualizar umbrales y criterios de evaluación |
| `user.profile.updated` | User Profiler | Actualizar criterio de coherencia con perfil |

---

## 8. Estado que posee

- **Sin estado propio de larga duración**; consume el perfil del User Profiler y los criterios de doctrinas activas.
- **PostgreSQL** (`qa_evaluations`): historial de evaluaciones para análisis del Auditor.

---

## 9. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia QA liviano p95 | < 1s |
| Latencia QA profundo p95 | < 3s |
| Tasa de aprobación al primer intento | > 85% (KR del OKR-B) |
| Tasa de falsos negativos (outputs malos que pasaron) | < 2% |
| Disponibilidad | 99.9% |

---

## 10. Decisiones que puede tomar sin escalar

- Aprobar, rechazar o aprobar con advertencias cualquier output.
- Solicitar corrección a un guild hasta 2 veces antes de escalar.
- Elegir entre QA liviano (rápido) o profundo (completo) según la clasificación de la petición.

---

## 11. Cuándo escala

- Más de 3 rechazos consecutivos del mismo guild → escala al Meta-Orchestrator para cambiar de guild o estrategia.
- Detección de patrón sistemático de baja calidad → `audit.finding.opened` para el Auditor.
- Output potencialmente peligroso que Compliance Officer no capturó → alerta directa al Compliance Officer.

---

## 12. Métricas de calidad propias

- `qa.pass_rate` — % de outputs que pasan en primera evaluación (gauge, KPI cardinal)
- `qa.rejection_by_criterion` — distribución de rechazos por criterio (histogram)
- `qa.evaluation_latency_ms` — latencia de evaluación liviana vs. profunda (histogram)
- `qa.post_delivery_issues_rate` — problemas detectados post-entrega (gauge)
- `qa.correction_cycles` — distribución de ciclos de corrección por petición (histogram)

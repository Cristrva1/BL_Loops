# Auditor

> **Status**: `stub` | Anillo: Transversal | Última revisión: 2026-05-07

## 1. Propósito

Revisar decisiones post-hoc, detectar drift y degradación silenciosa. Reporta solo al Meta-Orchestrator. Opera con muestra ciega para evitar sesgo de confirmación.

## 2. Anillo y rol

- **Anillo**: Transversal
- **Rol análogo**: Internal Affairs / Auditor independiente
- **Patrón**: Batch evaluator + Adversarial metrics

## 3. Reporta a / Dirige a

- **Reporta exclusivamente a**: Meta-Orchestrator
- **Alimenta a**: Pattern Miner (con hallazgos), Telemetry/SRE (con alertas de drift)

## 4. Puerto (interfaz) — pendiente de especificar

```python
class AuditorPort:
    async def audit_sample(self, sample: list[ResponseDelivered]) -> AuditReport:
        """
        Evalúa muestra ciega de respuestas entregadas.
        Compara con respuesta esperada de fuente independiente.
        """

    async def detect_drift(self, kpi_window: KPIWindow) -> list[DriftSignal]:
        """
        Analiza tendencias de KPIs para detectar degradación.
        Emite drift.detected si supera umbral.
        """
```

## 5. Métricas adversariales (anti-drift)

- Evalúa outputs con evaluador **independiente del que los generó**
- Mide si la satisfacción del usuario y la calidad real divergen
- Detecta optimización de proxy metrics (aparentar mejor, no serlo)

> **TODO**: Completar. Prioridad: fase 6 (QA/Auditor).

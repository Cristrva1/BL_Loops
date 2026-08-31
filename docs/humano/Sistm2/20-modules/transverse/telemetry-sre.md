# Telemetry / SRE

> **Status**: `draft` | Anillo: Transversal | Última revisión: 2026-05-07

---

## 1. Propósito

Recopilar, agregar y exponer métricas, trazas y logs de todos los módulos del sistema. Detectar anomalías en tiempo real y disparar alertas cuando se incumplen SLOs o se detecta drift.

---

## 2. Anillo y rol

- **Anillo**: Transversal (observa los tres anillos)
- **Rol análogo**: SRE / CTO de infraestructura
- **Patrón**: Observer + Alert Manager

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator (alertas) y operador humano (dashboard)
- **Dirige a**: nada; solo observa y alerta
- **Alimenta a**: Auditor (con datos de salud del sistema), Pattern Miner (con telemetría agregada)

---

## 4. Puerto (interfaz)

```python
class TelemetrySREPort:
    async def ingest_event(self, event: BaseEvent) -> None:
        """
        Consume cualquier evento del bus para extraer métricas.
        Latencia de procesamiento: < 50ms (no bloquea el productor).
        """

    async def record_span(self, span: OTelSpan) -> None:
        """
        Recibe trazas de OpenTelemetry de todos los módulos.
        """

    async def check_slos(self) -> list[SLOStatus]:
        """
        Evaluación periódica (cada 60s) de todos los SLOs registrados.
        Si alguno se incumple: publica slo.breached.
        """

    async def detect_drift(self) -> list[DriftSignal]:
        """
        Análisis de tendencias para detectar degradación silenciosa.
        Frecuencia: cada 1h.
        Si detecta drift: publica drift.detected.
        """

    def get_dashboard_data(self) -> DashboardSnapshot:
        """
        Agrega KPIs cardinales para el dashboard del operador.
        """
```

---

## 5. Eventos que publica

| Evento | Cuándo |
|---|---|
| `slo.breached` | Cuando un módulo incumple su SLO |
| `drift.detected` | Al detectar degradación estadística de un KPI |

---

## 6. Eventos que consume

Todos. El Telemetry/SRE suscribe a `>` (wildcard NATS) para observar el sistema completo. Filtra y procesa los que tienen métricas relevantes.

Eventos de atención especial:

| Evento | Métrica extraída |
|---|---|
| `request.received` | Tasa de entrada (req/s) |
| `response.delivered` | Latencia end-to-end, tokens totales |
| `task.completed` | Latencia por guild, tokens por tarea |
| `task.failed` | Error rate por guild |
| `guardrail.triggered` | Compliance event rate |
| `doctrine.published` | Velocidad del learning loop |
| `qa.pass` / `qa.fail` | Tasa de calidad al primer intento |

---

## 7. Estado que posee

- **PostgreSQL** (`kpi_rollups`): agregaciones horarias/diarias de todos los KPIs cardinales.
- **OpenTelemetry Collector**: recibe trazas y métricas vía OTLP; exporta a Grafana/Prometheus.
- **Redis** (`slo_status:<module>`): estado actual de cada SLO para evaluación rápida.

---

## 8. SLOs del propio módulo

| Métrica | Objetivo |
|---|---|
| Latencia de ingesta de eventos p99 | < 50ms |
| Cobertura de eventos procesados | 100% (KR cardinal) |
| Disponibilidad | 99.9% |
| Latencia de alerta `slo.breached` desde detección | < 30s |

---

## 9. KPIs cardinales que monitorea

### Calidad
- `kpi.quality.qa_pass_rate` — % outputs que pasan QA al primer intento
- `kpi.quality.post_delivery_correction_rate` — correcciones post-entrega

### Eficiencia
- `kpi.efficiency.tokens_per_request` — tokens promedio por petición exitosa (p50/p95)
- `kpi.efficiency.latency_ms` — latencia end-to-end (p50/p95/p99)
- `kpi.efficiency.cost_per_request` — costo estimado en USD por petición

### Aprendizaje
- `kpi.learning.patterns_detected_monthly` — patrones detectados por el Pattern Miner
- `kpi.learning.doctrines_promoted_monthly` — doctrinas promovidas
- `kpi.learning.doctrine_lift_avg` — lift promedio de doctrinas activas

### Satisfacción
- `kpi.satisfaction.explicit_rating_avg` — rating explícito promedio (si disponible)
- `kpi.satisfaction.reprompt_rate` — % de peticiones que generan un re-prompt inmediato

### Salud
- `kpi.health.error_rate` — error rate global del sistema
- `kpi.health.slo_breach_count` — SLOs incumplidos en la última hora
- `kpi.health.drift_signals_active` — señales de drift activas

---

## 10. Decisiones que puede tomar sin escalar

- Publicar `slo.breached` sin consultar a nadie.
- Publicar `drift.detected` sin consultar a nadie.
- Ajustar ventanas de agregación según el volumen del sistema.

---

## 11. Cuándo escala

- Incidente P0 (múltiples SLOs críticos incumplidos simultáneamente) → alerta al operador humano y al Meta-Orchestrator.
- Drift detectado en métrica de calidad → alerta al Auditor para revisión profunda.

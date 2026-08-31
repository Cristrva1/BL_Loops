# OKRs y KPIs

> **Status**: `draft` | Última revisión: 2026-05-07 | Período: primer ciclo de 6 meses post-MVP

---

## Objetivo A — Calidad sostenida

**OKR-A**: El sistema entrega respuestas de alta calidad de forma consistente.

### Key Results

| KR | Métrica | Baseline (día 0) | Target (6 meses) | Responsable |
|---|---|---|---|---|
| KR-A1 | % outputs aprobados por QA al primer intento | — | ≥ 85% | Guild QA |
| KR-A2 | % peticiones sin activación de fallback | — | ≥ 95% | Meta-Orchestrator |
| KR-A3 | Tasa de re-prompts inmediatos (señal de insatisfacción) | — | ≤ 10% | User Profiler + QA |
| KR-A4 | % interacciones sin guardrail.triggered innecesario (falsos positivos) | — | ≥ 99.5% | Compliance Officer |

---

## Objetivo B — Aprendizaje activo

**OKR-B**: El sistema mejora su comportamiento de forma autónoma y verificable.

### Key Results

| KR | Métrica | Baseline | Target | Responsable |
|---|---|---|---|---|
| KR-B1 | Doctrinas promovidas por mes (con lift positivo) | 0 | ≥ 3 | Doctrine Publisher |
| KR-B2 | Lift promedio de calidad de doctrinas activas | — | ≥ +5% vs baseline | Pattern Miner |
| KR-B3 | Tiempo de ciclo señal→doctrina publicada | — | ≤ 21 días | Todo el eje de aprendizaje |
| KR-B4 | Doctrinas revertidas por efectos negativos | — | ≤ 1/mes | Auditor |

---

## Objetivo C — Eficiencia operativa

**OKR-C**: El sistema opera dentro de los límites de costo y latencia establecidos.

### Key Results

| KR | Métrica | Baseline | Target | Responsable |
|---|---|---|---|---|
| KR-C1 | Latencia p95 end-to-end | — | ≤ 8s | Meta-Orchestrator + Guilds |
| KR-C2 | Tokens promedio por petición exitosa | — | Reducción ≥ 10% respecto a semana 1 | Resource Allocator |
| KR-C3 | Costo estimado por 1000 peticiones | — | Dentro de presupuesto operativo | Resource Allocator |
| KR-C4 | Disponibilidad del sistema | — | ≥ 99.9% | Telemetry/SRE |

---

## Objetivo D — Confianza y seguridad

**OKR-D**: El sistema opera dentro de límites éticos y de privacidad verificables.

### Key Results

| KR | Métrica | Baseline | Target | Responsable |
|---|---|---|---|---|
| KR-D1 | 100% de interacciones con al menos 1 evento de telemetría | — | 100% | Todos los módulos |
| KR-D2 | % de escrituras semánticas que pasaron por Anonymizer | — | 100% | Guild Memoria + Anonymizer |
| KR-D3 | Tiempo de respuesta a solicitudes de borrado GDPR | — | ≤ 48h | Knowledge Officer |
| KR-D4 | Incidentes P0 | — | 0 | Compliance + Telemetry |

---

## KPIs cardinales (tablero principal)

Estos KPIs son la vista ejecutiva del sistema. Se calculan diariamente.

| KPI | Descripción | Fuente | Alerta si |
|---|---|---|---|
| `qa.pass_rate_7d` | Tasa de aprobación QA (últimos 7 días) | Guild QA | < 80% |
| `latency.p95_24h` | Latencia p95 end-to-end (últimas 24h) | Telemetry | > 10s |
| `learning.doctrines_active` | Doctrinas activas con lift positivo | Doctrine Pub. | = 0 durante > 30 días |
| `efficiency.tokens_per_request_7d` | Tokens promedio por petición (7 días) | Telemetry | Aumento > 20% semana a semana |
| `health.error_rate_1h` | Error rate global (última hora) | Telemetry | > 1% |
| `health.slo_breaches_24h` | SLOs incumplidos (últimas 24h) | Telemetry | > 3 |
| `safety.guardrail_rate_7d` | % peticiones con guardrail activado | Compliance | > 2% (puede indicar problema) |

---

## Revisión y cadencia

- **Diaria**: KPIs cardinales en dashboard (Telemetry/SRE, automático).
- **Semanal**: revisión de tendencias y señales de drift (Auditor + KO, 30min).
- **Mensual**: revisión de OKRs y ajuste de targets si los datos lo justifican (operador + equipo).
- **Por ciclo de aprendizaje**: revisión de doctrinas completadas, lecciones y próximos experimentos (KO + Doctrine Publisher).

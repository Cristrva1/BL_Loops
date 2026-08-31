# Rituales operativos

> **Status**: `draft` | Última revisión: 2026-05-07

Cadencia y estructura de las revisiones recurrentes del sistema.

---

## Rituales regulares

### Daily — Revisión de salud (5 min, automático)

- **Quién**: Telemetry/SRE (automático). El operador revisa el dashboard si hay alertas.
- **Qué se revisa**: KPIs cardinales de las últimas 24h. SLO breaches. Guardrail rate. Error rate.
- **Output**: ninguno si todo está verde. Ticket si hay alerta activa.
- **Cuándo**: cada día a las 08:00 UTC (generación automática del snapshot diario).

---

### Weekly — Revisión de tendencias (30 min)

- **Quién**: Auditor + Knowledge Officer + (opcional) operador.
- **Agenda**:
  1. Tendencias de KPIs de la semana vs. semana anterior.
  2. Patrones detectados por el Pattern Miner esta semana.
  3. Estado de experimentos A/B activos.
  4. Audit findings abiertos — revisión de progreso.
  5. Señales de drift — ¿se confirmaron o cerraron?
- **Output**: decisión sobre si proponer nueva doctrina o cerrar experimentos.

---

### Monthly — Revisión de OKRs (60 min)

- **Quién**: operador + todos los responsables de KRs.
- **Agenda**:
  1. Progreso de cada KR (semáforo: verde/amarillo/rojo).
  2. Doctrinas publicadas este mes y su lift real.
  3. Incidentes del mes — post-mortems pendientes.
  4. Ajuste de targets si los datos justifican el cambio.
  5. Prioridades del mes siguiente.
- **Output**: actualización de `okrs-kpis.md` con métricas actuales y targets ajustados.

---

### Por experimento — Revisión de resultados

- **Quién**: Doctrine Publisher + Auditor + Knowledge Officer + Compliance Officer.
- **Trigger**: cuando un experimento A/B concluye (`experiment.concluded`).
- **Agenda**:
  1. Resultados estadísticos (p-value, lift, tamaño de muestra).
  2. Análisis del Auditor (evaluación adversarial).
  3. Decisión: publicar doctrina o archivar.
  4. Si se publica: plan de comunicación a los módulos afectados.
  5. Si se archiva: lecciones aprendidas para la próxima iteración.
- **Output**: doctrina publicada o archivada + nota de lecciones.

---

### Post-mortem de incidentes P1/P0

- **Quién**: operador + módulos afectados.
- **Trigger**: dentro de 48h de cierre del incidente P1; dentro de 24h del P0.
- **Agenda**:
  1. Cronología del incidente (timeline de eventos del event store).
  2. Root cause analysis (sin culpas, solo causas sistémicas).
  3. Acciones correctivas con responsable y fecha.
  4. Cambios en políticas, doctrinas o SLOs si aplica.
- **Output**: documento de post-mortem archivado en `docs/incidents/` (a crear cuando ocurra el primero).

---

## Principios de los rituales

- **Automático primero**: todo lo que el sistema puede calcular y reportar solo, no lo hace un humano.
- **Decisiones humanas donde importa**: el operador toma decisiones sobre doctrinas críticas, incidentes graves y cambios de OKR.
- **Sin reuniones de status puro**: si no hay decisión que tomar o anomalía que revisar, el ritual se salta o se reduce a leer el dashboard.
- **El event store como minuta**: cualquier decisión que afecte el comportamiento del sistema queda registrada como evento (`doctrine.published`, `audit.finding.opened`, etc.).

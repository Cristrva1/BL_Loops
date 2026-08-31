# Checklist de preparación para producción

> **Status**: `draft` | Última revisión: 2026-05-07

Checklist acumulativo. Cada fase debe completar su sección antes de avanzar a la siguiente.

---

## Fase 1 — Núcleo

### Arquitectura y contratos

- [ ] Event store creado con particionado mensual activo
- [ ] Idempotencia de eventos verificada (test: enviar dos veces el mismo event_id)
- [ ] Cadena de causalidad verificada (test: reconstruir árbol de un correlation_id)
- [ ] Streams NATS creados: REQUESTS, TASKS con política de retención configurada
- [ ] DLQ configurado en todos los consumers
- [ ] API Gateway con autenticación JWT funcional
- [ ] Rate limiting activo y probado

### Compliance

- [ ] Al menos 3 reglas de guardrail configuradas
- [ ] Test de bloqueo: petición con contenido prohibido → respuesta fallback
- [ ] Test de paso: petición normal → sin guardrail activado
- [ ] Evento `guardrail.triggered` registrado en event store

### Telemetría básica

- [ ] OTEL traces activos en todos los módulos del núcleo
- [ ] Dashboard muestra: latencia p50/p95, error rate, requests/min
- [ ] SLO de disponibilidad (99.9%) configurado con alerta

### Smoke test

- [ ] Ciclo completo E2E: petición → compliance → planning → guild → QA → entrega
- [ ] Todos los eventos del ciclo presentes en el event store
- [ ] Latencia p95 < 8s en condiciones normales

---

## Fase 2 — Memoria

- [ ] User Profiler persiste y recupera perfil correctamente
- [ ] Memoria episódica almacena resumen (sin texto completo de petición)
- [ ] Segunda petición del mismo usuario muestra adaptación al perfil
- [ ] Test de borrado GDPR: eliminación de perfil + memoria episódica verificada
- [ ] Anonymizer no deja pasar campos: tenant_id, email, nombre propio (test unitario)

---

## Fase 3 — Guilds

- [ ] Guild de Investigación: web search funcional, resultado integrado al plan
- [ ] Guild de Análisis: cálculo simple verificado por QA
- [ ] Guild de Comunicación: output adaptado a formato configurado en perfil
- [ ] Pipeline de 3 guilds: Research → Production → Communication funcional E2E
- [ ] Resource Allocator cancela tarea que excede budget (test con budget = 0)
- [ ] Timeout de guild activo: si un guild no responde, el plan degrada

---

## Fase 4 — QA

- [ ] QA rechaza output con calidad < umbral configurado
- [ ] Sistema genera corrección y QA evalúa de nuevo
- [ ] Máximo 2 reintentos respetado (no bucle infinito)
- [ ] KPI `qa.pass_rate_7d` visible en dashboard

---

## Fase 5 — Telemetría completa

- [ ] KPI rollups diarios generados correctamente
- [ ] SLO breach activa alerta (test: degradar servicio artificialmente)
- [ ] Modo degradado leve activado automáticamente (test: aumentar latencia artificialmente)
- [ ] Modo degradado severo probado
- [ ] Todos los KPIs cardinales del `okrs-kpis.md` visibles en dashboard

---

## Fase 6 — Auditoría

- [ ] Auditor evalúa muestra ciega con evaluador independiente
- [ ] Drift simulado detectado correctamente
- [ ] Audit finding abierto, asignado, y cerrado correctamente
- [ ] Ciclo completo `drift.detected` → `audit.finding.opened` → investigación → `audit.finding.resolved`

---

## Fase 7 — Pattern Miner

- [ ] Batch nocturno ejecutado sin errores
- [ ] Al menos 1 patrón detectado con datos reales
- [ ] Anonimización verificada por auditoría (0 PII en `semantic_memory`)
- [ ] Búsqueda vectorial funcional: query semántica retorna resultados relevantes

---

## Fase 8 — Aprendizaje completo

- [ ] Ciclo completo: patrón → doctrina propuesta → aprobación → experimento → resultado
- [ ] Rollback automático funcional (test: doctrina que degrada KPI)
- [ ] Despliegue canario al 5% verificado (solo el cohort tratamiento recibe la doctrina)
- [ ] Al menos 1 doctrina publicada con lift positivo medido
- [ ] Significancia estadística p < 0.05 en al menos un experimento

---

## Fase 9 — Producción

- [ ] Prueba de carga: 100 req/min sostenido durante 30 min, p95 < 8s
- [ ] Zero-downtime deployment verificado (añadir un nuevo especialista sin detener el sistema)
- [ ] Architecture Guardian rechaza un módulo con contrato inválido (test)
- [ ] Solicitud de borrado GDPR procesada en < 48h (test con tenant real)
- [ ] Post-mortem de al menos 1 incidente real documentado
- [ ] Todos los OKRs del ciclo 1 con datos medibles (aunque no se hayan alcanzado los targets)
- [ ] Roadmap del ciclo 2 definido con datos del ciclo 1

---

## Criterio de "listo para producción" (todos los ítems anteriores completados)

El sistema está listo para operar en producción con usuarios reales cuando:

1. Todas las fases 1–9 tienen checklist completado.
2. La tasa de entrega (con o sin fallback) es ≥ 99.9% en los últimos 7 días de staging.
3. No hay ningún audit finding abierto con severidad CRITICAL.
4. El Compliance Officer ha bloqueado correctamente todos los test cases de safety.
5. Al menos un operador humano ha completado el runbook de incidentes (no documentado aquí, a crear en `docs/runbooks/`).

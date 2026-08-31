# Orden de construcción — 9 fases

> **Status**: `draft` | Última revisión: 2026-05-07

Cada fase produce un sistema **funcional y desplegable**, no un conjunto de módulos incompletos. Se avanza en espiral: núcleo primero, luego capas.

---

## Principios de priorización

- **Núcleo antes que periférico**: el flujo de petición básico debe funcionar antes de añadir capas de aprendizaje.
- **Trazabilidad desde el día 0**: el event store y la telemetría básica se construyen en la fase 1, no después.
- **Compliance no es opcional**: el Compliance Officer se construye en la fase 1 junto con el resto del núcleo.
- **Los guilds son intercambiables**: se añaden uno a uno sin romper el núcleo.
- **El aprendizaje es la última capa**: solo se construye cuando el sistema base es estable y hay suficiente data.

---

## Fase 1 — Núcleo funcional mínimo

**Objetivo**: una petición entra, se evalúa, se ejecuta por un guild simple, y se entrega una respuesta auditada.

**Módulos a construir**:

- Meta-Orchestrator (planificación simple, un guild)
- Router/Triage (clasificación básica)
- Compliance Officer (guardrails básicos: bloques, modificaciones)
- Guild de Producción (un especialista: writer básico)
- Event Store (PostgreSQL, particionado, cadena de causalidad)
- Telemetría básica (OTEL traces, un dashboard mínimo)
- API Gateway (FastAPI, autenticación JWT, rate limiting)
- NATS JetStream (streams básicos: REQUESTS, TASKS)

**Criterio de completitud**:

- Una petición de texto pasa el ciclo completo end-to-end.
- El event store registra todos los eventos del ciclo.
- El Compliance Officer bloquea una petición de prueba con contenido prohibido.
- El dashboard muestra latencia y error rate.

---

## Fase 2 — Memoria y perfil de usuario

**Objetivo**: el sistema recuerda al usuario entre sesiones y adapta sus respuestas.

**Módulos a construir**:

- User Profiler (perfil explícito + inferencia básica)
- Guild de Memoria (capas: trabajo/Redis, episódica/PostgreSQL)
- Anonymizer (frontera PII básica)
- Proyecciones (`requests_view`, `tasks_view`, `user_profiles`)

**Criterio de completitud**:

- Un usuario en la segunda petición recibe una respuesta adaptada a su perfil.
- La memoria episódica almacena un resumen de la interacción anterior.
- El perfil se actualiza con preferencias inferidas.

---

## Fase 3 — Guilds críticos

**Objetivo**: el sistema puede atender peticiones complejas con múltiples guilds.

**Módulos a construir**:

- Guild de Investigación (especialista web-searcher)
- Guild de Análisis (especialista data-analyst)
- Guild de Comunicación (especialista formatter + tone-adaptor)
- Resource Allocator (presupuesto básico de tokens)

**Criterio de completitud**:

- Una petición compleja ("investiga X y escribe un informe") usa 3 guilds en pipeline.
- El Resource Allocator cancela una tarea que excede el budget.
- El sistema entrega una respuesta formateada según las preferencias del usuario.

---

## Fase 4 — QA y ciclo de calidad

**Objetivo**: toda respuesta pasa por un evaluador de calidad antes de ser entregada.

**Módulos a construir**:

- Guild de QA (evaluador de calidad, criterios configurables)
- Ciclo de corrección (hasta 2 reintentos si QA falla)
- KPIs de calidad en el dashboard (qa.pass_rate_7d)

**Criterio de completitud**:

- El QA rechaza un output de baja calidad y el sistema genera uno corregido.
- El dashboard muestra la tasa de aprobación QA por día.

---

## Fase 5 — Telemetría completa y SRE

**Objetivo**: visibilidad operativa completa del sistema.

**Módulos a construir**:

- Telemetry/SRE (KPI rollups, SLO breaches, alertas)
- Dashboard de Grafana completo (todos los KPIs cardinales)
- Modo degradado automático (leve y severo)

**Criterio de completitud**:

- El sistema activa automáticamente modo degradado cuando la latencia supera el SLO.
- El dashboard muestra en tiempo real el estado de todos los SLOs.
- Se puede simular un fallo de guild y verificar que el sistema degrada correctamente.

---

## Fase 6 — Auditoría y detección de drift

**Objetivo**: el sistema puede detectar degradación silenciosa y alertar.

**Módulos a construir**:

- Auditor (evaluación adversarial de muestra ciega)
- Detección de drift (comparación tendencias vs baseline)
- Sistema de audit findings (abrir, investigar, cerrar)

**Criterio de completitud**:

- El Auditor detecta y reporta un drift simulado.
- Un audit finding se abre, se investiga y se cierra con documentación.

---

## Fase 7 — Pattern Miner y señales de aprendizaje

**Objetivo**: el sistema acumula señales de comportamiento y detecta patrones.

**Módulos a construir**:

- Pattern Miner (batch nocturno, clustering)
- Memoria semántica global (pgvector, Anonymizer completo)
- Guild de Aprendizaje (colección de señales + hipótesis)

**Criterio de completitud**:

- El Pattern Miner detecta y reporta un patrón de comportamiento real (no sintético).
- La memoria semántica almacena embeddings anonimizados.
- El Auditor verifica que no hay PII en la memoria semántica.

---

## Fase 8 — Doctrine Publisher y ciclo de aprendizaje completo

**Objetivo**: el sistema puede proponer, experimentar y publicar doctrinas.

**Módulos a construir**:

- Doctrine Publisher (ciclo completo: propuesta → experimento → decisión)
- Knowledge Officer (aprobación de doctrinas)
- Experimentos A/B (routing por cohort, análisis estadístico)

**Criterio de completitud**:

- Una doctrina pasa por el ciclo completo: patrón → propuesta → experimento 7 días → publicación.
- El rollback automático funciona cuando los KPIs del tratamiento caen.
- El dashboard muestra el impacto de la doctrina activa vs. baseline.

---

## Fase 9 — Especialistas adicionales y escalabilidad

**Objetivo**: expandir el catálogo de especialistas y validar la escalabilidad del sistema.

**Actividades**:

- Añadir especialistas de alta prioridad (según señales del Pattern Miner).
- Architecture Guardian (validación formal de contratos).
- Knowledge Officer completo (gestión de retención, GDPR).
- Pruebas de carga (≥ 100 req/min simultáneas).
- Revisión de todos los SLOs con datos reales de producción.
- Primera revisión completa del roadmap con datos de 9 fases.

**Criterio de completitud**:

- El sistema maneja 100 req/min con p95 < 8s.
- Todos los OKRs del primer ciclo de 6 meses tienen datos medibles.
- Al menos 1 doctrina publicada con lift verificado por el Auditor.

# Documentación — Sistema de Orquestación Auto-Mejorante

> **Status general**: `draft` | Última revisión: 2026-05-07
> Stack de referencia: Python 3.11+ · FastAPI · NATS JetStream · PostgreSQL 16 · Redis · OpenTelemetry

Este directorio contiene el diseño técnico detallado del sistema. Es la fuente de verdad de la arquitectura, los módulos, los contratos y la gobernanza. **No contiene código de implementación.**

---

## Mapa de lectura recomendado

Para entender el sistema de arriba a abajo:

1. `00-overview/README.md` — qué es el sistema y cómo navegar la documentación
2. `00-overview/system-context.md` — diagrama C4 nivel 1, actores externos
3. `10-architecture/rings-topology.md` — topología de 3 anillos + eje de aprendizaje
4. `10-architecture/three-flows.md` — los 3 flujos cardinales (petición, memoria, aprendizaje)
5. `20-modules/core/meta-orchestrator.md` — el módulo central del sistema
6. `30-contracts/conventions.md` — cómo nombrar y versionar eventos
7. `40-data/postgres-schema.sql` — el modelo de datos completo
8. `90-roadmap/construction-order.md` — 9 fases de construcción ordenadas por dependencia

---

## Estructura de directorios

```
docs/
├── 00-overview/              Introducción, glosario y contexto del sistema
│   ├── README.md             Índice y guía de lectura de la documentación
│   ├── glossary.md           Definición de todos los términos clave
│   └── system-context.md     Diagrama C4 nivel 1 (sistema ↔ mundo externo)
│
├── 10-architecture/          Arquitectura técnica del sistema
│   ├── rings-topology.md     Topología de 3 anillos + eje transversal
│   ├── three-flows.md        Flujos de petición, memoria y aprendizaje
│   ├── deployment-topology.md Servicios, comunicación y escalado
│   └── c4-containers.md      Diagrama C4 nivel 2 (contenedores)
│
├── 20-modules/               Fichas detalladas de todos los módulos
│   ├── core/                 Anillo 1 — Núcleo (Meta-Orchestrator, Router, Compliance, etc.)
│   ├── guilds/               Anillo 2 — Coordinadores de dominio
│   ├── specialists/          Anillo 3 — Agentes tácticos intercambiables
│   └── transverse/           Módulos que cruzan todos los anillos
│
├── 30-contracts/             Contratos de eventos y APIs
│   ├── conventions.md        Naming, versioning y estructura canónica de eventos
│   ├── event-catalog.md      Registro de todos los eventos del sistema
│   └── events/               JSON Schemas de eventos (uno por archivo)
│
├── 40-data/                  Modelo de datos
│   ├── postgres-schema.sql   Schema SQL completo de referencia
│   ├── event-store.md        Log inmutable — principios y consultas
│   ├── projections.md        Vistas materializadas derivadas del event store
│   └── memory-layers.md      Las 3 capas de memoria (trabajo, episódica, semántica)
│
├── 50-flows/                 Diagramas de flujos cardinales (Mermaid)
│   ├── 01-request-flow.md    Ciclo completo de una petición (entrada → entrega)
│   ├── 02-learning-flow.md   Ciclo de aprendizaje (señal → doctrina publicada)
│   ├── 03-federation-flow.md Federación y delegación entre guilds
│   └── 04-escalation-flow.md Escalación, incidentes y rollbacks
│
├── 60-governance/            Gobernanza operativa
│   ├── raci.md               Matriz de responsabilidades (RACI)
│   ├── okrs-kpis.md          Objetivos, Key Results y KPIs cardinales
│   └── rituals.md            Cadencia y agenda de revisiones recurrentes
│
├── 70-adr/                   Architecture Decision Records
│   ├── ADR-0001-event-sourcing.md
│   ├── ADR-0002-nats-jetstream.md
│   ├── ADR-0003-orchestration-over-choreography.md
│   ├── ADR-0004-ring-topology.md
│   ├── ADR-0005-pgvector-semantic-memory.md
│   ├── ADR-0006-canary-doctrine-deployment.md
│   └── ADR-0007-anonymizer-boundary.md
│
└── 90-roadmap/               Plan de construcción
    ├── construction-order.md  9 fases ordenadas por dependencia
    └── readiness-checklist.md Checklist acumulativo de preparación para producción
```

---

## Estado por sección

| Sección | Estado | Notas |
|---|---|---|
| `00-overview` | `draft` | Completo |
| `10-architecture` | `draft` | Completo |
| `20-modules/core` | `draft` | 3 fichas completas; 3 stubs |
| `20-modules/guilds` | `draft` | 2 fichas completas; 5 stubs |
| `20-modules/transverse` | `draft` | 2 fichas completas; 3 stubs |
| `20-modules/specialists` | `draft` | Interfaz genérica completa |
| `30-contracts` | `draft` | 4 schemas completos; 16 pendientes (ver catálogo) |
| `40-data` | `draft` | Completo |
| `50-flows` | `draft` | Completo |
| `60-governance` | `draft` | Completo |
| `70-adr` | `draft` | 7 ADRs completos |
| `90-roadmap` | `draft` | Completo |

---

## Convenciones de esta documentación

- **`draft`**: contenido revisable, no congelado. Puede cambiar antes de la implementación.
- **`stub`**: esqueleto con propósito y contratos, pendiente de secciones detalladas.
- **`accepted`**: decisiones de arquitectura aceptadas. Requieren nuevo ADR para cambiar.
- Los diagramas usan sintaxis **Mermaid** (compatible con GitHub, GitLab y la mayoría de wikis).
- Los contratos usan **JSON Schema draft-07**.
- Los flujos de código de referencia usan Python (sin implementación real).

---

## Próximos pasos (para completar el diseño)

1. Completar fichas de módulos con status `stub` (secciones 5–11 del template).
2. Crear los 16 JSON Schemas de eventos pendientes (ver `30-contracts/event-catalog.md`).
3. Revisar y validar el `postgres-schema.sql` con el equipo de datos antes de la Fase 1.
4. Definir las políticas de retención exactas en `40-data/memory-layers.md`.
5. Crear `docs/runbooks/` con el runbook de incidentes antes del go-live.

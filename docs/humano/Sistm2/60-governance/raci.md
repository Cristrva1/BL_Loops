# Matriz RACI

> **Status**: `draft` | Última revisión: 2026-05-07

R = Responsable (ejecuta) | A = Accountable (rinde cuentas) | C = Consultado | I = Informado

---

## Actividades del ciclo de petición

| Actividad | Meta-Orch | Router | Compliance | Guilds | QA | User Profiler | Telemetry | Operador |
|---|---|---|---|---|---|---|---|---|
| Recibir petición | A | I | C | I | — | I | I | — |
| Clasificar petición | C | R,A | C | — | — | I | I | — |
| Evaluar seguridad de entrada | I | I | R,A | — | — | — | I | I |
| Planificar ejecución | R,A | C | — | I | — | C | I | — |
| Asignar presupuesto | A | — | — | I | — | — | R | — |
| Ejecutar tareas de guild | A | — | — | R | — | — | I | — |
| Evaluar calidad del output | A | — | C | I | R | C | I | — |
| Evaluar seguridad del output | I | — | R,A | — | C | — | I | I |
| Sintetizar respuesta | R,A | — | — | I | C | — | I | — |
| Entregar respuesta | R,A | — | I | — | — | I | I | — |
| Actualizar perfil de usuario | A | — | — | — | — | R | I | — |

---

## Actividades del ciclo de aprendizaje

| Actividad | KO | Compliance | Pattern Miner | Doctrine Pub. | Auditor | Telemetry | Operador |
|---|---|---|---|---|---|---|---|
| Anonimizar señales | A | C | R | — | I | I | — |
| Minar patrones | A | — | R | I | C | I | — |
| Proponer doctrina | A | C | R | I | I | I | — |
| Aprobar doctrina | A | R | C | I | C | I | I |
| Diseñar experimento A/B | C | C | C | R,A | I | I | I |
| Operar experimento | C | I | I | R,A | C | R | I |
| Evaluar experimento | C | I | C | R,A | R | C | I |
| Publicar doctrina | A | C | I | R | I | I | I |
| Revertir doctrina | A | R | I | R | R | C | I |

---

## Actividades de incidentes y gobernanza

| Actividad | Meta-Orch | Compliance | Auditor | Telemetry | KO | Operador |
|---|---|---|---|---|---|---|
| Detectar SLO breach | I | I | I | R,A | — | I |
| Activar modo degradado | R,A | I | I | C | — | I |
| Abrir audit finding | — | C | R,A | C | I | I |
| Investigar audit finding | I | C | R,A | C | C | I |
| Aprobar rollback de doctrina | A | R | C | — | C | I |
| Escalar a operador humano | I | R | R | R | I | A |
| Cerrar incidente | I | C | C | C | — | R,A |

---

## Actividades de arquitectura y cambios

| Actividad | Arch. Guardian | KO | Compliance | Operador |
|---|---|---|---|---|
| Registrar nuevo módulo | R,A | C | C | I |
| Validar contrato de módulo | R,A | I | C | I |
| Aprobar cambio de esquema de evento | R,A | C | C | I |
| Aprobar nueva política de compliance | C | C | R,A | I |
| Aprobar cambio de retención de datos | C | R,A | C | I |

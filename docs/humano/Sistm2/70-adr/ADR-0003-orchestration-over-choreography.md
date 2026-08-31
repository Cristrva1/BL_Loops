# ADR-0003 — Orquestación sobre coreografía para el flujo principal

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

En un sistema multi-agente distribuido, hay dos estilos principales de coordinación:
- **Orquestación**: un módulo central coordina explícitamente los pasos y el flujo.
- **Coreografía**: cada módulo reacciona a eventos de otros módulos sin coordinador central.

El sistema tiene un Meta-Orchestrator (CEO) que debe garantizar la entrega de respuestas y controlar el presupuesto de recursos.

---

## Decisión

**Adoptamos orquestación para el flujo principal** (ciclo de petición). El Meta-Orchestrator es el único coordinador del ciclo de vida de una petición: construye el plan, despacha tareas, recibe resultados y sintetiza la respuesta.

**Adoptamos coreografía para el eje de aprendizaje**: el ciclo pattern → doctrina → despliegue sigue un modelo event-driven donde cada módulo reacciona al evento del anterior, sin un coordinador central.

---

## Consecuencias positivas — Orquestación

- **Visibilidad total**: el Meta-Orchestrator sabe en todo momento el estado del plan.
- **Control de presupuesto**: puede detener o degradar el plan si el presupuesto se agota.
- **Manejo de errores centralizado**: si un guild falla, el MO decide reintentar, degradar o fallar.
- **Saga pattern**: implementa el patrón Saga orquestada, que garantiza compensaciones consistentes.
- **Debugging simple**: el log del MO es el "mapa" de lo que ocurrió.

---

## Consecuencias negativas — Orquestación

- **Cuello de botella potencial**: el MO es un punto de fallo único en el flujo de petición.
- **Mayor acoplamiento**: los guilds dependen del MO para recibir tareas (pero el MO no depende de los guilds concretos, solo del contrato).
- **Escalabilidad**: múltiples instancias del MO requieren coordinación (resuelta con el state en Redis por `correlation_id`).

---

## Consecuencias positivas — Coreografía en el eje de aprendizaje

- **Desacoplamiento**: el Pattern Miner no sabe de Doctrine Publisher; solo publica `pattern.detected`.
- **Extensibilidad**: se puede añadir un nuevo paso al ciclo de aprendizaje sin modificar los módulos existentes.
- **Resiliencia**: si el KO está caído, los patrones se acumulan en el stream y se procesan cuando se recupera.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Coreografía pura para todo | Difícil de rastrear el estado de una petición; sin control de presupuesto; debugging complejo |
| Orquestación para el eje de aprendizaje | Introduce acoplamiento innecesario en un flujo que es inherentemente asíncrono y batch |
| Microkernel / Workflow engine externo | Complejidad adicional; no justificada en las fases iniciales |

---

## Revisión

Esta decisión se revisará si el Meta-Orchestrator se convierte en un cuello de botella real (> 1000 req/s simultáneas). En ese caso, se evaluará sharding del MO por tenant o migración parcial a coreografía para subtareas independientes.

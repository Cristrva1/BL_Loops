# ADR-0004 — Topología de 3 anillos para los módulos

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema tiene múltiples módulos con diferentes niveles de responsabilidad, estabilidad requerida y frecuencia de cambio. Se necesita una forma de organizar los módulos que refleje su criticidad y sus relaciones de dependencia.

---

## Decisión

**Adoptamos una topología de 3 anillos concéntricos** más un eje transversal:

- **Anillo 1 — Core**: módulos que nunca cambian de contrato sin proceso de ADR. Alta estabilidad requerida.
- **Anillo 2 — Guilds**: módulos intercambiables con el mismo contrato base. Pueden cambiar internamente sin afectar el sistema.
- **Anillo 3 — Especialistas**: agentes tácticos completamente reemplazables. Máxima volatilidad permitida.
- **Eje transversal**: módulos que cruzan todos los anillos (User Profiler, Auditor, Pattern Miner, Doctrine Publisher, Telemetry).

La regla de dependencia: **las dependencias solo fluyen hacia adentro**. Los módulos del anillo exterior pueden depender de los del interior, pero no al revés.

---

## Consecuencias positivas

- **Estabilidad diferenciada**: los módulos del Core tienen contratos estables; los especialistas pueden cambiar continuamente.
- **Evolución controlada**: añadir un nuevo especialista no requiere ningún cambio en Core ni en los Guilds.
- **Modularidad real**: se puede reemplazar cualquier guild o especialista en caliente sin parar el sistema.
- **Analogía organizacional**: la topología de anillos mapea directamente con la jerarquía de roles (CEO, Chief of Staff, Coordinadores, Especialistas), facilitando el razonamiento sobre el sistema.

---

## Consecuencias negativas

- **Rigidez del Core**: cambiar un contrato de Core requiere proceso formal (ADR). Esto es intencional pero puede ralentizar iteraciones tempranas.
- **Complejidad conceptual**: los módulos transversales no encajan perfectamente en la metáfora de anillos.
- **Sub-delegación controlada**: los guilds pueden llamarse entre sí (un nivel), lo que requiere vigilancia para no crear dependencias circulares.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Flat (todos los módulos al mismo nivel) | Sin diferenciación de estabilidad; cualquier cambio puede romper cualquier cosa |
| Jerarquía estricta (árbol) | Los módulos transversales (Telemetry, Auditor) no encajan en un árbol; requieren acceso lateral |
| Microservicios sin topología | Máxima flexibilidad pero sin límites claros de estabilidad; difícil de razonar |

---

## Revisión

Esta decisión es estructural y se revisará solo si la topología impide el crecimiento del sistema (por ejemplo, si se necesitan más de 3 niveles de coordinación). No se anticipa revisión en las primeras 9 fases del roadmap.

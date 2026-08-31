# Glosario canónico

> **Status**: `draft` | Última revisión: 2026-05-07

Términos con definición oficial para este sistema. Ante conflicto entre este glosario y cualquier otro documento, **este glosario gana**.

---

## A

**Agente**
Unidad autónoma que puede percibir estado, tomar decisiones y ejecutar acciones. En este sistema, un agente siempre expone un *puerto* y publica/consume *eventos*. Puede ser un LLM con herramientas, un script, un servicio externo o cualquier combinación.

**Anonymizer**
Componente obligatorio que transforma datos per-usuario antes de que salgan del perímetro individual hacia la memoria global. Elimina PII y datos identificables; solo viajan *patrones*. Ver ADR-0007.

**Auditor**
Rol transversal que revisa decisiones post-hoc, detecta *drift* y degradación. Reporta solo al Meta-Orchestrator. Distinto del módulo *QA* (que opera en tiempo real sobre cada output).

---

## C

**Cadena de causalidad**
Traza de eventos relacionados mediante `correlation_id` (petición única) y `causation_id` (evento padre). Permite reconstruir el historial completo de cualquier interacción.

**Compliance Officer (Guardrails)**
Módulo C-Level con poder de **veto absoluto**. Único módulo que suplanta (no solo veta) decisiones de niveles superiores. Opera síncronamente en la ruta crítica.

**Control Plane**
Plano que decide qué hacer: Meta-Orchestrator, Router, Planificador, Coordinadores de guild. Nunca ejecuta trabajo directamente.

**Correlation ID**
UUID que identifica una petición de extremo a extremo. Todos los eventos de esa petición lo comparten.

---

## D

**Data Plane**
Plano que ejecuta: Especialistas, herramientas externas, LLMs, APIs. Recibe tareas del Control Plane y devuelve resultados.

**Doctrina**
Conocimiento validado que pasa de *patrón detectado* a *política activa*. Se almacena en la tabla `doctrines` y se despliega como actualización de prompt/política/router. Las doctrinas tienen versión, estado (`proposed|active|retired`) y *lift* medido.

**Drift**
Degradación silenciosa del rendimiento del sistema a lo largo del tiempo. Causa: el sistema optimiza la métrica definida, no la intención real. Detectado por el Auditor vía métricas adversariales.

---

## E

**Event Bus**
NATS JetStream. Sistema nervioso central. Todo agente publica y consume eventos por aquí. Agregar un nuevo módulo = suscribirlo al bus.

**Event Store**
Tabla PostgreSQL append-only que es la única fuente de verdad. Nunca se actualiza ni borra. El estado actual se deriva de "doblar" el log.

**Evento**
Hecho ocurrido en el sistema, inmutable. Estructura: `event_id`, `event_type`, `event_version`, `occurred_at`, `producer`, `correlation_id`, `causation_id`, `tenant_id`, `payload`. Ver `30-contracts/conventions.md`.

---

## F

**Federación**
Modelo por el que el aprendizaje sube de perfiles individuales a doctrina global, pasando siempre por el Anonymizer. Inspirado en Federated Learning. Ver `50-flows/federation-loop.md`.

**Falla cerrada**
Principio: cuando el sistema falla, nunca degrada la experiencia del usuario; devuelve un fallback seguro. El aprendizaje y la mejora son abiertos; la falla, no.

---

## G

**Guild**
Unidad de coordinación de dominio (Anillo 2). Agrupa especialistas de un área. Tiene un Coordinador que reporta al Meta-Orchestrator vía Router.

**Guardrail**
Restricción de seguridad/calidad que el Compliance Officer aplica. Dispara el evento `guardrail.triggered` cuando bloquea una acción.

---

## H

**Hub federado en anillos**
Topología elegida para este sistema. Tres anillos concéntricos (Core, Guilds, Specialists) + eje vertical de aprendizaje. Ver `10-architecture/rings-topology.md` y ADR-0001.

---

## K

**KPI cardinal**
Métrica irrenunciable del sistema. Cinco dimensiones: Calidad, Eficiencia, Aprendizaje, Satisfacción, Salud. Ver `60-governance/kpis-catalog.md`.

**KR (Key Result)**
Resultado medible asociado a un OKR. Siempre tiene valor baseline, target y fecha.

---

## L

**Learning Plane**
Plano que mejora al Control Plane y al Data Plane. Opera de forma asíncrona. Componentes: Pattern Miner, Auditor, Doctrine Publisher, Validator A/B.

**Lift**
Mejora medida de una doctrina sobre el baseline. Se calcula comparando KPIs de la cohorte con doctrina vs. cohorte control.

**LLM Gateway**
Capa de abstracción sobre proveedores de LLM (OpenAI, Anthropic, etc.). Todos los especialistas que usan LLMs pasan por aquí. Ver ADR-0006.

---

## M

**Memoria episódica**
Capa de memoria scoped por `user_id`. Almacena interacciones pasadas de ese usuario. Persiste en PostgreSQL.

**Memoria semántica**
Capa de memoria global con embeddings (`pgvector`). Solo contiene datos anonimizados. Sirve para recuperación por similitud semántica.

**Memoria de trabajo**
Capa efímera scoped por `correlation_id`. Redis con TTL corto. Desaparece al terminar la petición.

**Meta-Orchestrator**
Módulo CEO del sistema. Recibe intenciones, asigna recursos, garantiza entrega. No ejecuta trabajo; orquesta. Ver `20-modules/core/meta-orchestrator.md`.

**Módulo**
Unidad del sistema con interfaz estable (puerto), responsabilidades claras y SLOs definidos. Puede reemplazarse internamente sin romper el contrato externo.

---

## O

**OKR (Objective + Key Results)**
Marco de objetivos trimestrales. Un Objetivo + 3–5 KRs medibles. Ver `60-governance/okrs-template.md`.

---

## P

**Patrón**
Señal agregada detectada por el Pattern Miner sobre múltiples interacciones anonimizadas. Candidato a convertirse en doctrina tras validación A/B.

**PII (Personally Identifiable Information)**
Cualquier dato que identifique o pueda identificar a un usuario. Nunca sale del perímetro individual sin pasar por el Anonymizer.

**Puerto (Port)**
Interfaz abstracta de un módulo. Define qué métodos expone y qué eventos produce/consume, sin decir cómo lo hace. Hexagonal Architecture (Cockburn).

**Profile per-usuario**
Registro individual que almacena preferencias, profesión, estilo, historial de un usuario específico. No se globaliza como dato; solo contribuye a patrones anonimizados.

---

## R

**RACI**
Matriz de responsabilidades: Responsible, Accountable, Consulted, Informed. Resuelve la ambigüedad de las tres jerarquías coexistentes. Ver `60-governance/raci-matrix.md`.

**Rollback**
Retiro automático de una doctrina cuando su lift cae por debajo del umbral. Dispara el evento `doctrine.rolled_back`.

**Router / Triage**
Módulo Chief of Staff. Clasifica cada petición: trivial, requiere planificación, delicada, requiere herramientas externas.

---

## S

**SLO (Service Level Objective)**
Objetivo de nivel de servicio de un módulo: latencia, throughput, error budget. Si se incumple, el módulo notifica via `slo.breached`.

**Subsidiariedad**
Regla de delegación: la decisión la toma el nivel más bajo que tenga información completa. No se escala si el especialista puede resolver.

---

## T

**Tenant**
Unidad de aislamiento lógico. Puede ser un usuario, una organización o cualquier entidad con perfil independiente. El campo `tenant_id` aparece en todos los eventos.

---

## V

**Veto descendente**
Niveles superiores pueden vetar pero no suplantar decisiones, **excepto** el Compliance Officer que sí suplanta.

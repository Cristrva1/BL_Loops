# Guild de Memoria

> **Status**: `draft` | Anillo: Guild (2) | Última revisión: 2026-05-07

---

## 1. Propósito

Gestionar todas las operaciones de lectura y escritura sobre las tres capas de memoria del sistema (trabajo, episódica, semántica). Es el único guild que tiene acceso directo a las bases de datos de memoria.

---

## 2. Anillo y rol

- **Anillo**: 2 — Guilds
- **Rol análogo**: Coordinador de Memoria / Chief Memory Officer
- **Patrón**: Repository + Cache-aside

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator (vía Router)
- **Dirige a**: especialistas de memoria (lectura vectorial, lectura episódica, escritura)
- **Técnicamente reporta a**: Knowledge Officer (CKO) para decisiones de retención y descarte

---

## 4. Puerto (interfaz)

```python
class MemoryGuildPort:
    async def read_context(self, task: TaskDispatched) -> MemoryContext:
        """
        Recupera contexto relevante de las tres capas para una petición.
        Orden de prioridad: trabajo > episódica > semántica.
        """

    async def write_working(self, correlation_id: str, data: dict, ttl_seconds: int) -> None:
        """
        Escribe en memoria de trabajo (Redis). TTL = timeout de petición.
        """

    async def write_episodic(self, tenant_id: str, interaction_summary: dict) -> None:
        """
        Persiste resumen de interacción en memoria episódica (PostgreSQL).
        NUNCA escribe el texto completo, solo metadatos y resúmenes.
        """

    async def write_semantic(self, embedding: list[float], metadata: dict) -> None:
        """
        Escribe embedding en memoria semántica (pgvector).
        PRECONDICIÓN: metadata debe estar anonimizado (sin PII).
        """

    async def search_semantic(self, query_embedding: list[float], top_k: int = 5) -> list[MemoryResult]:
        """
        Búsqueda por similitud en pgvector. Solo sobre datos globales anonimizados.
        """
```

---

## 5. Eventos que publica

| Evento | Cuándo |
|---|---|
| `memory.write.committed` | Al confirmar escritura exitosa en cualquier capa |
| `memory.read.served` | Al completar una lectura con los resultados |
| `task.completed` | Al completar la tarea de memoria delegada |

---

## 6. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `task.dispatched` | Meta-Orchestrator | Ejecutar operación de memoria |
| `response.delivered` | Meta-Orchestrator | Trigger para escritura episódica del resultado |
| `doctrine.published` | Doctrine Publisher | Actualizar políticas de retención |

---

## 7. Estado que posee (directo)

- **Redis** (`work:<correlation_id>:*`): memoria de trabajo activa
- **PostgreSQL** (`episodic_memory`): historial por `tenant_id`, particionado por mes
- **PostgreSQL + pgvector** (`semantic_memory`): embeddings globales (anonimizados)
- **NO posee** el perfil de usuario (eso es del User Profiler)

---

## 8. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia `read_context` p95 | < 100ms |
| Latencia `write_working` p95 | < 10ms |
| Latencia `write_episodic` p95 | < 200ms |
| Latencia `search_semantic` p95 | < 300ms |
| Disponibilidad | 99.9% |

---

## 9. Decisiones que puede tomar sin escalar

- Elegir qué capas consultar según el contexto de la tarea.
- Decidir cuántos resultados semánticos devolver (top-k dinámico según presupuesto de tokens).
- Truncar resúmenes episódicos para no exceder el contexto del LLM receptor.
- Descartar resultados semánticos con similitud < umbral mínimo.

---

## 10. Cuándo escala

- Si se solicita escritura en semántica con datos que contienen posible PII → bloquea y alerta al Compliance Officer.
- Si la retención de datos episódicos supera la política de retention → solicita al Knowledge Officer decisión.

---

## 11. Métricas de calidad propias

- `memory.read.cache_hit_rate` — tasa de hits en memoria de trabajo y episódica (gauge)
- `memory.semantic.search_latency_ms` — latencia de búsqueda vectorial (histogram)
- `memory.episodic.records_per_user` — tamaño promedio de historial por usuario activo (histogram)
- `memory.write.episodic_daily` — escrituras episódicas por día (counter)
- `memory.semantic.embedding_count` — total de embeddings en pgvector (gauge)

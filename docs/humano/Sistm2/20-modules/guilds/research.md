# Guild de Investigación

> **Status**: `stub` | Anillo: Guild (2) | Última revisión: 2026-05-07

---

## 1. Propósito

Búsqueda de información, fact-checking y síntesis de fuentes externas e internas. Provee el sustento factual para que otros guilds produzcan outputs correctos.

---

## 2. Especialistas típicos

- `web-searcher` — búsqueda en internet vía herramientas externas
- `deep-reader` — lectura y extracción de documentos largos
- `citation-checker` — validación de referencias
- `contradiction-detector` — detección de inconsistencias entre fuentes

---

## 3. Puerto (interfaz) — pendiente de especificar

```python
class ResearchGuildPort:
    async def research(self, task: TaskDispatched) -> None:
        """
        Ejecuta investigación según las instrucciones de la tarea.
        Publica: task.completed con resultado o task.failed.
        """
```

---

## 4. SLOs (preliminares)

- Latencia p95: < 10s (búsquedas web pueden ser lentas)
- Precisión factual: > 90% (medida por QA)

---

> **TODO**: Completar secciones completas. Prioridad: fase 3 (primeros guilds críticos).

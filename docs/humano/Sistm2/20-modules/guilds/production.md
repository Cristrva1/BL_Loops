# Guild de Producción

> **Status**: `stub` | Anillo: Guild (2) | Última revisión: 2026-05-07

---

## 1. Propósito

Generación de artefactos: textos, código, documentos, reportes, presentaciones. Transforma instrucciones e información en outputs entregables.

---

## 2. Especialistas típicos

- `writer` — redacción de textos, artículos, emails
- `coder` — generación y revisión de código
- `report-builder` — estructuración de reportes y documentos
- `summarizer` — síntesis y resúmenes de contenido largo

---

## 3. Puerto (interfaz) — pendiente de especificar

```python
class ProductionGuildPort:
    async def produce(self, task: TaskDispatched) -> None:
        """
        Genera el artefacto solicitado según instrucciones y contexto.
        Publica: task.completed con artefacto o task.failed.
        """
```

---

## 4. SLOs (preliminares)

- Latencia p95: < 8s
- Calidad: > 85% aprobación QA al primer intento

---

> **TODO**: Completar secciones completas. Prioridad: fase 3 (primeros guilds críticos).

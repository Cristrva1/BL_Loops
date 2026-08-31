# Guild de Análisis

> **Status**: `stub` | Anillo: Guild (2) | Última revisión: 2026-05-07

## 1. Propósito

Procesamiento de datos cuantitativos: cálculos, estadísticas, modelado, análisis de datasets. Transforma datos en insights estructurados.

## 2. Especialistas típicos

- `data-analyst` — análisis estadístico y visualización
- `calculator` — cálculos precisos y verificados
- `modeler` — modelado cuantitativo y simulaciones
- `sql-querier` — consultas a bases de datos

## 3. Puerto (interfaz) — pendiente de especificar

```python
class AnalysisGuildPort:
    async def analyze(self, task: TaskDispatched) -> None: ...
```

## 4. SLOs (preliminares)

- Latencia p95: < 15s (puede requerir procesamiento pesado)
- Precisión numérica: 100% (cero tolerancia a errores de cálculo)

> **TODO**: Completar. Prioridad: fase 3+.

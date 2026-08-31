# Guild de Aprendizaje

> **Status**: `stub` | Anillo: Guild (2) | Última revisión: 2026-05-07

## 1. Propósito

Operar el ciclo de mejora continua del sistema: recopilar señales de aprendizaje, colaborar con el Pattern Miner y coordinar experimentos A/B con el Doctrine Publisher.

## 2. Especialistas típicos

- `signal-collector` — agrega señales de feedback explícito e implícito
- `hypothesis-generator` — formula hipótesis de mejora basadas en patrones
- `experiment-designer` — diseña experimentos A/B controlados

## 3. Puerto (interfaz) — pendiente de especificar

```python
class LearningGuildPort:
    async def process_learning_task(self, task: TaskDispatched) -> None: ...
```

## 4. SLOs (preliminares)

- Tiempo de ciclo completo de aprendizaje (señal → doctrina): < 7 días
- Doctrinas válidas por mes: ≥ 3 (KR del OKR-B)

> **TODO**: Completar. Prioridad: fase 7 (Pattern Miner offline).

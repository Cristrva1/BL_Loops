# Doctrine Publisher

> **Status**: `stub` | Anillo: Transversal | Última revisión: 2026-05-07

## 1. Propósito

Convertir patrones validados en actualizaciones de prompts, políticas y configuraciones de router. Gestionar el ciclo de vida de las doctrinas (propuesta → experimento → aprobación → despliegue → retiro).

## 2. Anillo y rol

- **Anillo**: Transversal
- **Rol análogo**: Change Manager / Release Manager del aprendizaje
- **Patrón**: Event-driven state machine + Canary deployment

## 3. Reporta a / Dirige a

- **Reporta a**: Knowledge Officer (CKO)
- **Requiere aprobación de**: Compliance Officer (para cualquier doctrina)
- **Despliega a**: todos los módulos afectados (vía `doctrine.published`)

## 4. Puerto (interfaz) — pendiente de especificar

```python
class DoctrinePublisherPort:
    async def propose_doctrine(self, pattern: PatternDetected) -> DoctrineProposed:
        """
        Crea propuesta de doctrina a partir de patrón.
        Inicia proceso de aprobación (CKO + Compliance).
        """

    async def start_experiment(self, doctrine: DoctrineApproved) -> ExperimentStarted:
        """
        Despliega doctrina en cohorte canaria (5% del tráfico).
        Emite experiment.started.
        """

    async def conclude_experiment(self, experiment: ExperimentData) -> None:
        """
        Evalúa resultados con significancia estadística.
        Emite doctrine.published (si gana) o doctrine.rolled_back (si pierde).
        """
```

## 5. Reglas del ciclo

- Despliegue siempre en modo canaria (5%) antes de rollout completo.
- Significancia estadística requerida: p < 0.05, mínimo N días configurables.
- Rollback automático si KPIs críticos caen > 2% respecto al baseline.
- Cada experimento archivado siempre, independientemente del resultado.

> **TODO**: Completar. Prioridad: fase 8.

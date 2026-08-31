# Pattern Miner

> **Status**: `stub` | Anillo: Transversal | Última revisión: 2026-05-07

## 1. Propósito

Escanear logs anonimizados buscando patrones de comportamiento: qué prompts funcionan mejor, qué rutas fallan, qué clusters de usuario tienen necesidades similares.

## 2. Anillo y rol

- **Anillo**: Transversal
- **Rol análogo**: Data Scientist / Pattern Analyst
- **Patrón**: Batch pipeline + Clustering

## 3. Reporta a / Dirige a

- **Reporta a**: Knowledge Officer (CKO)
- **Alimenta a**: Doctrine Publisher (con patrones candidatos)

## 4. Puerto (interfaz) — pendiente de especificar

```python
class PatternMinerPort:
    async def mine_patterns(self, time_window: TimeWindow) -> list[PatternCandidate]:
        """
        Analiza eventos anonimizados del período.
        Solo opera sobre datos que pasaron por Anonymizer.
        Emite pattern.detected por cada patrón significativo.
        """
```

## 5. Reglas críticas

- **Solo opera sobre datos anonimizados**. Nunca accede directamente a perfiles per-usuario.
- Resultados ponderados por cluster (no por volumen) para evitar sesgo hacia usuarios más activos.
- Batch nocturno en fases iniciales; streaming suave en fases avanzadas.

> **TODO**: Completar. Prioridad: fase 7.

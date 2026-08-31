# Flujo 2 — Ciclo de aprendizaje

> **Status**: `draft` | Última revisión: 2026-05-07

Flujo de mejora continua: desde señal de comportamiento hasta doctrina publicada.

---

## Diagrama

```mermaid
sequenceDiagram
  autonumber
  participant MO as Meta-Orchestrator
  participant UP as User Profiler
  participant Anon as Anonymizer
  participant PM as Pattern Miner
  participant KO as Knowledge Officer
  participant CO as Compliance Officer
  participant DP as Doctrine Publisher
  participant Audit as Auditor
  participant ES as Event Store
  participant AllModules as Todos los módulos

  Note over MO,UP: FASE 1 — Captura de señal (continua)
  MO->>UP: response.delivered (señal implícita)
  UP->>UP: infer_preferences()
  UP->>ES: INSERT user.preference.inferred
  UP->>Anon: export_anonymized_signal(tenant_id)
  Anon->>Anon: elimina PII, verifica
  Anon->>PM: AnonymizedSignal

  Note over PM,KO: FASE 2 — Minería de patrones (batch, nocturno)
  PM->>PM: mine_patterns(last_7_days)
  PM->>PM: clustering + análisis estadístico
  PM->>ES: INSERT pattern.detected
  PM->>KO: pattern.detected (candidato a doctrina)

  Note over KO,CO: FASE 3 — Validación y aprobación
  KO->>KO: Evalúa impacto potencial, coherencia
  KO->>CO: doctrine.proposed (solicita aprobación)
  CO->>CO: evaluate_doctrine()
  alt CO aprueba
    CO-->>DP: doctrine.proposed (aprobada)
  else CO bloquea
    CO-->>PM: doctrine.proposed rechazada
    Note over PM: registrar razón, descartar patrón
  end

  Note over DP: FASE 4 — Experimento A/B (canaria)
  DP->>DP: start_experiment (5% del tráfico)
  DP->>ES: INSERT experiment.started
  Note over DP: Período mínimo configurable (default 7 días)

  DP->>Audit: Auditor monitorea KPIs del experimento
  Audit->>Audit: Evalúa muestra ciega del grupo tratamiento vs control

  alt Experimento gana (p<0.05, lift positivo)
    DP->>DP: conclude_experiment(winner=treatment)
    DP->>ES: INSERT doctrine.published
    DP->>AllModules: doctrine.published (vía NATS broadcast)
    AllModules->>AllModules: Actualiza prompts/políticas/routing
    Note over AllModules: KV Store NATS actualizado
  else Experimento pierde o es inconcluso
    DP->>DP: conclude_experiment(winner=control)
    DP->>ES: INSERT doctrine.rolled_back
    Note over DP: Patrón archivado para aprendizaje futuro
  end
```

---

## Tiempos del ciclo

| Fase | Duración típica | Configurable |
|---|---|---|
| Captura de señal | Continua (por petición) | N/A |
| Acumulación de señales (antes de minar) | 7 días | Sí |
| Minería de patrones (batch) | 1–4h (depende del volumen) | Sí |
| Validación por KO + CO | 0–48h (humano puede intervenir) | Sí |
| Experimento A/B | Mínimo 7 días | Sí (por doctrina) |
| **Ciclo completo** | **~14–21 días** | Sí |

---

## Invariantes del ciclo

1. **El Anonymizer es obligatorio** antes de que cualquier dato de usuario llegue al Pattern Miner.
2. **El Compliance Officer tiene veto** sobre cualquier doctrina propuesta, sin excepción.
3. **Ninguna doctrina se despliega al 100% sin pasar por canaria** (5% por defecto).
4. **El rollback es automático** si un KPI cardinal cae > 2% durante el experimento.
5. **Todo experimento se archiva**, gane o pierda, para aprendizaje futuro.

---

## Señales de aprendizaje reconocidas

| Señal | Tipo | Peso |
|---|---|---|
| Re-prompt inmediato tras respuesta | Implícita negativa | Alto |
| Copia del output sin modificar | Implícita positiva | Medio |
| Expansión explícita ("más detalle") | Explícita refinamiento | Medio |
| Rating explícito (si disponible) | Explícita | Alto |
| Tiempo de lectura largo | Implícita positiva | Bajo |
| Guardrail activado | Implícita negativa | Crítico |
| QA fallado (antes de entrega) | Interna negativa | Alto |

---

## Protección anti-reward-hacking

El Auditor evalúa con un evaluador **independiente** del que generó el output. Si el sistema aprende a "parecer bueno" en las métricas de QA sin serlo realmente, el Auditor lo detecta al comparar con evaluación adversarial externa.

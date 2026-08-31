# ADR-0006 — Despliegue canario para todas las doctrinas

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema mejora su comportamiento publicando doctrinas (cambios de prompts, políticas y routing). Una doctrina incorrecta podría degradar la calidad para todos los usuarios. Se necesita un mecanismo que limite el impacto de una doctrina problemática antes de su despliegue completo.

---

## Decisión

**Toda doctrina pasa obligatoriamente por un despliegue canario** antes de activarse al 100%. El proceso es:

1. La doctrina propuesta se aprueba por KO + Compliance Officer.
2. Se activa para un cohort del 5% del tráfico (configurable, nunca 0%, nunca 100% directo).
3. El experimento corre durante el período mínimo definido (default: 7 días).
4. El Auditor evalúa los resultados con un evaluador adversarial independiente.
5. Si los KPIs del grupo tratamiento superan al control con p < 0.05: `doctrine.published` al 100%.
6. Si no: `doctrine.rolled_back`. El cohort revierte a la versión anterior.

**No existe bypass a este proceso**, incluso para el operador humano (que puede acelerar el período mínimo, pero no saltarlo).

---

## Consecuencias positivas

- **Límite de impacto**: una doctrina problemática afecta máximo al 5% del tráfico durante el período de experimentación.
- **Evidencia empírica**: cada doctrina tiene datos reales de su impacto antes de desplegarse al 100%.
- **Rollback automático**: no requiere intervención humana para revertir si los KPIs caen.
- **Anti-reward-hacking**: el evaluador adversarial del Auditor evita que el sistema aprenda a optimizar métricas proxy sin mejora real.
- **Confianza en el aprendizaje**: el historial de experimentos con resultados medibles es el registro de cómo el sistema mejoró.

---

## Consecuencias negativas

- **Velocidad reducida**: ninguna mejora llega al 100% de usuarios antes de 7 días mínimo.
- **Complejidad de routing**: el sistema debe enrutar un subconjunto del tráfico a una configuración diferente.
- **Requisito de volumen**: el experimento requiere suficiente tráfico para ser estadísticamente significativo. Con muy poco tráfico, el período puede extenderse.

---

## Mecanismo de asignación de cohort

Los usuarios se asignan al grupo tratamiento o control de forma estable (mismo usuario siempre en el mismo grupo durante el experimento) usando:

```
cohort = hash(tenant_id + experiment_id) % 100
is_treatment = cohort < treatment_cohort_pct
```

Esto garantiza que un usuario no cambie de grupo durante el experimento, evitando experiencias inconsistentes.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Despliegue directo al 100% | Riesgo de degradar a todos los usuarios simultáneamente |
| Despliegue manual por el operador | Introduce latencia humana; no escala con la velocidad del ciclo de aprendizaje |
| Shadow testing (sin tráfico real) | No captura el comportamiento real del usuario; los efectos de calidad percibida no son medibles |
| Feature flags por usuario | Sin control estadístico; sin comparación sistemática con baseline |

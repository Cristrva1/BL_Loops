# User Profiler

> **Status**: `draft` | Anillo: Transversal | Última revisión: 2026-05-07

---

## 1. Propósito

Mantener, actualizar y servir el modelo individual de cada usuario: preferencias, profesión, estilo de comunicación, historial de interacciones e inferencias de comportamiento. Es **el registro per-usuario** del sistema.

---

## 2. Anillo y rol

- **Anillo**: Transversal (cruza los tres anillos)
- **Rol análogo**: Profiler de usuario / CRM interno
- **Patrón**: Event-driven state machine sobre perfil JSONB

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator (sirve contexto) y Knowledge Officer (CKO) para decisiones de globalización
- **Dirige a**: nada; es un proveedor de contexto
- **Alimenta a**: Pattern Miner (con señales anonimizadas vía Anonymizer), todos los guilds (con perfil al inicio de cada tarea)

---

## 4. Puerto (interfaz)

```python
class UserProfilerPort:
    async def get_profile(self, tenant_id: str) -> UserProfile:
        """
        Devuelve el perfil completo del usuario para uso en planificación.
        Latencia objetivo: < 50ms (desde caché Redis hot path).
        """

    async def update_profile(self, event: UserProfileUpdated) -> None:
        """
        Aplica actualización incremental al perfil.
        Fuente: cualquier evento con señales de preferencia.
        """

    async def infer_preferences(self, event: ResponseDelivered) -> None:
        """
        A partir de la interacción completa, infiere preferencias implícitas.
        Publica: user.preference.inferred si detecta nuevas señales.
        """

    async def export_anonymized_signal(self, tenant_id: str) -> AnonymizedSignal:
        """
        Exporta señales de comportamiento sin PII hacia el Pattern Miner.
        SIEMPRE pasa por Anonymizer antes de salir de este módulo.
        """
```

---

## 5. Estructura del perfil de usuario

```json
{
  "tenant_id": "uuid",
  "version": 42,
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "explicit": {
    "name": "...",
    "profession": "...",
    "language": "es",
    "timezone": "America/Mexico_City",
    "preferred_response_format": "markdown",
    "preferred_detail_level": "expert",
    "custom_instructions": "..."
  },
  "inferred": {
    "communication_style": "direct_no_pleasantries",
    "prefers_tables": true,
    "prefers_code_examples": true,
    "typical_domains": ["technology", "business_strategy"],
    "avg_tokens_consumed": 1200,
    "re_prompt_rate": 0.08,
    "satisfaction_signals": {
      "explicit_ratings": [],
      "implicit_engagement": 0.87
    }
  },
  "history_summary": {
    "total_requests": 347,
    "last_30_days_requests": 42,
    "top_guilds_used": ["production", "research"],
    "last_interaction_at": "ISO8601"
  },
  "active_doctrines": ["doctrine-uuid-1", "doctrine-uuid-2"]
}
```

---

## 6. Eventos que publica

| Evento | Cuándo |
|---|---|
| `user.profile.updated` | Cada vez que el perfil cambia (incluye diff) |
| `user.preference.inferred` | Al detectar nueva preferencia implícita con confianza > 0.75 |

---

## 7. Eventos que consume

| Evento | Fuente | Acción |
|---|---|---|
| `response.delivered` | Meta-Orchestrator | Inferencia de preferencias implícitas |
| `user.profile.updated` | Sí mismo / API admin | Actualización explícita |
| `doctrine.published` | Doctrine Publisher | Añadir doctrina al perfil activo del usuario |
| `guardrail.triggered` | Compliance Officer | Registrar evento en historial (para análisis) |

---

## 8. Estado que posee

- **PostgreSQL** (`user_profiles`): perfil JSONB con columnas indexadas para búsqueda (language, profession, preferred_format).
- **Redis** (`profile:<tenant_id>`): caché hot-path del perfil. TTL = 1h, invalidado en cada `user.profile.updated`.
- **PostgreSQL** (`profile_history`): snapshots inmutables de cada versión del perfil para rollback y auditoría.

---

## 9. SLOs

| Métrica | Objetivo |
|---|---|
| Latencia `get_profile` p95 (cache hit) | < 10ms |
| Latencia `get_profile` p95 (cache miss) | < 50ms |
| Latencia `update_profile` p95 | < 100ms |
| Disponibilidad | 99.9% |

---

## 10. Decisiones que puede tomar sin escalar

- Actualizar cualquier campo del perfil basado en señales de interacciones.
- Invalidar inferencias antiguas si hay suficientes señales contradictorias.
- Incrementar/decrementar confianza de preferencias inferidas.
- Exportar señales anónimas al Pattern Miner (sin PII, siempre vía Anonymizer).

---

## 11. Cuándo escala

- El usuario solicita explícitamente borrar su perfil (GDPR/privacidad) → escala a Knowledge Officer.
- Se detecta patrón anómalo en el perfil (posible ataque de prompt injection persistente) → alerta al Compliance Officer.

---

## 12. Métricas de calidad propias

- `profiler.profile.version_avg` — versión promedio de perfil por usuario activo (gauge)
- `profiler.preference.inferred_count` — nuevas preferencias inferidas por día (counter)
- `profiler.cache.hit_rate` — tasa de cache hits en get_profile (gauge)
- `profiler.update.latency_ms` — latencia de actualización (histogram)
- `profiler.anonymized_signal.exported_count` — señales exportadas al Pattern Miner (counter)

---

## Notas de implementación

- El perfil usa JSONB para flexibilidad, pero los campos de indexación frecuente (language, profession) deben ser columnas propias.
- La inferencia de preferencias debe ser **conservadora**: solo actualiza si la señal es consistente en al menos 3 interacciones o la confianza supera 0.75.
- El Anonymizer debe ejecutarse **en este módulo** antes de exportar, no en el Pattern Miner. Ver ADR-0007.
- El perfil nunca debe contener el texto completo de peticiones o respuestas anteriores; solo metadatos y resúmenes.

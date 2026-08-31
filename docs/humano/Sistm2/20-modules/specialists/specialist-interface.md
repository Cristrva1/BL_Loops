# Interfaz genérica de Especialista

> **Status**: `draft` | Anillo: 3 — Especialistas | Última revisión: 2026-05-07

---

## Principio clave

Todos los especialistas son **intercambiables**. Se reentrenan o sustituyen sin afectar al Guild que los coordina, porque todos exponen el mismo contrato.

---

## Contrato obligatorio de todo especialista

```python
class SpecialistPort:
    """
    Contrato mínimo que TODOS los especialistas deben implementar.
    Un especialista que no implementa este contrato no puede ser registrado en el sistema.
    """

    specialist_id: str
    specialist_type: str
    guild_affinity: str
    version: str

    async def execute(self, task: TaskDispatched) -> None:
        """
        Punto de entrada único. Recibe una tarea del coordinador de guild.
        DEBE publicar task.completed o task.failed.
        DEBE publicar al menos 1 evento de telemetría.
        NUNCA debe superar el budget de tokens/latencia definido en task.constraints.
        """

    async def health_check(self) -> HealthStatus:
        """
        Estado de salud del especialista.
        Retorna: healthy | degraded | unavailable
        """

    async def get_capabilities(self) -> list[str]:
        """
        Lista de capacidades del especialista (para routing dinámico).
        Ejemplo: ["web_search", "url_fetch", "pdf_parse"]
        """
```

---

## Reglas que todo especialista debe respetar

1. **Falla cerrada**: si falla internamente, publica `task.failed` con código de error. Nunca se queda en silencio.
2. **Idempotente**: si recibe el mismo `task_id` dos veces, lo detecta por Redis y responde con el resultado anterior.
3. **Sin estado propio de larga duración**: el estado del especialista es efímero. El estado persistente lo maneja el Guild de Memoria.
4. **Respetar el budget**: si va a exceder `constraints.max_tokens` o `constraints.deadline_at`, publica `task.failed` con razón `budget_exceeded` antes de intentarlo.
5. **Telemetría obligatoria**: cada ejecución produce al menos un evento con `tokens_used`, `latency_ms` y `llm_model` si aplica.

---

## Ciclo de vida de un especialista

```
Registro en module_registry
  → Validación de contrato por Architecture Guardian
  → Asignación a guild(s) por Knowledge Officer
  → Operación normal (consume task.dispatched, publica task.completed)
  → Actualización de versión (sin downtime, reemplazable en caliente)
  → Retiro (guild deja de enrutarle; nuevo especialista registrado)
```

---

## Cómo agregar un nuevo especialista al sistema

1. Implementar el `SpecialistPort` completo.
2. Crear ficha de módulo siguiendo la plantilla de `20-modules/`.
3. Registrar en `module_registry` vía API admin.
4. Architecture Guardian valida el contrato.
5. Asignar al guild correspondiente en la tabla de routing.
6. El especialista empieza a recibir tareas del guild.

**No requiere**: cambios en el Meta-Orchestrator, el Router, ni en otros guilds.

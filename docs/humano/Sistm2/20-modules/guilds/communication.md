# Guild de Comunicación

> **Status**: `stub` | Anillo: Guild (2) | Última revisión: 2026-05-07

## 1. Propósito

Adaptar el output al canal, tono, idioma y formato preferido por el usuario. Es la capa de presentación de todas las respuestas.

## 2. Especialistas típicos

- `formatter` — aplica formato markdown, HTML, JSON según el canal
- `translator` — traducción de idiomas con preservación de contexto técnico
- `tone-adaptor` — ajuste de registro (formal/informal, experto/divulgativo)
- `length-optimizer` — ajusta longitud según preferencias del usuario

## 3. Puerto (interfaz) — pendiente de especificar

```python
class CommunicationGuildPort:
    async def format_output(self, task: TaskDispatched) -> None: ...
```

## 4. SLOs (preliminares)

- Latencia p95: < 2s
- Coherencia con perfil de usuario: > 90% (medida por QA)

> **TODO**: Completar. Prioridad: fase 3.

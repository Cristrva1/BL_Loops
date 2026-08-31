# Evaluación

## Fase implementada: F-LOCAL-CODE-004@0.1.0

**Objetivo:** decidir si el host está preparado para una futura corrida con Hermes sin cambiar su estado.

### Criterios iniciales

- Python activo 3.12.
- endpoint Ollama HTTP inequívocamente loopback.
- en modo formal, referencias autorizadas de firewall y perfil del servidor.
- alias `local-code-9b-64k` con `FROM qwen3.5:9b` y `num_ctx 65536`.
- versión de Hermes capturable.
- ningún modelo de LM Studio cargado.
- `HEAD` exacto en modo formal.
- al menos 8 GiB de RAM física y de margen de commit, y 12,288 MiB de VRAM libres antes de carga.

Los umbrales son gates conservadores de preparación, no una garantía de que el modelo cargará 100 % en GPU.

### Terminales

| Terminal | Significado | Score |
|---|---|---|
| `run.completed` | todos los requisitos iniciales pasaron | `null` |
| `run.blocked` | falta requisito o autoridad | `null` |
| `run.failed` | fallo interno del harness | `null` |

Toda corrida de esta fase exporta `scored=false` y `comparable=false`.

## Fase pendiente: B-CODE-003@0.1.0

El proyecto de precios exige corregir la frontera de descuento completo y añadir una prueba para valores superiores a 100. El verificador requiere cambios exactos en producción y tests, preserva los casos 0/25/100 y negativos mediante comprobaciones ocultas, y ejecuta mutantes para demostrar que los cuatro tests requeridos fallan ante una implementación errónea.

Antes de puntuar también deben demostrarse:

- residencia 100 % GPU en `ollama ps`;
- contexto efectivo de 65,536;
- cero mensajes `truncating input prompt` y cero HTTP 500;
- ausencia de paginación sostenida;
- tool calls, edición y pruebas correctos;
- inferencia local y cero egress con evidencias separadas.

## Comparación futura

Hermes, OpenCode y Claude Code deben partir del mismo `HEAD`, fixture, permisos, modelo, digest, contexto y hardware. Se requieren tres corridas puntuadas válidas por cliente. Un preflight aislado nunca autoriza una clasificación.

## Verificación automática

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run hermes-run-validate <ruta-jsonl>
```

Las pruebas son herméticas. El preflight real es una demostración separada de solo lectura; la corrida de agente queda aplazada.

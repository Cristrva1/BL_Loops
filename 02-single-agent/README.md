# 02 · Agente único: el chat local más pequeño posible

> **Pregunta:** ¿cuál es el camino mínimo para conversar con un modelo local desde la terminal?
> **Nivel:** 1 · **Tiempo:** ~30 min · **Necesita Ollama:** sí, con `gemma4:e4b`

Un chat de PowerShell que conserva el contexto de la sesión en RAM y consulta `gemma4:e4b` mediante
la API local de Ollama. No tiene herramientas, RAG, navegador ni interfaz web: enseña solo la idea
base de todo agente, que el modelo **recibe de nuevo todo el historial en cada turno**.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\02-single-agent
uv sync --all-groups          # crea la .venv propia; el runtime solo usa la biblioteca estándar
ollama list                   # debe aparecer gemma4:e4b
uv run single-agent           # abre el chat
```

Dentro del chat:

```text
Tu > Recuerda que mi color de prueba es verde.
Tu > ¿Cuál es mi color de prueba?
Tu > /memoria        ← cuántos mensajes y caracteres se reenviarán (no llama al modelo)
Tu > /olvidar        ← vacía el historial: el modelo deja de “recordar”
Tu > /salir
```

Al salir, valida la traza de la sesión:

```powershell
uv run single-agent-validate
```

## Qué deberías ver

```text
Agente local | modelo: gemma4:e4b
Flujo: humano -> Ollama local -> agente
Escribe /ayuda para ver los comandos locales o /salir para terminar.
...
Conversacion terminada. Traza: .local/runs/<fecha>-run-<id>.jsonl
JSONL valido: 7 eventos, terminal=run.completed, run_id=run-<id>
```

La traza registra estados, longitudes, tokens y tiempos, **nunca** el texto de la conversación.

## Comandos locales del chat

| Comando | Qué hace | ¿Llama al modelo? |
|---|---|---|
| `/ayuda` | Lista los comandos | No |
| `/memoria` | Muestra mensajes en RAM, caracteres que se reenviarán y tokens del último turno | No |
| `/olvidar` | Vacía el historial y conserva solo la instrucción de sistema | No |
| `/salir` | Termina la sesión y cierra la traza JSONL | No |

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/single_agent/` | Configuración, cliente de Ollama, chat, eventos y validador |
| `tests/` | Pruebas deterministas con un modelo falso: no necesitan Ollama |
| `contracts/run-event.schema.json` | Contrato de cada evento exportado |
| `examples/demo-input.txt` | Conversación de ejemplo |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/runs/` | Trazas de cada sesión (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): requisitos y primera conversación.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): memoria, olvido, trazas y fallos con salidas reales.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [01-prompt-agent-factory](../01-prompt-agent-factory/README.md).
**Sigue con:** [03-orchestration](../03-orchestration/README.md), donde varios roles se reparten una tarea.

## Estado y límites

- **Implementado:** chat CLI, memoria de sesión, comandos locales, validación de endpoint y modelo,
  traza JSONL sanitizada y validador.
- **Aplazado:** tools, dashboard web, SSE y comparación de los cuatro modelos iniciales.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

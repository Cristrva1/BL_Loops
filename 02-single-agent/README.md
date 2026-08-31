# 02-single-agent

Chat mínimo para Windows 11 que conserva el contexto de la sesión y consulta `gemma4:e4b` mediante la API local de Ollama. No tiene tools, RAG, navegador, servicios cloud ni interfaz web.

## Ejecutar

Desde PowerShell:

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\02-single-agent
uv sync --all-groups
uv run single-agent
```

Escribe un mensaje y presiona `Enter`. Usa `/salir` para terminar.

```text
Tu > Hola, ¿quién eres?
[procesando] humano -> Ollama -> agente
Agente > Soy un asistente de IA local...
```

Cada sesión exporta una traza sin el texto de la conversación. Importa y valida la más reciente con:

```powershell
uv run single-agent-validate
```

## Organización

- `src/single_agent/`: configuración, cliente de Ollama, chat, eventos y validador.
- `tests/`: pruebas deterministas sin invocar el modelo.
- `contracts/`: contrato JSON Schema de cada evento exportado.
- `examples/`: conversación de ejemplo.
- `docs/humano/`: explicación, recorrido, ejercicios, diagnóstico y evaluación.
- `.local/runs/`: trazas creadas al ejecutar; está ignorada por Git.

Empieza en [docs/humano/README.md](docs/humano/README.md) y sigue el [inicio rápido](docs/humano/QUICKSTART.md).

> Estado: primer corte funcional del laboratorio de agente único. Cumple el chat CLI pedido; tools, dashboard, SSE y comparación de modelos permanecen aplazados.

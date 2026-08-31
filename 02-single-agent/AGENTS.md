# Instrucciones de trabajo de 02-single-agent

Estas reglas se aplican a todo este laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; al copiar el laboratorio, conservan sus límites esenciales.

## Objetivo y estado

- Este corte enseña el agente mínimo: una conversación de texto en la CLI de Windows 11 contra `gemma4:e4b` mediante Ollama local.
- La única memoria es el historial en RAM de la sesión actual.
- No presentar tools, RAG, persistencia de conversaciones, interfaz web, SSE ni autonomía como capacidades existentes.
- La traza JSONL contiene estados y métricas, pero no guarda el texto crudo de la conversación.

## Separación y seguridad

- `src/`, `contracts/`, `examples/` y `tests/` son operativos; `docs/humano/` es material de aprendizaje y nunca una dependencia del runtime.
- No importar código, configuración mutable, bases de datos ni servicios de otro laboratorio.
- Toda escritura se limita a `.local/runs/` dentro de este proyecto.
- Solo se admite Ollama por HTTP en `localhost`, `127.0.0.1` o `::1`.
- No añadir fallbacks cloud, telemetría, tools o conectores reales.
- No registrar prompts, respuestas, secretos, PII ni contenido de `.env`.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se lee el `.env` de la raíz; fuera del repositorio se admite un `.env` local creado desde `.env.example`.
- Las rutas relativas siempre se resuelven contra la raíz de este laboratorio.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Mantener una única ruta de ejecución fácil de explicar: humano → cliente HTTP → Ollama → respuesta.
4. Actualizar documentación y pruebas en el mismo cambio.
5. Distinguir lo implementado de lo aplazado.
6. No hacer commit, push, publicación ni descargas sin solicitud explícita.

## Verificación

Ejecutar desde esta carpeta:

```powershell
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run single-agent-validate <ruta-jsonl>
uv run single-agent
```

La última comprobación debe usar una conversación breve real con Ollama. Termina la sesión con `/salir` y comprueba que el JSONL generado se pueda importar con `single-agent-validate`.

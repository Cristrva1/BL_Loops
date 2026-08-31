# Instrucciones de trabajo de 01-prompt-agent-factory

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz; si el laboratorio se copia, este archivo conserva sus límites esenciales.

## Objetivo y estado

- Este proyecto enseña a convertir una intención en `PromptSpec`, `AgentSpec` o `SkillSpec` validado y exportable.
- La Parte 1 es determinista: interfaz, API, contratos y exportación son reales, pero no invoca Ollama.
- No presentar SQLite, SSE, ejecución de tools o generación con IA como capacidades existentes hasta implementarlas y verificarlas en una parte posterior.

## Separación

- `backend/`, `frontend/`, `contracts/` y `examples/` contienen archivos operativos.
- `docs/humano/` contiene enseñanza y nunca puede ser una dependencia del runtime.
- No importar código, bases de datos, servicios o estado de otro laboratorio.
- Los artefactos se exportan a `.local/`; no se escribe fuera del proyecto.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio.
- Dentro de BL_Loops se usa el `.env` de la raíz; si se copia, se crea un `.env` local desde `.env.example`.
- Nunca imprimir el `.env` ni exponer settings sensibles en endpoints o logs.
- No añadir APIs cloud, telemetría o conectores reales como fallback.

## Forma de trabajar

1. Revisar `git status --short` y preservar cambios existentes.
2. Leer `README.md` y el documento humano relacionado con la tarea.
3. Construir el corte vertical más pequeño que enseñe la capacidad nueva.
4. Mantener contratos estrictos, permisos denegados por defecto y salidas dentro del laboratorio.
5. Actualizar la guía, arquitectura, metodología, ejercicios, diagnóstico o evaluación que resulten afectados.
6. Distinguir capacidad implementada, límite deliberado y trabajo futuro.
7. No modificar ni instalar dependencias en repositorios bajo `Repositorios_Prueba`.
8. No hacer commit, push o publicación salvo solicitud explícita.

## Verificación

Ejecutar las comprobaciones aplicables desde esta carpeta:

```powershell
uv run pytest
uv run ruff check .
uv run factory-export-schemas
npm --prefix frontend run build
uv run factory-demo
```

Si cambia la interfaz, verificar también el recorrido real en navegador, la consola y los estados derivados de la API. Si aparece una corrida evaluable, comprobar su exportación JSONL e importación antes de declararla terminada.

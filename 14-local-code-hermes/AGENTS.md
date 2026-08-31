# Instrucciones de trabajo de 14-local-code-hermes

Estas reglas se suman a las de `BL_Loops/AGENTS.md` y permanecen vigentes si el laboratorio se copia fuera del repositorio.

## Objetivo y estado

- Este corte implementa únicamente el preflight no puntuado `F-LOCAL-CODE-004@0.1.0` para Hermes, Ollama y `local-code-9b-64k`.
- `B-CODE-003@0.1.0` incluye un fixture congelado y un verificador, pero Hermes todavía no lo ejecuta.
- No presentar como verificadas la residencia 100 % GPU, el contexto efectivo, la ausencia de truncación o HTTP 500, el uso de tools ni el cero egress.
- No traducir controles `medium` o `high` de otros clientes a una capacidad supuesta del modelo local.

## Seguridad y efectos

- El preflight diagnostica; no crea o carga modelos, no inicia o detiene Ollama, Hermes o LM Studio, no cambia variables globales ni configura firewall.
- Toda escritura del runtime queda bajo `.local/` dentro de este laboratorio.
- No importar código, configuración, datos ni servicios de otro laboratorio. `docs/humano/` nunca es dependencia del runtime.
- No guardar stdout o stderr crudos, prompts, respuestas, `.env`, secretos, rutas personales ni datos sensibles en JSONL.
- Solo se acepta Ollama por HTTP en loopback. Eso prueba una configuración local, no cero egress del árbol de procesos.
- Ejecutar código generado en el fixture requiere revisión humana y aislamiento autorizados; el verificador no es un sandbox del sistema operativo.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` propios.
- Mantener `qwen3.5:9b` a 65,536 tokens como cohorte primaria. Si no cabe, `qwen3.5:4b` a 65,536 es otra cohorte; 32k no es comparable.
- No descargar modelos ni dependencias, descargar o instalar clientes, ni alterar procesos activos sin solicitud explícita.

## Forma de trabajar

1. Revisar Git y preservar cualquier cambio ajeno.
2. Leer `README.md` y el documento humano relacionado.
3. Mantener separadas preparación, preflight, benchmark puntuado y decisión humana.
4. Usar dobles herméticos en tests; nunca invocar servicios locales reales desde pytest.
5. Actualizar código, contratos y enseñanza en la misma tanda.
6. No hacer commit, push, publicación ni cambios del host salvo solicitud explícita.

## Verificación

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run hermes-preflight --mode exploratory
uv run hermes-run-validate <ruta-jsonl>
```

El preflight real puede terminar correctamente como `run.blocked` y devolver código 2. No se ejecuta la fase viva hasta cumplir todos los prerrequisitos y contar con autorización.

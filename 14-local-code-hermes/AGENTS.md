# Instrucciones de trabajo de 14-local-code-hermes

Estas reglas se suman a las de `BL_Loops/AGENTS.md` y permanecen vigentes si el laboratorio se copia fuera del repositorio.

## Objetivo y estado

- `F-LOCAL-CODE-004@0.1.0` implementa el preflight sanitario de Hermes, Ollama y `local-code-9b-64k`.
- `B-CODE-003@0.1.0` incluye el fixture congelado, el verificador test-first y un runner para una corrida autorizada de Hermes.
- El runner usa proveedor `custom` con Ollama loopback, una configuración temporal de Hermes y Docker por sesión sin red.
- `--allow-dirty-worktree` es únicamente un smoke de desarrollo: conserva el gate Git bloqueado y no permite score ni comparabilidad.
- No presentar como verificadas la ausencia de truncación/HTTP 500, la residencia GPU, el contexto efectivo, cero egress o una comparación entre clientes si no aparecen en la evidencia de la corrida.

## Seguridad y efectos

- `hermes-preflight` diagnostica sin cambiar el host. `hermes-benchmark` solo inicia Hermes cuando recibe `--execute` y el preflight formal está verde, salvo el override explícito de worktree sucio.
- El sandbox Docker usa `--network=none`, elimina capacidades, impide escalada, limita PID, monta solo el workspace y usa contenedor efímero. La imagen debe estar instalada; el runner no hace `pull`.
- La configuración temporal de Hermes no hereda API keys, tokens, proxies, volúmenes ni variables de entorno al contenedor.
- Toda escritura del runtime queda bajo `.local/` dentro de este laboratorio.
- No guardar stdout, stderr, prompts, respuestas, `.env`, secretos, rutas personales ni datos sensibles en JSONL.
- Solo se acepta Ollama por HTTP en loopback. Eso no sustituye la evidencia independiente de cero egress.

## Entorno

- Usar el `pyproject.toml`, `uv.lock` y `.venv` propios.
- Mantener `qwen3.5:9b` a 65,536 tokens como cohorte primaria. El fallback `qwen3.5:4b` a 65,536 es otra cohorte; 32k no es comparable.
- No descargar modelos ni dependencias ni alterar procesos activos sin solicitud explícita. La corrida viva y los cambios de host requieren la autorización del operador.

## Forma de trabajar

1. Revisar Git y preservar cualquier cambio ajeno.
2. Leer `README.md` y el documento humano relacionado.
3. Mantener separadas preparación, preflight, smoke, benchmark puntuado y decisión humana.
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

La corrida viva se ejecuta solo de forma consciente:

```powershell
uv run hermes-benchmark --execute
```

El JSONL de benchmark debe validarse con el mismo `hermes-run-validate`; no se interpreta una salida de proceso como evidencia hasta pasar el validador.

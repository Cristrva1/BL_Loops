# Handoff para la siguiente sesión

## Estado al cerrar esta sesión

- La implementación del runner, el sandbox Docker y la validación JSONL están en el worktree; no hay commit ni push.
- `local-code-9b-64k:latest` existe en Ollama y se creó desde `qwen3.5:9b` con `num_ctx=65536`, sin repetir el pull después de corregir el almacén local.
- Hermes detectado: `0.20.0`. El runner fuerza proveedor custom, endpoint loopback y `HERMES_HOME` temporal; no usa el proveedor cloud configurado por el usuario.
- LM Studio no tenía modelo cargado ni proceso observado.
- El perfil Firewall Público quedó habilitado en la sesión anterior, con entrada bloqueada y salida permitida. Esa evidencia histórica no sustituye una comprobación contemporánea.
- El estado vivo comprobado al retomar ya no tiene un único servidor: `ollama ps` está vacío, pero coexisten un `ollama.exe` manual en `127.0.0.1:11434` y el servidor de Ollama App en `:::11434`. No detener ninguno sin autorización explícita del operador.
- El read-back sanitario del log actual de Ollama App no coincide con el perfil requerido completo. Por tanto, `OLLAMA-LOCAL-20260830` ya no debe tratarse como prueba contemporánea aunque el gate `ollama.server_profile` solo registre que la referencia fue proporcionada.
- Se eliminó únicamente el residuo `sha256-…-partial*` de la descarga cancelada en la caché de usuario de Ollama; no se tocaron configuración, claves ni blobs no parciales.

## Evidencia disponible

- Preflight formal más reciente: `.local/runs/preflight-run-20260831T054950Z-5df7bb0c.jsonl`.
- Ese JSONL es válido y tiene 22 eventos. Pasaron endpoint configurado, firewall referenciado, perfil referenciado, identidad del modelo, Hermes, LM Studio y VRAM.
- Sigue bloqueado por `git.head` (86 entradas en el worktree compartido) y `resource.ram` (5.99 GiB disponibles frente a 8 GiB requeridos). El worktree sucio incluye cambios ajenos del laboratorio 13; no limpiarlos ni revertirlos.
- El JSONL no detecta la coexistencia de los dos listeners ni demuestra que el perfil referenciado siga activo. Es evidencia diagnóstica bloqueada, no autorización de ejecución.
- Smoke de benchmark: `.local/runs/benchmark-run-20260831T053157Z-25147453.jsonl`; es válido y terminó antes de lanzar Hermes por `preflight_not_green`.
- Fixture aislado aprobado: `uv run hermes-fixture-verify verify final-fixture` sobre `.local/workspaces/final-fixture`.

## Continuación segura

1. Leer la raíz `AGENTS.md`, el `AGENTS.md` del laboratorio y `docs/INDEX.md`; revisar `git status --short` y conservar todos los cambios existentes.
2. Resolver con autorización del operador la coexistencia actual de dos servidores Ollama. Después confirmar `lms ps --json`, `ollama ps`, exactamente un listener loopback en `127.0.0.1:11434` y la ausencia de `llama-server.exe` separado.
3. Volver a probar el perfil Ollama real, incluyendo contexto, GPU offload, cache, paralelismo, máximo de modelos y cloud deshabilitado. Registrar una referencia contemporánea distinta de `OLLAMA-LOCAL-20260830`.
4. Solo entonces repetir el preflight formal con las referencias autorizadas:

   ```powershell
   uv run hermes-preflight --mode formal `
     --network-proof firewall-authorized `
     --firewall-proof-id FW-PUBLIC-20260830 `
     --server-profile-proof operator-authorized `
     --server-profile-proof-id OLLAMA-<ID-CONTEMPORANEO>
   ```

5. No ejecutar Hermes hasta que RAM disponible sea al menos 8 GiB, exista un único servidor Ollama con el perfil comprobado y el worktree pueda fijarse a un SHA limpio. No detener los contenedores `sinow-*` ni aplicaciones con estado del usuario sólo para forzar el gate.
6. Con todos los gates verdes, ejecutar una sola vez:

   ```powershell
   uv run hermes-benchmark --execute `
     --network-proof-id FW-PUBLIC-20260830 `
     --server-profile-proof-id OLLAMA-<ID-CONTEMPORANEO>
   ```

   `--allow-dirty-worktree` sólo sirve para un smoke explícitamente no puntuable y no convierte el resultado en evidencia oficial.
7. Validar el JSONL generado:

   ```powershell
   uv run hermes-run-validate .local/runs/<benchmark-jsonl>
   ```

8. Después de una corrida viva, verificar `ollama ps`, liberar el alias si corresponde y revisar que no queden procesos Hermes, Docker efímeros ni `llama-server` huérfanos. No hacer commit, push ni publicación sin solicitud explícita.

## Verificación local ya ejecutada

```powershell
uv run pytest -q --basetemp .pytest-tmp-final-2
uv run ruff check .
uv run ruff format --check .
uv run hermes-fixture-verify verify final-fixture
uv run hermes-run-validate .local/runs/preflight-run-20260831T053328Z-6fad8a2f.jsonl
uv run hermes-run-validate .local/runs/benchmark-run-20260831T053157Z-25147453.jsonl
uv run hermes-run-validate .local/runs/preflight-run-20260831T054950Z-5df7bb0c.jsonl
```

Todos terminaron correctamente; la única excepción deliberada fue el benchmark, bloqueado antes de ejecutar Hermes por los gates de preflight. En la continuación también pasaron 121 pruebas, Ruff, formato y la verificación del fixture; el nuevo preflight terminó bloqueado como correspondía y su JSONL sí pasó el validador.

# Ejemplos resueltos · Hermes local-code

> Los ejemplos 1 a 3 se ejecutan **sin Ollama, sin Hermes y sin Docker**. El ejemplo 1 se obtuvo en una
> máquina que **no** tiene esas herramientas (un contenedor Linux): por eso casi todos los gates
> fallan, y esa es precisamente la lección. En tu Windows preparado los resultados serán distintos.
> El ejemplo 4 necesita el host completo y autorización: se muestra la forma esperada. Ejecuta todo
> desde `14-local-code-hermes`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Preflight en una máquina incompleta | Fallar cerrado ante evidencia ausente |
| 2 | El fixture antes de la reparación | Un verificador con varias capas |
| 3 | La reparación correcta | Cambiar solo lo permitido y probar el borde |
| 4 | Una corrida viva controlada | Inferencia local frente a cero egress |

---

## Ejemplo 1 · Preflight en una máquina incompleta

```powershell
uv run hermes-preflight --mode exploratory
$runFile = Get-ChildItem .local\runs\preflight-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

```text
Preflight blocked; terminal=run.blocked; JSONL=.local/runs/preflight-run-20261105T130705Z-24a3a3c5.jsonl
JSONL valido: run_id=run-20261105T130705Z-24a3a3c5 eventos=22 terminal=run.blocked
```

Resumen de los diez gates según el JSONL (evento terminal de cada nodo y su código):

| Gate | Resultado en esta máquina | Lectura |
|---|---|---|
| `python.runtime` | `python_3_12` | Requisito cumplido |
| `network.endpoint` | `loopback_http` | El endpoint configurado es HTTP local |
| `network.firewall` | `locality_unproven_exploratory` | Sin prueba de firewall: aviso, no autorización |
| `ollama.server_profile` | `server_profile_unproven_exploratory` | Sin prueba del perfil del servidor |
| `ollama.model` | `command_not_found` | No hay `ollama`: no se puede comprobar el alias de 64k |
| `hermes.available` | `command_not_found` | Hermes no está instalado |
| `lmstudio.conflict` | `command_not_found` | No se puede demostrar que LM Studio no tenga modelos cargados |
| `git.head` | `worktree_dirty` | Hay cambios sin confirmar: una corrida no sería reproducible |
| `resource.ram` / `resource.vram` | `command_not_found` | No hay forma de medir memoria en este host |

**Qué aprender:**

- El programa **funcionó bien**: termina `run.blocked` (código de salida `2`) porque faltan
  requisitos, no porque tenga un error. Bloquear es la respuesta correcta.
- Ante evidencia ausente, cada gate **falla cerrado**. Por ejemplo, no poder ejecutar la herramienta de
  LM Studio no se interpreta como «LM Studio está libre».
- Un endpoint en loopback (`loopback_http`) pasa, pero eso no prueba cero egress: el firewall sigue sin
  demostrar.

## Ejemplo 2 · El fixture antes de la reparación

`B-CODE-003` es un proyecto diminuto con un error de borde: `apply_discount(1000, 100)` debería devolver
`0`, pero el código rechaza el 100 %.

```powershell
uv run hermes-fixture-verify prepare demo-ejemplo
uv run hermes-fixture-verify verify demo-ejemplo
```

```text
Workspace preparado: .local/workspaces/demo-ejemplo
Fixture no aprobado: changed_files_mismatch,required_tests_missing,unittest_failed,hidden_semantic_check_failed,test_quality_check_failed
```

**Qué observar:** el verificador tiene varias capas, y todas fallan con el código original:

| Código | Qué comprueba |
|---|---|
| `changed_files_mismatch` | Que se modificaran exactamente los archivos permitidos (`src/pricing.py` y `tests/test_pricing.py`) |
| `required_tests_missing` | Que exista la prueba nueva `test_discount_above_100_is_rejected` |
| `unittest_failed` | Que las pruebas del proyecto pasen |
| `hidden_semantic_check_failed` | Un chequeo oculto del comportamiento correcto en el borde |
| `test_quality_check_failed` | Prueba de mutación: la prueba nueva debe fallar si se sustituye `apply_discount` por una versión mutante |

## Ejemplo 3 · La reparación correcta

En `.local/workspaces/demo-ejemplo/src/pricing.py`, la condición pasa de `>= 100` a `> 100`:

```python
if discount_percent < 0 or discount_percent > 100:
    raise ValueError("discount_percent must be between 0 and 100")
```

Y en `tests/test_pricing.py` se añade la prueba de la frontera superior:

```python
def test_discount_above_100_is_rejected(self) -> None:
    with self.assertRaises(ValueError):
        apply_discount(1000, 101)
```

```powershell
uv run hermes-fixture-verify verify demo-ejemplo
```

```text
Fixture aprobado; archivos permitidos y pruebas verificadas.
```

**Qué aprender:** esta es la tarea que el benchmark pide a cada cliente de programación. Una solución
que «haga pasar las pruebas» borrando la de 100 %, tocando otro archivo o sin probar el 101 % no
aprueba. El fixture mide la reparación, no la apariencia de la reparación.

## Ejemplo 4 · Una corrida viva controlada (host completo y autorización)

```powershell
uv run hermes-benchmark --execute --allow-dirty-worktree
$runFile = Get-ChildItem .local\runs\benchmark-*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

Forma esperada:

```text
JSONL valido: run_id=<id> eventos=<n> terminal=<run.completed|run.failed|run.blocked>
```

**Qué observar:**

- Hermes usa Ollama en loopback y ejecuta sus comandos en Docker con `--network=none`: **inferencia
  local** y **aislamiento de comandos**.
- `--allow-dirty-worktree` solo habilita un *smoke* de desarrollo: la evidencia conserva el bloqueo de
  Git y fuerza `scored=false` y `comparable=false`.
- Ninguna corrida única es una comparación entre clientes. Para eso harán falta los laboratorios 15 y
  16, el mismo SHA y el mismo gate.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

# 14-local-code-hermes

Preflight didáctico sin efectos externos para preparar un futuro benchmark de programación local con Hermes, Ollama y `local-code-9b-64k`. El corte actual inspecciona prerrequisitos, escribe JSONL sanitario solo bajo `.local/` y ofrece un fixture determinista; todavía no inicia Hermes ni ejecuta el benchmark.

## Qué existe

```text
humano
  -> preflight de solo diagnóstico
     -> Python y endpoint loopback
     -> evidencia referenciada de red y perfil Ollama
     -> identidad del Modelfile y versión de Hermes
     -> conflicto de LM Studio y HEAD de Git
     -> margen de RAM, commit y VRAM
  -> JSONL F-LOCAL-CODE-004 (no puntuado, no comparable)

B-CODE-003 congelado -> workspace copiado -> verificador local
                                      (ejecución con Hermes pendiente)
```

El preflight no crea el modelo, no cambia el host, no libera VRAM y no ejecuta tools. Un resultado `run.blocked` es una salida válida cuando falta un prerrequisito o autoridad.

## Verificación hermética

Desde PowerShell:

```powershell
# Desde la raíz de BL_Loops
Set-Location .\14-local-code-hermes
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Estas pruebas no llaman a Ollama, Hermes, LM Studio ni internet.

## Preflight real de solo lectura

```powershell
uv run hermes-preflight --mode exploratory
```

El comando solo consulta herramientas ya instaladas y escribe una traza sanitizada en `.local/runs/`. Valídala con:

```powershell
$runFile = Get-ChildItem .local\runs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
uv run hermes-run-validate $runFile.FullName
```

Consulta [docs/humano/QUICKSTART.md](docs/humano/QUICKSTART.md) antes de preparar el modelo o un gate formal.

## Organización

- `src/local_code_hermes/`: configuración, comandos seguros, gates, JSONL y verificador del fixture.
- `cases/B-CODE-003/`: proyecto sintético congelado, sin PII.
- `contracts/`: schema estructural de evento `1.1`; el validador stdlib aplica además lifecycle y semántica por gate.
- `tests/`: pruebas deterministas con dobles.
- `docs/humano/`: explicación, práctica, diagnóstico y evaluación.
- `.local/`: corridas y copias de trabajo ignoradas por Git.

> Estado: `F-LOCAL-CODE-004` implementado. `B-CODE-003`, contexto efectivo, 100 % GPU, tools, edición, pruebas y cero egress siguen pendientes de una corrida autorizada. OpenCode y Claude Code son laboratorios posteriores independientes.

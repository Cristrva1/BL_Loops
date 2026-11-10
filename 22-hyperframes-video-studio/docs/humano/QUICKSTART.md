# Inicio rápido: 22-hyperframes-video-studio

Todos los comandos se ejecutan en PowerShell desde la carpeta del laboratorio.

## 1. Requisitos

| Herramienta | Comprobación | Para qué |
|---|---|---|
| `uv` | `uv --version` | Entorno Python del laboratorio |
| Node.js 22 o superior | `node --version` | `npx` ejecuta HyperFrames |
| FFmpeg y ffprobe | `ffmpeg -version`, `ffprobe -version` | Ensamblar y medir el MP4 |
| Ollama (opcional) | `ollama list` | Escenas propuestas por un modelo local |

En Windows: `winget install OpenJS.NodeJS.LTS` y `winget install Gyan.FFmpeg`; abre una terminal
nueva después. La primera vez que renderices, `npx` descarga HyperFrames 0.8.34 (necesita red).

## 2. Preparar el entorno

```powershell
Set-Location .\22-hyperframes-video-studio
uv sync
```

No hace falta `.env`: los valores por defecto ya son locales. Para cambiarlos,
`Copy-Item .env.example .env`.

## 3. Diagnosticar HyperFrames (opcional)

```powershell
$env:HYPERFRAMES_NO_TELEMETRY = "1"
npx --yes hyperframes@0.8.34 doctor
npx --yes hyperframes@0.8.34 browser ensure
```

`doctor` revisa Node.js, FFmpeg y el navegador; `browser ensure` descarga el Chrome headless que
usa el render. La variable de la primera línea desactiva la telemetría también en estos comandos
manuales; el estudio la pone siempre por su cuenta.

## 4. Ejecutar las pruebas

```powershell
uv run pytest
```

**Resultado esperado:** `28 passed`. No usan red ni lanzan HyperFrames: Ollama se simula y el render
se sustituye por dobles de prueba.

## 5. Ejecutar la demostración

```powershell
uv run hyperframes-studio-demo
```

Qué ocurre:

1. El director pide 5 escenas a Ollama. Sin Ollama verás
   `Origen de las escenas: fallback (ConnectError al consultar Ollama)`.
2. El estudio fija la línea de tiempo (15 s → 5 escenas de 3 s) y escribe
   `.local/workspace/index.html`.
3. El lint local revisa la composición; si falla, la corrida se detiene antes de abrir Chrome.
4. `npx hyperframes@0.8.34 render` genera `.local/output/tutorial_hyperframes.mp4`.
5. `ffprobe` lo mide y se añade una línea a `.local/eval_results.jsonl`.

Códigos de salida: `0` render correcto, `1` fallo de render, `2` configuración inválida. Las
salidas reales están en [EXAMPLES.md](EXAMPLES.md).

## 6. Abrir el panel

```powershell
uv run python -m hyperframes_studio.main
```

Abre `http://127.0.0.1:8022`. Las píldoras de Ollama y `npx` muestran el estado comprobado; los seis
nodos se iluminan con los eventos SSE; las pestañas muestran el MP4, el HTML generado y las trazas.
Un brief fuera de contrato (por ejemplo, un modelo `cloud`) aparece como error en las trazas.
Detén el servidor con `Ctrl+C`.

# Inicio rápido: 23-remotion-superpowers-studio

Todos los comandos se ejecutan en PowerShell desde la carpeta del laboratorio.

## 1. Requisitos

| Herramienta | Comprobación | Para qué |
|---|---|---|
| `uv` | `uv --version` | Entorno Python del laboratorio |
| Node.js 22 o superior | `node --version`, `npm --version` | Remotion, React y TypeScript |
| FFmpeg y ffprobe | `ffmpeg -version`, `ffprobe -version` | Medir el MP4 |
| Ollama (opcional) | `ollama list` | Escenas propuestas por un modelo local |

En Windows: `winget install OpenJS.NodeJS.LTS` y `winget install Gyan.FFmpeg`; abre una terminal
nueva después.

## 2. Preparar los dos entornos

```powershell
Set-Location .\23-remotion-superpowers-studio
uv sync
npm ci
```

`uv sync` crea `.venv` (Python 3.12); `npm ci` instala exactamente las versiones de
`package-lock.json` en `node_modules/` (unos 750 MB; tardó 4 minutos en la verificación). No hace
falta `.env`.

## 3. Ejecutar las comprobaciones

```powershell
uv run pytest          # 21 pruebas de Python, sin red ni Remotion
npm run typecheck      # tipos de la composición React
```

**Resultado esperado:** `21 passed` y `tsc --noEmit` sin errores.

## 4. Ejecutar la demostración

```powershell
uv run remotion-studio-demo
```

Qué ocurre:

1. El director pide 4 escenas a Ollama. Sin Ollama verás
   `Origen de las escenas: fallback (ConnectError al consultar Ollama)`.
2. El estudio calcula los fotogramas (12 s × 30 = 360; 90 por escena) y escribe
   `src/video_composition/scenes.json`.
3. Remotion renderiza `MainVideo` en `.local/output/remotion_superpowers.mp4`. La primera vez
   descarga su Chrome headless.
4. `ffprobe` mide el MP4 y se añade una línea a `.local/eval_results.jsonl`.

En la verificación, el render de 12 s tardó unos 30 s. Códigos de salida: `0` correcto, `1` fallo de
render, `2` configuración inválida. Salidas reales en [EXAMPLES.md](EXAMPLES.md).

## 5. Ver la composición en Remotion Studio

```powershell
npm run dev
```

Abre la interfaz de Remotion en el navegador (la dirección aparece en la terminal). Puedes mover la
línea de tiempo fotograma a fotograma y ver cómo cambia cada escena. Detén con `Ctrl+C`.

## 6. Abrir el panel del laboratorio

```powershell
uv run python -m remotion_studio.main
```

Abre `http://127.0.0.1:8023`: píldoras de estado comprobadas (Ollama y `npx`), nodos que se iluminan
con los eventos SSE, el MP4 y el `scenes.json` actual. Detén con `Ctrl+C`.

## 7. Volver al `scenes.json` del repositorio

Cada corrida reescribe `src/video_composition/scenes.json`. Si Ollama participó, el archivo cambia:

```powershell
git status --short src/video_composition/scenes.json
git restore src/video_composition/scenes.json
```

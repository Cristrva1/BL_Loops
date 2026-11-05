# Inicio rápido: 24-open-generative-ai-studio

Todos los comandos se ejecutan en PowerShell desde la carpeta del laboratorio.

## 1. Requisitos

| Herramienta | Comprobación | Para qué |
|---|---|---|
| `uv` | `uv --version` | Crea la `.venv` del laboratorio y ejecuta los comandos |
| FFmpeg y ffprobe | `ffmpeg -version` y `ffprobe -version` | Renderizar el animatic y medirlo |
| Ollama (opcional) | `ollama list` | Generar storyboard y prompts con un modelo local |

En Windows, FFmpeg se instala con `winget install Gyan.FFmpeg`; abre una terminal nueva después
para que el `PATH` se actualice.

## 2. Preparar el entorno

```powershell
Set-Location .\24-open-generative-ai-studio
uv sync
```

`uv sync` crea `.venv` con Python 3.12 y las dependencias exactas de `uv.lock`, incluidas las de
desarrollo (`pytest`, `ruff`). No necesitas `.env`: los valores por defecto ya son locales. Si
quieres cambiar algo, copia el contrato:

```powershell
Copy-Item .env.example .env
```

## 3. Ejecutar las pruebas

```powershell
uv run pytest
```

**Resultado esperado:** `37 passed`. Las pruebas no usan red ni Ollama (se simula con
`httpx.MockTransport`). La única prueba que llama a FFmpeg de verdad se marca como omitida (`s`) si
FFmpeg o ffprobe no están instalados.

## 4. Ejecutar la demostración

```powershell
uv run open-genai-demo
```

Qué ocurre, paso a paso:

1. Se lee la configuración y se valida que Ollama sea local.
2. Storyboard Studio pide 4 planos a Ollama. Sin Ollama verás
   `Origen de los planos: fallback (ConnectError al consultar Ollama)`.
3. FFmpeg renderiza un segmento por plano en `.local/workspace/` y los une en
   `.local/output/open_genai_animatic.mp4`.
4. `ffprobe` mide el MP4 y se añade una línea a `.local/eval_results.jsonl`.

La salida completa y cómo interpretarla están en [EXAMPLES.md](EXAMPLES.md#ejemplo-1-demo-completa-sin-ollama).
La demo termina con código `0` si renderiza, `1` si FFmpeg falla y `2` si la configuración es
inválida.

## 5. Abrir el panel

```powershell
uv run python -m open_genai_studio.main
```

Abre `http://127.0.0.1:8024`. Verás:

- **Píldoras de estado** comprobadas de verdad: Ollama, FFmpeg/ffprobe y la conexión de eventos.
- **Cuatro nodos** (Concepto, Storyboard, Animatic, Evaluación) que se iluminan con cada evento SSE.
- Un **aviso de fallback** cuando los planos no vienen del modelo.
- Pestañas **Animatic MP4**, **Storyboard** (una tarjeta por plano), **Prompt Studio** y **Trazas SSE**.
- **Métricas medidas** y el botón **Exportar evaluación JSONL**.

Comprobación rápida desde otra terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8024/api/status
```

Debe responder `status = ok`, `ollama_reachable` y `ffmpeg_available` con valores reales (`True` o
`False`). Detén el servidor con `Ctrl+C`.

## 6. Usar otro modelo

En el `.env` del laboratorio:

```text
OLLAMA_MODEL=qwen3.5:4b
```

En el panel, el selector «Modelo local» permite elegir otro modelo para una corrida; «El del .env»
usa el configurado. Un modelo con etiqueta `cloud` se rechaza con `422`.

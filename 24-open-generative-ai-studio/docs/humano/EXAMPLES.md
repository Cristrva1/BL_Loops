# Ejemplos resueltos: 24-open-generative-ai-studio

Cada salida de este documento se obtuvo ejecutando el comando indicado en un clon limpio, con
FFmpeg 6.1 y **sin Ollama**. Lo que depende del modelo se indica como «forma esperada»: el texto
concreto cambia en cada corrida y no se inventa aquí. Los tiempos de render y los tamaños varían
ligeramente de una máquina a otra.

## Ejemplo 1: demo completa sin Ollama

**Entrada:** el proyecto por defecto, «Expedición Nebular», 12 segundos.

```powershell
uv run open-genai-demo
```

**Salida real:**

```text
=== BL_Loops: Laboratorio 24 - Open Generative AI Studio ===
1. Ollama: http://127.0.0.1:11434 | modelo: qwen3.5:9b
2. Proyecto: 'Expedición Nebular' (12.0s)
Storyboard calibrado en uso: ConnectError al consultar Ollama
3. Origen de los planos: fallback (ConnectError al consultar Ollama)
   - Plano 1: Extreme Wide Shot | Slow Pan Right | 3.0s | El Vasto Glaciar de Europa
   - Plano 2: Medium Shot | Tracking Shot | 3.0s | El Avance del Explorador
   - Plano 3: Close-up | Dolly In (Push In) | 3.0s | La Señal Ancestral
   - Plano 4: Wide Shot | Crane Down | 3.0s | El Despertar del Monolito
4. Animatic renderizado:
   - Archivo: .local/output/open_genai_animatic.mp4
   - Duración medida: 12.0s | 1920x1080 a 30 fps
   - Tamaño: 179.52 KB
5. Evaluación exportada a .local/eval_results.jsonl
   - Aprobada: True
```

**Qué observar:**

- La línea `Storyboard calibrado en uso: ...` la escribe el registro (`logging`) del motor; la línea 3
  la escribe la demo. Son el mismo aviso visto desde dos capas.
- 12 s / 4 planos = 3 s por plano. La duración la fija el estudio, no el modelo.
- `Duración medida` viene de `ffprobe`, no del valor pedido. Si `ffprobe` falta, verías `0.0s` y la
  evaluación no aprobaría.
- `Aprobada: True` evalúa el render. El origen `fallback` indica que el modelo no participó.

**Forma esperada con Ollama activo** (el contenido depende del modelo):

```text
3. Origen de los planos: ollama
   - Plano 1: <tipo de plano> | <movimiento> | 3.0s | <titular propuesto por el modelo>
   ...
```

Si el modelo responde algo fuera de contrato, la línea 3 muestra `fallback (respuesta no válida: ...)`
con el motivo exacto: por ejemplo, `se esperaban 4 planos y llegaron 3`.

## Ejemplo 2: configuración insegura rechazada

```powershell
$env:OLLAMA_BASE_URL = "http://example.com:11434"
uv run open-genai-demo
Remove-Item Env:OLLAMA_BASE_URL

$env:OLLAMA_MODEL = "qwen3.5:cloud"
uv run open-genai-demo
Remove-Item Env:OLLAMA_MODEL
```

**Salida real** (cada comando termina con código `2`, sin traza de Python):

```text
Configuracion invalida: OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434.
Configuracion invalida: El modelo debe ser local, no cloud: revisa OLLAMA_MODEL o el campo model.
```

**Qué observar:** la validación ocurre antes de crear la app. Un `.env` mal escrito no puede enviar
datos a otra máquina ni a un modelo cloud.

## Ejemplo 3: FFmpeg no disponible

Se obtuvo ejecutando la demo con un `PATH` que no contiene FFmpeg.

**Salida real (resumida):**

```text
Storyboard calibrado en uso: ConnectError al consultar Ollama
No se encontró FFmpeg: instálalo para renderizar.
3. Origen de los planos: fallback (ConnectError al consultar Ollama)
   ...
[ERROR] No se pudo renderizar el animatic: No se encontró FFmpeg: instálalo para renderizar.
```

**Qué observar:** el storyboard sí se genera, el render falla con una frase clara y la demo termina con
código `1`. No se escribe ninguna línea en el JSONL porque no hay nada que evaluar.

## Ejemplo 4: el contrato del storyboard en acción

Guarda este script como `contrato.py` en la carpeta del laboratorio:

```python
from open_genai_studio.animatic_renderer import drawtext_value, safe_hex_color
from open_genai_studio.storyboard_engine import parse_shots

print(drawtext_value("Plano 2: la 'señal' llega al 100%"))
print(safe_hex_color("#38BDF8"), safe_hex_color("azul eléctrico"))

respuesta = '```json\n[{"shot_type": "close-up", "camera_movement": "static", "headline": "La lámpara"}]\n```'
try:
    parse_shots(respuesta, duration_seconds=3.0)
except ValueError as exc:
    print("Rechazada:", exc)

planos = parse_shots(respuesta, duration_seconds=3.0, expected=1)
print(planos[0].shot_type.value, "|", planos[0].camera_movement.value, "|", planos[0].duration_seconds)
```

```powershell
uv run python contrato.py
```

**Salida real:**

```text
Plano 2\: la ’señal’ llega al 100%
38bdf8 6366f1
Rechazada: se esperaban 4 planos y llegaron 1
Close-up | Static | 3.0
```

**Qué observar:**

1. El `:` queda escapado y la comilla recta pasa a tipográfica: así no cierra `text='...'`.
2. `%` queda igual porque cada `drawtext` usa `expansion=none`.
3. Un nombre de color no es un hex: cae al acento base.
4. La valla ```` ```json ```` se elimina sola, y `close-up` y `static` se aceptan aunque el modelo
   cambie las mayúsculas. Lo que no se acepta es un número de planos distinto del pedido.

Borra `contrato.py` al terminar.

## Ejemplo 5: la API desde PowerShell

Con el servidor en marcha (`uv run python -m open_genai_studio.main`), en otra terminal:

```powershell
$api = "http://127.0.0.1:8024"
Invoke-RestMethod "$api/api/status"
```

**Respuesta real** (JSON devuelto por la API; PowerShell lo muestra como objeto):

```json
{
  "status": "ok",
  "orchestrator_state": "IDLE",
  "run_in_progress": false,
  "ollama_url": "http://127.0.0.1:11434",
  "model": "qwen3.5:9b",
  "ollama_reachable": false,
  "ffmpeg_available": true,
  "ffprobe_available": true,
  "last_render": null,
  "last_eval": null
}
```

### Una petición fuera de contrato

```powershell
Invoke-RestMethod -Method Post -Uri "$api/api/pipeline/run" -ContentType "application/json" `
    -Body '{"model": "qwen3.5:cloud"}'
```

**Respuesta real:** HTTP `422`. PowerShell lo muestra como error con este cuerpo:

```json
{"detail":[{"type":"value_error","loc":["body","model"],"msg":"Value error, El modelo debe ser local, no cloud: revisa OLLAMA_MODEL o el campo model.","input":"qwen3.5:cloud","ctx":{"error":{}}}]}
```

Una duración menor de 4 s también devuelve `422`, porque con 4 planos cada uno duraría menos de 1 s:

```json
{"detail":[{"type":"greater_than_equal","loc":["body","total_duration_target"],"msg":"Input should be greater than or equal to 4","input":2,"ctx":{"ge":4.0}}]}
```

### Prompt Studio

```powershell
$idea = '{"raw_idea": "Un faro en la niebla al amanecer", "style": "Documental 16mm"}'
Invoke-RestMethod -Method Post -Uri "$api/api/prompt/expand" -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes($idea))
```

**Respuesta real sin Ollama:**

```json
{
  "source": "fallback",
  "fallback_reason": "ConnectError al consultar Ollama",
  "model": "qwen3.5:9b",
  "result": {
    "positive_prompt": "Cinematic Documental 16mm shot of Un faro en la niebla al amanecer, anamorphic lens flare, volumetric fog, Kodak Vision3 500T 35mm film grain, high detail.",
    "negative_prompt": "blurry, oversaturated, low quality, artifacts, distorted geometry, extra limbs, watermark.",
    "camera_settings": "Large-format digital camera, anamorphic 50mm lens, T2.0",
    "mood_palette": ["#0ea5e9", "#f59e0b", "#0f172a"]
  }
}
```

**Qué observar:** `model` es el del `.env` porque la petición no indicó ninguno. Con Ollama activo,
`source` vale `ollama`, `fallback_reason` es `null` y `result` conserva las mismas cuatro claves con
el contenido del modelo (forma esperada).

### Una corrida con eventos SSE

Para ver los eventos, abre `http://127.0.0.1:8024/api/pipeline/events` en el navegador (o la pestaña
«Trazas SSE» del panel) y lanza una corrida de 8 segundos:

```powershell
$proyecto = '{"title": "Faro", "narrative_concept": "Una farera descubre un barco fantasma atrapado en la niebla", "total_duration_target": 8}'
Invoke-RestMethod -Method Post -Uri "$api/api/pipeline/run" -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes($proyecto))
```

**Respuesta real:** `{"message":"Pipeline iniciado","model":"qwen3.5:9b"}`. Si repites la petición
antes de que termine, la API responde `409`: no se permiten dos renders sobre el mismo workspace.

**Eventos reales** (estado, nodo y mensaje de cada evento SSE):

```text
ANALYZING_CONCEPT      ConceptAnalyzer   Analizando concepto narrativo: 'Una farera descubre un barco fantasma atrapado en la niebla' (8.0s)
GENERATING_STORYBOARD  StoryboardStudio  Desglosando planos cinematográficos y prompts con Ollama (qwen3.5:9b)...
GENERATING_STORYBOARD  StoryboardStudio  Fallback visible: ConnectError al consultar Ollama. Se usan 4 planos calibrados; el storyboard no refleja una decisión del modelo.
RENDERING_ANIMATIC     AnimaticEngine    Compilando animatic de 4 planos a 1080p con FFmpeg...
EVALUATING             QualityEvaluator  Evaluando animatic generado (8.0s)...
COMPLETED              PipelineGate      Animatic generado en 5.37s.
```

**Qué observar:** con 8 s, cada plano dura 2 s y la duración medida es 8.0 s. El evento de fallback
lleva además `data.director_source = "fallback"` y `data.fallback_reason`, que el panel usa para el
aviso naranja.

## Ejemplo 6: la línea JSONL exportada

Tras el ejemplo 1, `.local/eval_results.jsonl` contiene una línea como esta (formateada aquí para
leerla; la marca de tiempo se sustituye):

```json
{
  "timestamp": "<fecha ISO-8601 UTC>",
  "lab_id": "24-open-generative-ai-studio",
  "case_id": "EVAL-OPEN-GENAI-001",
  "model": "qwen3.5:9b",
  "success": true,
  "duration_actual": 12.0,
  "duration_expected": 12.0,
  "render_time_seconds": 5.42,
  "file_size_kb": 179.52,
  "shots_count": 4,
  "metrics": {
    "resolution": "1920x1080",
    "fps": 30,
    "duration_delta_seconds": 0.0,
    "deterministic": true,
    "all_shots_have_prompts": true,
    "duration_measured": true,
    "director_source": "fallback"
  }
}
```

**Qué observar:** para comparar modelos, filtra las líneas con `director_source = "ollama"`. Las de
`fallback` prueban que el render funciona, no que el modelo sea bueno. El criterio completo está en
[EVALUATION.md](EVALUATION.md).

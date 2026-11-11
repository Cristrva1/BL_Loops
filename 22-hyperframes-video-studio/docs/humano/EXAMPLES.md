# Ejemplos resueltos: 22-hyperframes-video-studio

Cada salida de este documento se obtuvo ejecutando el comando indicado, **sin Ollama**. Lo que
depende del modelo o de un render con HyperFrames se indica como «forma esperada»: no se inventa
aquí. Los ejemplos 2 a 5 no necesitan Node.js. El ejemplo 7 es un render real con HyperFrames.

## Ejemplo 1: demo sin Ollama y sin Node.js

```powershell
uv run hyperframes-studio-demo
```

**Salida real** (obtenida con un `PATH` sin `npx`):

```text
=== BL_Loops: Laboratorio 22 - HyperFrames Video Studio ===
1. Conectando a Ollama (http://127.0.0.1:11434) con modelo: qwen3.5:9b
2. Brief de video: 'Explicar qué es HyperFrames, cómo usarlo y qué puede hacer' (15.0s)
Ollama no entregó escenas (All connection attempts failed); se usan escenas calibradas.
No se encontró npx: instala Node.js para renderizar con HyperFrames.
3. Origen de las escenas: fallback (ConnectError al consultar Ollama)
[ERROR] Error durante el renderizado: No se encontró npx: instala Node.js para renderizar con HyperFrames.
```

**Qué observar:**

- Dos avisos honestos: el origen de las escenas (`fallback`) y la herramienta que falta (`npx`).
- La demo termina con código `1` y no escribe JSONL: no hay video que evaluar.
- La composición sí se generó: está en `.local/workspace/index.html` y puedes abrirla en el navegador.

**Forma esperada con Node.js 22+ y FFmpeg** (el render tarda más la primera vez porque `npx`
descarga HyperFrames):

```text
3. Origen de las escenas: fallback (ConnectError al consultar Ollama)
[OK] VIDEO RENDERIZADO EXITOSAMENTE:
   - Archivo: ...\.local\output\tutorial_hyperframes.mp4
   - Duración: <medida por ffprobe, cerca de 15.0>s
   - Resolución: 1920x1080 (30 FPS)
...
[OK] Aprobada: <True si el desvío es ≤ 1 s y el MP4 pesa más de 10 KB>
```

## Ejemplo 2: configuración insegura rechazada

```powershell
$env:OLLAMA_BASE_URL = "http://example.com:11434"
uv run hyperframes-studio-demo
Remove-Item Env:OLLAMA_BASE_URL

$env:HOST = "0.0.0.0"
uv run hyperframes-studio-demo
Remove-Item Env:HOST
```

**Salida real** (código de salida `2` en ambos casos):

```text
Configuracion invalida: OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434.
Configuracion invalida: HOST debe ser 127.0.0.1, localhost o ::1.
```

## Ejemplo 3: leer la composición sin renderizar

Guarda como `composicion.py` en la carpeta del laboratorio:

```python
import re

from hyperframes_studio.ollama_client import DEFAULT_SCENES
from hyperframes_studio.schemas import VideoBrief
from hyperframes_studio.templates import generate_hyperframes_html

html = generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES)
for scene_id, start, duration in re.findall(
    r'<div id="([^"]+)" class="clip scene-card"\s+data-start="([^"]+)"\s+data-duration="([^"]+)"', html
):
    print(f"{scene_id:<22} empieza en {start:>4} s y dura {duration} s")
print("Bloque de código de la escena 2:", re.findall(r"<code>(.*?)</code>", html)[1])
print("Bytes del HTML:", len(html.encode("utf-8")))
```

```powershell
uv run python composicion.py
```

**Salida real:**

```text
scene-1-intro          empieza en  0.0 s y dura 3.0 s
scene-2-architecture   empieza en  3.0 s y dura 3.0 s
scene-3-cli            empieza en  6.0 s y dura 3.0 s
scene-4-capabilities   empieza en  9.0 s y dura 3.0 s
scene-5-outro          empieza en 12.0 s y dura 3.0 s
Bloque de código de la escena 2: &lt;div class=&quot;clip&quot; data-start=&quot;0&quot; data-duration=&quot;3&quot;&gt;
Bytes del HTML: 11902
```

**Qué observar:** cada escena empieza donde termina la anterior. El fragmento de la escena 2 está
escapado: el navegador mostrará `<div class="clip" ...>` como texto. Antes de esta corrección, ese
mismo fragmento se convertía en un clip real sin id que empezaba en el segundo 0 y su texto no se
veía en pantalla.

## Ejemplo 4: el lint local en acción

```python
from hyperframes_studio.ollama_client import DEFAULT_SCENES
from hyperframes_studio.renderer import TELEMETRY_OPT_OUT
from hyperframes_studio.schemas import VideoBrief
from hyperframes_studio.templates import generate_hyperframes_html, lint_composition

html = generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES)
print("1. Composición calibrada:", lint_composition(html, DEFAULT_SCENES) or "sin problemas")

fantasma = html.replace("</body>", '<div class="clip" data-start="0" data-duration="3"></div></body>')
print("2. Con un clip fantasma:", lint_composition(fantasma, DEFAULT_SCENES))

hueco = [s.model_copy() for s in DEFAULT_SCENES]
hueco[2] = hueco[2].model_copy(update={"start_time": 7.0})
print("3. Con un hueco:", lint_composition(generate_hyperframes_html(VideoBrief(), hueco), hueco))

print("4. Variables que recibe el render:", TELEMETRY_OPT_OUT)
```

**Salida real:**

```text
1. Composición calibrada: sin problemas
2. Con un clip fantasma: ['clip inesperado id=None data-start=0 data-duration=3']
3. Con un hueco: ['scene-3-cli: empieza en 7.0 s y debería empezar en 6.0 s', 'scene-4-capabilities: empieza en 9.0 s y debería empezar en 10.0 s']
4. Variables que recibe el render: {'HYPERFRAMES_NO_TELEMETRY': '1', 'DO_NOT_TRACK': '1'}
```

**Qué observar:** mover una sola escena produce dos problemas: un hueco antes (6 → 7 s) y un solape
después (la escena 3 termina en 10 s, pero la 4 empieza en 9 s). En una corrida, cualquiera de ellos
detiene el pipeline en `VALIDATING_LINT` antes de abrir Chrome.

## Ejemplo 5: la API desde PowerShell

Con el servidor en marcha (`uv run python -m hyperframes_studio.main`):

```powershell
$api = "http://127.0.0.1:8022"
Invoke-RestMethod "$api/api/status"
```

**Respuesta real** (JSON devuelto por la API, en una máquina con Node.js y sin Ollama):

```json
{
  "status": "ok",
  "orchestrator_state": "IDLE",
  "run_in_progress": false,
  "ollama_url": "http://127.0.0.1:11434",
  "model": "qwen3.5:9b",
  "ollama_reachable": false,
  "npx_available": true,
  "last_render": null,
  "last_eval": null
}
```

Un brief fuera de contrato se rechaza con `422` antes de tocar Ollama o HyperFrames:

```powershell
Invoke-RestMethod -Method Post -Uri "$api/api/pipeline/run" -ContentType "application/json" `
    -Body '{"model": "qwen3.5:cloud"}'
```

**Cuerpo real de la respuesta `422`:**

```json
{"detail":[{"type":"value_error","loc":["body","model"],"msg":"Value error, El modelo debe ser local, no cloud: revisa OLLAMA_MODEL o el campo model.","input":"qwen3.5:cloud","ctx":{"error":{}}}]}
```

Y una duración menor de 5 s (`{"target_duration": 2}`):

```json
{"detail":[{"type":"greater_than_equal","loc":["body","target_duration"],"msg":"Input should be greater than or equal to 5","input":2,"ctx":{"ge":5.0}}]}
```

Si lanzas una corrida mientras otra sigue activa, la API responde `409`.

## Ejemplo 6: la línea JSONL

Tras un render correcto, `.local/eval_results.jsonl` recibe una línea con la forma descrita en
[EVALUATION.md](EVALUATION.md#formato-de-la-línea-jsonl). Para comparar modelos, filtra las líneas con
`director_source = "ollama"` y `duration_measured = true`.

## Ejemplo 7: render real con HyperFrames

Render hecho el 2026-11-11 en Linux, con Node.js 22, FFmpeg y `hyperframes@0.8.34`. Se usó la
composición que escribe la demo en `.local/workspace/` con las escenas calibradas, sin Ollama:

```bash
cd .local/workspace
HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 npx --yes hyperframes@0.8.34 render -o ../output/tutorial_hyperframes.mp4
```

Final de la salida:

```text
  ██████████████████████░░░  90%  Assembling final video
  █████████████████████████  100%  Render complete

◇  .../tutorial_hyperframes.mp4
   2.7 MB · 15.0s video · rendered in 41.0s
```

Medición con `ffprobe`:

```text
codec_name=h264
width=1920
height=1080
r_frame_rate=30/1
nb_frames=450
duration=15.000000
size=2780372
```

**Qué observar:** salen las cinco escenas con su etiqueta, el titular y el paso («Paso 2 de 5»). En
la escena 2, el fragmento `<div class="clip" data-start="0" data-duration="3">` aparece como texto
dentro del bloque de código: el escapado funciona y el fragmento no se convierte en un clip.

> **Nota:** en el entorno de esta prueba no había salida a `cdn.jsdelivr.net`, así que se sirvió
> `gsap.min.js` 3.14.2 (el mismo archivo, descargado con `npm pack gsap@3.14.2`) desde el propio
> workspace. Sin ese archivo, HyperFrames detiene el render con `sub_timeline_script_failure` y el
> estudio marca la corrida como fallida. Lo explica el punto 9 de [TROUBLESHOOTING.md](TROUBLESHOOTING.md#9-sub_timeline_script_failure-gsap-no-carga).

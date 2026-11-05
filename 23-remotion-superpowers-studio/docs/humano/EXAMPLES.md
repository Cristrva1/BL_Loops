# Ejemplos resueltos: 23-remotion-superpowers-studio

Cada salida de este documento se obtuvo ejecutando el comando indicado, con Node.js 22, FFmpeg 6.1,
`npm ci` hecho y **sin Ollama**. Lo que depende del modelo se indica como «forma esperada». Los
tiempos de render y los tamaños varían de una máquina (y de una corrida) a otra.

## Ejemplo 1: demo completa

```powershell
uv run remotion-studio-demo
```

**Salida real:**

```text
=== BL_Loops: Laboratorio 23 - Remotion Superpowers Studio ===
1. Conectando a Ollama (http://127.0.0.1:11434) con modelo: qwen3.5:9b
2. Brief de video: 'Demostrar Remotion y el patrón Remotion Superpowers con React y IA Local' (12.0s @ 30 FPS)
Ollama no entregó escenas (All connection attempts failed); se usan escenas calibradas.
3. Origen de las escenas: fallback (ConnectError al consultar Ollama)

========================================================
[OK] VIDEO REMOTION RENDERIZADO EXITOSAMENTE:
   - Archivo: .local/output/remotion_superpowers.mp4
   - Duración: 12.0s
   - Resolución: 1920x1080 (30 FPS)
   - Fotogramas Totales: 360
   - Tamaño: 2644.73 KB
   - Tiempo de render: 29.53s
========================================================

[OK] Evaluación exportada a: .local/eval_results.jsonl
[OK] Aprobada: True
```

**Qué observar:**

- La línea 4 viene del registro (`logging`) del director; la línea 3, de la demo. Es el mismo aviso
  de fallback en dos capas.
- `Duración`, `Resolución` y `Fotogramas Totales` los mide `ffprobe` sobre el MP4.
- Otra corrida idéntica produjo `2646.45 KB`: los fotogramas y la duración coinciden, pero el
  archivo no es idéntico byte a byte. «Determinista» aquí significa mismo contenido y misma
  duración, no mismo archivo.

**Forma esperada con Ollama activo:** `3. Origen de las escenas: ollama`, titulares distintos en cada
corrida y los mismos 360 fotogramas, porque los calcula el estudio.

## Ejemplo 2: configuración insegura rechazada

```powershell
$env:OLLAMA_MODEL = "qwen3.5:cloud"
uv run remotion-studio-demo
Remove-Item Env:OLLAMA_MODEL
```

**Salida real** (código de salida `2`):

```text
Configuracion invalida: El modelo debe ser local, no cloud: revisa OLLAMA_MODEL o el campo model.
```

## Ejemplo 3: de segundos a fotogramas

Guarda como `fotogramas.py`:

```python
import asyncio

from remotion_studio.ollama_director import RemotionOllamaDirector
from remotion_studio.schemas import RemotionBrief

for seconds in (10.0, 7.0):
    brief = RemotionBrief(target_duration=seconds)
    director = RemotionOllamaDirector(base_url="http://127.0.0.1:9")  # sin Ollama: fallback
    scenes = asyncio.run(director.generate_scenes(brief))
    frames = [s.duration_in_frames for s in scenes]
    print(f"{seconds} s -> pedidos {round(seconds * 30)} fotogramas | escenas {frames} | suma {sum(frames)} = {sum(frames) / 30:.2f} s")
```

```powershell
uv run python fotogramas.py
```

**Salida real** (sin las líneas de aviso del registro):

```text
10.0 s -> pedidos 300 fotogramas | escenas [75, 75, 75, 75] | suma 300 = 10.00 s
7.0 s -> pedidos 210 fotogramas | escenas [52, 52, 52, 52] | suma 208 = 6.93 s
```

**Qué observar:** 210 / 4 no es exacto y la división entera pierde 2 fotogramas: el video duraría
6,93 s. La evaluación lo aprueba porque el margen es de 1 s, pero el reparto se puede mejorar: es el
[ejercicio intermedio](EXERCISES.md#intermedio-que-no-se-pierda-ningún-fotograma).

## Ejemplo 4: lo que lee React

Segunda escena de `src/video_composition/scenes.json` tras la demo:

```json
{
  "id": "scene-2-timing",
  "title": "Control por Fotogramas",
  "startFrame": 90,
  "durationInFrames": 90,
  "headline": "Sincronía Milimétrica por Fotogramas",
  "subheadline": "Usa useCurrentFrame(), interpolate() y spring() para animaciones fluidas sin caídas de cuadros.",
  "bgGradient": "linear-gradient(135deg, #090d16 0%, #064e3b 100%)",
  "accentColor": "#10b981",
  "badge": "Frame Accuracy",
  "code": "const frame = useCurrentFrame();"
}
```

**Qué observar:** `MainComposition.tsx` crea un `<Sequence from={90} durationInFrames={90}>` con
estos datos. Dentro, `useCurrentFrame()` vuelve a empezar en 0: la escena no sabe en qué segundo del
video está, solo cuántos fotogramas lleva. Si el modelo propone un color o un gradiente que no es
`#rrggbb` o `linear-gradient(...)`, se sustituye por el valor base antes de escribir el archivo.

## Ejemplo 5: renderizar un solo fotograma

Renderizar 360 fotogramas tarda ~30 s; para revisar un cambio basta uno:

```powershell
npx remotion still src/video_composition/index.ts MainVideo .local/still_frame_100.png --frame=100
```

**Salida real** (última línea; según el entorno, Remotion añade antes avisos sobre la memoria):

```text
Rendered 1/1
```

El PNG mide 1920×1080. El fotograma 100 pertenece a la segunda escena (90–179): dentro de ella,
`useCurrentFrame()` devuelve 10. Muestra la escena «Sincronía Milimétrica por Fotogramas» con la
barra de progreso inferior a algo más de un cuarto.

## Ejemplo 6: la API desde PowerShell

Con el servidor en marcha (`uv run python -m remotion_studio.main`):

```powershell
$api = "http://127.0.0.1:8023"
Invoke-RestMethod "$api/api/status"
```

**Respuesta real** (antes de la primera corrida):

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

Un brief con otros fps se rechaza porque `Root.tsx` fija 30:

```powershell
Invoke-RestMethod -Method Post -Uri "$api/api/pipeline/run" -ContentType "application/json" -Body '{"fps": 60}'
```

**Cuerpo real de la respuesta `422`:**

```json
{"detail":[{"type":"literal_error","loc":["body","fps"],"msg":"Input should be 30","input":60,"ctx":{"expected":"30"}}]}
```

`GET /api/scenes` devuelve el `scenes.json` actual: 4 escenas que empiezan en los fotogramas 0, 90,
180 y 270. Una segunda corrida lanzada mientras otra sigue activa recibe `409`.

## Ejemplo 7: la línea JSONL

Línea real añadida por la demo del ejemplo 1 (formateada; la marca de tiempo se sustituye):

```json
{
  "timestamp": "<fecha ISO-8601 UTC>",
  "lab_id": "23-remotion-superpowers-studio",
  "case_id": "EVAL-REMOTION-001",
  "model": "qwen3.5:9b",
  "success": true,
  "duration_actual": 12.0,
  "duration_expected": 12.0,
  "render_time_seconds": 29.53,
  "file_size_kb": 2644.73,
  "total_frames": 360,
  "scenes_count": 4,
  "metrics": {
    "resolution": "1920x1080",
    "fps": 30,
    "duration_delta_seconds": 0.0,
    "deterministic": true,
    "react_component_root": "MainVideo",
    "duration_measured": true,
    "director_source": "fallback"
  }
}
```

**Qué observar:** `director_source = "fallback"` indica que esta corrida prueba el render, no la
calidad del modelo. El criterio completo está en [EVALUATION.md](EVALUATION.md).

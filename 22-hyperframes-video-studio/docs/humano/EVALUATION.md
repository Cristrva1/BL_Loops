# Evaluación: 22-hyperframes-video-studio

## Qué se evalúa y qué no

La evaluación comprueba que el **pipeline** cumple su contrato: un MP4 medible con la duración
pedida. **No** juzga si el guion es bueno; para eso hay que leer las escenas en el panel.
`director_source` indica si el modelo participó.

## Caso `EVAL-HYPERFRAMES-001`

- **Entrada:** un `VideoBrief` (por defecto, 15 s sobre qué es HyperFrames).
- **Puertas previas** (si fallan, no hay evaluación porque la corrida termina en `FAILED`):
  1. El brief cumple el contrato (5–60 s, modelo local, 1920×1080 a 30 fps).
  2. El lint local no encuentra problemas.
  3. HyperFrames termina con código 0 y el MP4 no está vacío.
- **Criterios de aprobado** (`success = true` solo si se cumplen todos):
  1. `|duración medida − duración pedida| ≤ 1.0 s`, con la duración leída por `ffprobe`.
  2. El MP4 pesa más de 10 KB.

| Métrica | Significado | Cómo interpretarla |
|---|---|---|
| `resolution`, `fps` | Medidos con `ffprobe` | Deben ser `1920x1080` y `30` |
| `duration_delta_seconds` | Desvío respecto a lo pedido | Cerca de `0.0` |
| `duration_measured` | Si `ffprobe` midió algo | `false` invalida la corrida |
| `has_min_size` | MP4 de más de 10 KB | `false` sugiere un render vacío |
| `director_source` | `ollama` o `fallback` | Solo las corridas `ollama` dicen algo del modelo |
| `deterministic` | Render determinista para las mismas escenas | Siempre `true` |

## Formato de la línea JSONL

La demo o `POST /api/export` añaden una línea a `.local/eval_results.jsonl` con esta forma (los
valores numéricos dependen de la corrida):

```json
{"timestamp": "<fecha ISO-8601 UTC>", "lab_id": "22-hyperframes-video-studio", "case_id": "EVAL-HYPERFRAMES-001", "model": "qwen3.5:9b", "success": true, "duration_actual": 15.0, "duration_expected": 15.0, "render_time_seconds": "<segundos>", "file_size_kb": "<KB>", "scenes_count": 5, "metrics": {"resolution": "1920x1080", "fps": 30, "duration_delta_seconds": 0.0, "deterministic": true, "has_min_size": true, "duration_measured": true, "director_source": "fallback"}}
```

El JSONL no guarda el tema ni el texto de las escenas.

## Cómo comparar corridas

1. Misma duración, dos modelos (selector del panel); exporta cada corrida.
2. Descarta líneas con `director_source = "fallback"` o `duration_measured = false`.
3. Revisa a mano el HTML generado (pestaña «HTML HyperFrames») para juzgar el contenido.
4. El comparador central de BL_Loops solo importa este JSONL.

## Pruebas automáticas

`uv run pytest` ejecuta 28 pruebas sin red ni HyperFrames: configuración local, rechazo de modelos
cloud y duraciones imposibles, escapado de la plantilla con valores hostiles, lint (clip fantasma y
huecos), tiempos fijados por el estudio, parada antes del render si el lint falla, 409/422 de la API,
exclusión de telemetría, fallback visible y medición sin invenciones.

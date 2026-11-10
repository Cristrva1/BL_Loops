# Evaluación: 23-remotion-superpowers-studio

## Qué se evalúa y qué no

La evaluación comprueba que el **pipeline** cumple su contrato: un MP4 medible con la duración y los
fotogramas pedidos. **No** juzga la calidad del guion; `director_source` indica si el modelo
participó.

## Caso `EVAL-REMOTION-001`

- **Entrada:** un `RemotionBrief` (por defecto, 12 s = 360 fotogramas a 30 fps).
- **Puertas previas** (si fallan, la corrida termina en `FAILED` y no hay evaluación):
  1. El brief cumple el contrato (4–60 s, 30 fps, 1920×1080, modelo local).
  2. Remotion termina con código 0 y el MP4 no está vacío.
- **Criterios de aprobado** (`success = true` solo si se cumplen todos):
  1. `|duración medida − duración pedida| ≤ 1.0 s`, con la duración de `ffprobe`.
  2. El MP4 pesa más de 10 KB.

| Métrica | Significado | Cómo interpretarla |
|---|---|---|
| `resolution`, `fps` | Medidos con `ffprobe` | `1920x1080` y `30` |
| `total_frames` (campo raíz) | `nb_frames` del MP4 | `360` para 12 s |
| `duration_delta_seconds` | Desvío respecto a lo pedido | Hasta 0,1 s por la división entera de fotogramas |
| `duration_measured` | Si `ffprobe` midió algo | `false` invalida la corrida |
| `react_component_root` | Composición renderizada | `MainVideo` |
| `director_source` | `ollama` o `fallback` | Solo las corridas `ollama` dicen algo del modelo |

## Formato de la línea JSONL

Línea real de la verificación (la marca de tiempo se sustituye):

```json
{"timestamp": "<fecha ISO-8601 UTC>", "lab_id": "23-remotion-superpowers-studio", "case_id": "EVAL-REMOTION-001", "model": "qwen3.5:9b", "success": true, "duration_actual": 12.0, "duration_expected": 12.0, "render_time_seconds": 29.53, "file_size_kb": 2644.73, "total_frames": 360, "scenes_count": 4, "metrics": {"resolution": "1920x1080", "fps": 30, "duration_delta_seconds": 0.0, "deterministic": true, "react_component_root": "MainVideo", "duration_measured": true, "director_source": "fallback"}}
```

El JSONL no guarda el tema ni el texto de las escenas. `file_size_kb` varía unos KB entre corridas
iguales, así que no sirve para comparar modelos.

## Cómo comparar corridas

1. Misma duración, dos modelos (selector del panel); exporta cada corrida.
2. Descarta líneas con `director_source = "fallback"` o `duration_measured = false`.
3. Revisa los `scenes.json` de cada corrida (pestaña del panel o `git diff`) para juzgar el contenido.
4. El comparador central de BL_Loops solo importa este JSONL.

## Pruebas automáticas

`uv run pytest` ejecuta 21 pruebas sin red ni Remotion: configuración local, contrato del brief,
fallback visible con fotogramas exactos, `scenes.json` con estilos validados, 409/422 de la API,
evaluación, exportación y medición sin invenciones. `npm run typecheck` comprueba los tipos de la
composición React.

# Protocolo de Evaluación: 23-remotion-superpowers-studio

## Caso de Evaluación: `EVAL-REMOTION-001`
- **Nombre**: Generación y Renderizado de Video React con Remotion Superpowers e IA Local.
- **Entrada**: Brief de 12 segundos (360 fotogramas a 30 FPS).
- **Criterios de Aprobación**:
  1. Generación de 4 escenas correlativas con cálculo exacto de fotogramas.
  2. Actualización exitosa de `scenes.json`.
  3. Ejecución de `@remotion/cli` produciendo un MP4 determinista.
  4. Duración exacta verificada con `ffprobe` ($12.0 \pm 1.0\text{ s}$).
  5. Tamaño de archivo superior a 10 KB.
  6. Registro en `.local/eval_results.jsonl`.

## Formato del Registro JSONL

```json
{
  "timestamp": "2026-09-11T05:28:00Z",
  "lab_id": "23-remotion-superpowers-studio",
  "case_id": "EVAL-REMOTION-001",
  "model": "qwen3.5:9b",
  "success": true,
  "duration_actual": 12.0,
  "duration_expected": 12.0,
  "render_time_seconds": 14.5,
  "file_size_kb": 920.3,
  "total_frames": 360,
  "scenes_count": 4,
  "metrics": {
    "resolution": "1920x1080",
    "fps": 30,
    "duration_delta_seconds": 0.0,
    "deterministic": true,
    "react_component_root": "MainVideo"
  }
}
```

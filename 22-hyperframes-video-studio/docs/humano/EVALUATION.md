# Protocolo de Evaluación: 22-hyperframes-video-studio

## Caso de Evaluación: `EVAL-HYPERFRAMES-001`
- **Nombre**: Generación y Renderizado de Video Explicativo HyperFrames con IA Local.
- **Entrada**: Brief de 15 segundos sobre capacidades de HyperFrames.
- **Criterios de Aprobación**:
  1. Generación válida de 5 escenas correlativas.
  2. Compilación de HTML estructurado con `data-start`, `data-duration` y GSAP timeline.
  3. Ejecución exitosa de `npx hyperframes render` sin errores fatales.
  4. Generación de un archivo `.mp4` legible con tamaño mayor a 10 KB.
  5. Desviación temporal del video final $\le 1.0$ segundo respecto a la duración solicitada.
  6. Registro del evento en `.local/eval_results.jsonl`.

## Formato del Registro JSONL

```json
{
  "timestamp": "2026-09-11T05:18:00Z",
  "lab_id": "22-hyperframes-video-studio",
  "case_id": "EVAL-HYPERFRAMES-001",
  "model": "qwen3.5:9b",
  "success": true,
  "duration_actual": 15.0,
  "duration_expected": 15.0,
  "render_time_seconds": 13.2,
  "file_size_kb": 26.5,
  "scenes_count": 5,
  "metrics": {
    "resolution": "1920x1080",
    "fps": 30,
    "duration_delta_seconds": 0.0,
    "deterministic": true,
    "has_min_size": true
  }
}
```

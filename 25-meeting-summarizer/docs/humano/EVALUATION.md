# Evaluación y Criterios de Calidad · Laboratorio 25

Este documento define la suite de evaluación determinista para la extracción de resúmenes y compromisos.

## 1. Métricas de evaluación

Para que una minuta generada por IA sea considerada aprobada (**PASS**), debe cumplir con los siguientes umbrales:

| Métrica | Definición | Umbral mínimo |
|---|---|---|
| **Precisión de participantes** | Porcentaje de personas mencionadas en el transcript que fueron identificadas correctamente en la minuta. | >= 90% |
| **Recall de compromisos** | Porcentaje de tareas explícitas acordadas en la llamada que fueron capturadas en `action_items`. | >= 85% |
| **Exactitud de plazos** | Concordancia exacta entre los plazos mencionados en voz y los valores en el campo `deadline`. | >= 90% |
| **Cero Alucinaciones** | Ninguna tarea ni decisión registrada puede ser inventada por el modelo. | 100% |
| **Tiempo de respuesta** | Tiempo total en procesar una reunión típica de 15 minutos (< 2,000 palabras) con `qwen3.5:9b`. | < 25 segundos |

## 2. Contrato de la corrida JSONL

Cada procesamiento exitoso genera un registro en `.local/runs/` con la siguiente estructura:

```json
{
  "run_id": "run_meet_1234_abc89f",
  "meeting_id": "meet_1234",
  "timestamp": "2026-09-19T11:00:00Z",
  "model": "qwen3.5:9b",
  "mode": "completo",
  "duration_ms": 12450.5,
  "metrics": {
    "total_words": 1540,
    "total_turns": 24,
    "participants_count": 4,
    "decisions_count": 3,
    "action_items_count": 5,
    "topics_count": 3,
    "open_questions_count": 1
  },
  "report": { ... }
}
```

Estos registros pueden ser importados en cualquier momento por el dashboard de evaluación transversal de `BL_Loops` para comparar la calidad entre diferentes modelos de Ollama (`qwen3.5:9b`, `qwen3.5:4b`, `gemma4:e4b`).

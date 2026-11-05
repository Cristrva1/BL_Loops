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

Cada procesamiento exitoso genera un archivo en `.local/runs/` con **un registro sanitizado**: métricas
y una huella del informe, nunca su contenido. El informe completo (nombres, tareas, minuta) se guarda
únicamente en `.local/data/meetings.db`.

```json
{
  "run_id": "run_meet_1234_abc89f",
  "meeting_id": "meet_1234",
  "timestamp": "2026-11-05T11:00:00+00:00",
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
  "report_sha256": "<huella SHA-256 del informe guardado en SQLite>",
  "raw_content_stored": false
}
```

(Valores ilustrativos.) `report_sha256` permite comprobar que una traza corresponde a un informe
concreto de SQLite sin copiarlo. Antes del 2026-11-05 la traza incluía el informe completo; ese
comportamiento se retiró porque exponía datos personales al comparador.

## 3. Caso de práctica con clave de corrección

`fixtures/meet_compromisos_ambiguos.txt` tiene una clave conocida (ver el
[ejemplo 6](EXAMPLES.md#ejemplo-6--resumir-una-reunión-con-compromisos-ambiguos-necesita-ollama)): una
decisión, una idea no aprobada, dos compromisos completos, un compromiso sin responsable y una
pregunta abierta. Úsalo para calcular a mano el recall de compromisos y las alucinaciones de cada
modelo antes de confiar en una transcripción larga.

## 4. Verificación automática

```powershell
uv run pytest
uv run ruff check .
```

Las pruebas cubren el parser de cada formato, el troceador con solapamiento, el comando `parse`, la
validación de endpoint y modelo locales, el descubrimiento seguro del `.env`, el almacenamiento SQLite,
la API y la sanitización del JSONL.

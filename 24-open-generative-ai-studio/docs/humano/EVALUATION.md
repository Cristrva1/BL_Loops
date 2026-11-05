# Evaluación: 24-open-generative-ai-studio

## Qué se evalúa y qué no

La evaluación comprueba que el **pipeline** cumple su contrato: un animatic medible, con la duración
pedida y con prompt en cada plano. **No** juzga la calidad narrativa del storyboard. Para eso sirve
`director_source`: indica si el modelo participó.

## Caso `EVAL-OPEN-GENAI-001`

- **Entrada:** un `StoryboardProject` (por defecto, «Expedición Nebular», 12 s).
- **Criterios de aprobado** (`success = true` solo si se cumplen todos):
  1. El render termina sin error (`RenderResult.success`).
  2. `|duración medida − duración pedida| ≤ 1.0 s`, con la duración leída por `ffprobe`.
  3. El MP4 pesa más de 10 KB.
- **Métricas informativas** (no cambian `success`, pero hay que leerlas):

| Métrica | Significado | Cómo interpretarla |
|---|---|---|
| `resolution`, `fps` | Medidos con `ffprobe` | Deben ser `1920x1080` y `30` |
| `duration_delta_seconds` | Desvío respecto a lo pedido | Normalmente `0.0` |
| `duration_measured` | Si `ffprobe` midió algo | `false` invalida cualquier conclusión |
| `all_shots_have_prompts` | Cada plano tiene un prompt de más de 20 caracteres | Un modelo que omite prompts da `false` |
| `director_source` | `ollama` o `fallback` | Solo las corridas `ollama` dicen algo del modelo |
| `deterministic` | El render es determinista para unos mismos planos | Siempre `true` en este estudio |

## Formato de la línea JSONL

`POST /api/export` (botón «Exportar evaluación JSONL») o la demo añaden una línea a
`.local/eval_results.jsonl`. Ejemplo real, con la marca de tiempo sustituida:

```json
{"timestamp": "<fecha ISO-8601 UTC>", "lab_id": "24-open-generative-ai-studio", "case_id": "EVAL-OPEN-GENAI-001", "model": "qwen3.5:9b", "success": true, "duration_actual": 12.0, "duration_expected": 12.0, "render_time_seconds": 5.42, "file_size_kb": 179.52, "shots_count": 4, "metrics": {"resolution": "1920x1080", "fps": 30, "duration_delta_seconds": 0.0, "deterministic": true, "all_shots_have_prompts": true, "duration_measured": true, "director_source": "fallback"}}
```

El JSONL no contiene la sinopsis ni el texto de los planos: solo el modelo, los tiempos y las
métricas.

## Cómo comparar corridas

1. Ejecuta la misma sinopsis con dos modelos (selector «Modelo local» del panel) y exporta cada una.
2. Descarta las líneas con `director_source = "fallback"` o `duration_measured = false`.
3. Compara `all_shots_have_prompts` y revisa a mano los storyboards en el panel: la calidad
   narrativa sigue siendo una evaluación humana.
4. El comparador central de BL_Loops solo importa este JSONL; no consulta el estudio en vivo.

## Pruebas automáticas

`uv run pytest` ejecuta 37 pruebas sin red ni Ollama. Cubren configuración local, rechazo de modelos
cloud, lectura y rechazo de respuestas del modelo, fallback visible, escapado de texto y de fuentes,
fallo explícito de un plano, medición sin invenciones, API (estado, 409, 422, Prompt Studio) y
exportación JSONL. La prueba de render real se omite si FFmpeg no está instalado.

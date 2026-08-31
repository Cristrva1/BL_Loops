# Evaluación del chat mínimo

## Caso base

**ID:** `CHAT-BASIC-001@0.1.0`  
**Objetivo:** mantener una conversación de texto coherente durante una sesión local.

Entrada sintética sugerida:

```text
Recuerda que la figura de prueba tiene cuatro lados.
¿Qué figura sencilla podría ser y cuántos lados te indiqué?
```

## Criterios de aprobado

- La CLI arranca desde PowerShell con `uv run single-agent`.
- El banner indica `gemma4:e4b` y un endpoint local.
- Una respuesta no vacía y relacionada llega desde Ollama.
- El segundo turno recibe el historial del primero.
- Solo se muestra `message.content`; el pensamiento no se imprime ni se conserva.
- No se realizan tools, búsquedas, escrituras externas ni fallback cloud.
- La traza termina correctamente y no contiene texto crudo de la conversación.
- `uv run single-agent-validate` puede importarla.

## Verificación automática

```powershell
uv run pytest
uv run ruff check .
```

Las pruebas cubren:

- valores por defecto y prioridad de `.env`;
- rechazo de endpoints no locales y rutas de salida inseguras;
- transporte directo que no hereda proxies ni sigue redirecciones HTTP;
- rechazo explícito de etiquetas de modelo cloud;
- contrato exacto enviado a `/api/chat`;
- exclusión del campo de pensamiento;
- contexto entre turnos;
- errores sin retry automático;
- sanitización y reimportación del JSONL;
- independencia respecto de documentación y otros laboratorios.

## Demostración real

1. Ejecuta una ronda de calentamiento no puntuada.
2. Abre una sesión nueva y realiza el caso base.
3. Termina con `/salir`.
4. Valida la corrida más reciente.
5. Revisa que haya una ruta completa por turno y un solo evento terminal.

La calidad semántica requiere observación humana: una prueba determinista no puede garantizar por sí sola que toda respuesta futura sea congruente.

## Métricas disponibles

| Métrica | Fuente | Uso |
|---|---|---|
| `wall_duration_ms` | Reloj monotónico del cliente | Tiempo percibido por el humano |
| `ollama_duration_ms` | `total_duration` de Ollama | Tiempo reportado por el servidor |
| `prompt_tokens` | `prompt_eval_count` | Tamaño efectivo de entrada |
| `output_tokens` | `eval_count` | Tamaño de la respuesta |
| `input_chars` / `response_chars` | Conteo local | Evidencia de entrada/salida sin guardar contenido |

RAM y VRAM no se muestrean todavía. Al no existir una cohorte comparable, los scores normalizados permanecen aplazados.

## Exportación

Cada línea de `.local/runs/*.jsonl` cumple `contracts/run-event.schema.json` y comparte `run_id`. El primer evento es `run.started`; el último es `run.completed` o `run.failed`.

## Estado frente al laboratorio completo

Este corte aprueba como **chat CLI mínimo**. No debe declararse terminado el laboratorio amplio de agente único del plan maestro hasta añadir, mediante decisiones posteriores, visualización web real, SSE, tools simuladas y comparación con los cuatro modelos iniciales.

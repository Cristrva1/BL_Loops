# AGENTS.md - 23-remotion-superpowers-studio

Instrucciones operativas para futuras sesiones de agentes en este laboratorio.

## Propósito
Este laboratorio pone a prueba el motor de video programático `remotion` (`remotion-dev/remotion`) junto con el patrón agéntico de `remotion-superpowers` (`DojoCodingLabs/remotion-superpowers`).
Integra un Director de IA Local (Ollama: `qwen3.5:9b`) que diseña guiones, coreografía de escenas, cálculo de fotogramas ($fps \times \text{segundos}$), tipografía cinética y transiciones en React, renderizando un MP4 determinista con `@remotion/cli`.

## Reglas locales
- La IA es 100% local a través de Ollama (`127.0.0.1:11434`).
- No fallbacks a APIs externas o de pago.
- El backend Python reside en `src/remotion_studio/`.
- La composición de React reside en `src/video_composition/`.
- Los artefactos generados se guardan bajo `.local/output/`.
- El runtime no debe importar ni depender de archivos dentro de `docs/humano/`.
- Pruebas deterministas en `tests/` ejecutadas con `uv run pytest`.
- Exportación de métricas en `.local/eval_results.jsonl`.

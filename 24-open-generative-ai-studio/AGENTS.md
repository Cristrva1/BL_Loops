# AGENTS.md - 24-open-generative-ai-studio

Instrucciones operativas para futuras sesiones de agentes en este laboratorio.

## Propósito
Este laboratorio evalúa y adapta la arquitectura de **Open-Generative-AI** (`Anil-matcha/Open-Generative-AI`) a un entorno de **IA 100% Local con Ollama (`qwen3.5:9b`)**.
Implementa un workbench con estudios especializados:
- **Prompt Studio**: Refinador y expansor cinematográfico de prompts (cámara, iluminación, lentes, atmósfera).
- **Storyboard Studio**: Desglose de guiones en planos cinematográficos y tipos de toma.
- **Workflow & Media Engine**: Ensamblado determinista de animatics y previsualizaciones en video MP4 con FFmpeg.

## Reglas locales
- Utiliza la API local de Ollama en `http://127.0.0.1:11434`.
- El backend reside en `src/open_genai_studio/`.
- Los artefactos y bases de datos SQLite se almacenan bajo `.local/`.
- No importar ni depender de archivos dentro de `docs/humano/`.
- Pruebas deterministas con `uv run pytest`.
- Exportación JSONL conforme al contrato en `.local/eval_results.jsonl`.

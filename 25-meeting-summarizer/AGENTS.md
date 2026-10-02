# Reglas operativas para 25-meeting-summarizer

Este archivo complementa el `AGENTS.md` de la raíz para el laboratorio de resúmenes de videollamadas.

## Principios del laboratorio

1. **Aislamiento**: Este laboratorio no importa código, módulos ni bases de datos de otros laboratorios. Utiliza su propio entorno Python (`uv`) y su propio frontend React.
2. **IA 100% Local**: La inferencia se realiza exclusivamente contra el endpoint local de Ollama (`http://127.0.0.1:11434`), con modelos como `qwen3.5:9b` o `qwen3.5:4b`. No se permiten llamadas a APIs en la nube.
3. **Persistencia Local**: La base de datos es SQLite (`.local/data/meetings.db`). Las corridas y evaluaciones se exportan a `.local/runs/*.jsonl`.
4. **Respeto a los Contratos**: Todos los contratos de entrada, salida y eventos SSE se definen con Pydantic en `meeting_summarizer.contracts`.
5. **Enfoque Didáctico**: El código debe ser legible, tipado con Python 3.12 (`type | None`, slots en dataclasses cuando corresponda) y estar acompañado de documentación completa en `docs/humano/`.

# 09 · RAG agéntico: un agente de ventas que decide qué buscar

> **Pregunta:** ¿puede el agente decidir cuándo y cómo buscar sin perder el control del runtime?
> **Nivel:** 3 · **Tiempo:** ~60 min · **Necesita Ollama:** sí, con `qwen3.5:4b` y `qwen3-embedding:latest`

Un agente local de ventas consultivas. El modelo **formula** la consulta mediante *tool calling*;
el runtime **autoriza y ejecuta como máximo una** herramienta, `search_sales_library`, sobre un
índice privado híbrido (FTS5 + `qwen3-embedding:latest`, como en el 07). Si la llamada del modelo es
inválida, el runtime usa la pregunta literal como consulta (*fallback* determinista y registrado).
La respuesta cita archivo y líneas, la memoria vive solo en RAM y la traza JSONL no guarda texto
crudo. No hay CRM, navegador, correo ni fallback cloud.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\09-agentic-rag
uv sync --locked --all-groups
uv run sales-agent index --source .\fixtures\evaluation-corpus       # corpus sintético pequeño
uv run sales-agent ask "¿Cómo vendo una vivienda sin presionar?"
uv run sales-agent chat                                               # /estado, /limpiar, /salir
uv run sales-agent-validate
```

Con el corpus de libros: `uv run sales-agent index --source ..\docs\humano\Libros`.

## Qué deberías ver

```text
Indice listo: 2/3 docs, 2 vectores, 2 secciones excluidas, 0 fuentes no revisadas.
```

Ese recuento es determinista: `03-ruido.md` solo contiene secciones excluidas. Cada turno imprime
cuatro nodos — `[1/4 decidir]`, `[2/4 herramienta]`, `[3/4 evidencia]`, `[4/4 responder]` — y la ruta
de decisión: `model_tool_call` si el modelo pidió bien la herramienta o `runtime_fallback` si no.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/sales_agent/` | Agente acotado, herramienta, índice híbrido, filtro, prompt, CLI y JSONL |
| `tests/` | Pruebas con modelo y embedder falsos: no necesitan Ollama |
| `fixtures/evaluation-corpus/` | Venta relacional, venta desafiante y una ficha contaminada |
| `contracts/run-event.schema.json` | Contrato de cada evento exportado |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | Índice privado y trazas sanitizadas (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): chat, RAG y agente comparados.
2. [Inicio rápido](docs/humano/QUICKSTART.md): índice, primera pregunta y conversación.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): cómo el runtime acota las decisiones del modelo.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [08-graph-rag](../08-graph-rag/README.md) y, para la búsqueda híbrida, [07-vector-rag](../07-vector-rag/README.md).
**Sigue con:** [25-meeting-summarizer](../25-meeting-summarizer/README.md), una aplicación completa.

## Estado y límites

- **Implementado (corte A0):** tool calling local con una búsqueda por turno, fallback determinista
  visible, índice híbrido propio, memoria acotada en RAM, citas validadas y JSONL sanitizado.
- **Aplazado:** reformular y volver a buscar en bucle, LangGraph, CrewAI y Flowise.
- El corpus de libros contiene sobre todo fichas editoriales: «experto» describe el rol, no una
  garantía de conocimiento completo.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

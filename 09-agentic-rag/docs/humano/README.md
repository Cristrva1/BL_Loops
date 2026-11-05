# Guía humana: agente local experto en ventas

## Objetivo

Aprender la diferencia entre un chat, un RAG y un agente. Aquí el modelo no recibe todos los
libros ni puede actuar fuera del equipo. Decide una consulta, llama una herramienta local
acotada, observa la evidencia y produce una respuesta citada.

El término “experto” describe su rol y método —ventas consultivas, éticas e inmobiliarias—,
no una garantía de que el corpus sea completo. Con las fuentes actuales puede sintetizar
principios presentes en descripciones editoriales; no puede reconstruir capítulos que no
existen en los Markdown.

## Antes de empezar

- **Laboratorios previos:** [02-single-agent](../../../02-single-agent/docs/humano/README.md) (chat)
  y [07-vector-rag](../../../07-vector-rag/docs/humano/README.md) (búsqueda híbrida). Este laboratorio
  los combina y añade la decisión del modelo.
- **Software:** `uv` y Ollama con `qwen3.5:4b` y `qwen3-embedding:latest`.
- **Vocabulario:** [agente](../../../docs/humano/maestro/GLOSARIO.md#agente),
  [herramienta y tool calling](../../../docs/humano/maestro/GLOSARIO.md#herramienta-tool-y-tool-calling)
  y [fallback visible](../../../docs/humano/maestro/GLOSARIO.md#fallback-visible).
- **Sin Ollama** puedes ver cómo el runtime acota al modelo con los ejemplos 1 y 2 de
  [EXAMPLES.md](EXAMPLES.md).

## Chat, RAG y agente en una tabla

| | Chat (02) | RAG (07) | Agente RAG (09) |
|---|---|---|---|
| ¿Quién decide buscar? | Nadie: no busca | El programa, siempre | El modelo propone; el runtime autoriza |
| ¿Con qué consulta? | — | La pregunta literal | La que formule el modelo (o la literal si falla) |
| ¿Cuántas búsquedas? | 0 | 1 | Como máximo 1 por turno |
| ¿Memoria? | Todo el historial | No | Últimos 4 turnos en RAM |
| ¿Cita fuentes? | No | Sí | Sí |

## Mapa visual

```text
pregunta + memoria RAM acotada
             │
             ▼
     [DECIDE · qwen3.5:4b]
        │ tool call válido
        │ o fallback del runtime
        ▼
 [search_sales_library · 1 máximo]
        │
        ├─ FTS5/BM25 ─────┐
        └─ Qwen3 vector ──┼─ RRF ponderado ─ fuentes [S1..Sn]
                          │
                          ▼
       [GROUND · datos no confiables delimitados]
                          │
                          ▼
        [ANSWER · consejo + citas + límites]
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
     pantalla humana          JSONL sin texto crudo
```

Estados visibles por turno: `decide → search_sales_library → ground → answer → completed`.
Si no hay resultados: `decide → search_sales_library → no_matches → completed`. Un error
termina en `run.failed`; no existe un retry oculto.

## Recorrido guiado

1. Sigue [QUICKSTART.md](QUICKSTART.md) para preparar el entorno y el índice.
2. Recorre los [ejemplos 1 y 2](EXAMPLES.md) sin Ollama.
3. Ejecuta una pregunta con `sales-agent ask` y localiza los cuatro nodos impresos.
4. Comprueba que la respuesta use `[S1]` y que debajo aparezcan archivo, líneas y estado.
5. Abre una conversación con `sales-agent chat`, consulta `/estado` y después `/limpiar`.
6. Valida la última corrida con `sales-agent-validate`.
7. Usa [EXERCISES.md](EXERCISES.md) y [EVALUATION.md](EVALUATION.md) para comparar resultados.

## Qué aprenderás

- Por qué 0.66 MiB de texto no exige una base vectorial por capacidad.
- Por qué una pregunta parafraseada sí puede justificar embeddings.
- Cómo el runtime, no el modelo, limita herramientas y efectos.
- Cómo la higiene del corpus puede importar más que el algoritmo de búsqueda.
- Cómo separar memoria conversacional, índice de conocimiento y observabilidad.

## Dónde encaja en la ruta

- **Antes:** [08-graph-rag](../../../08-graph-rag/docs/humano/README.md) cierra las variantes de
  recuperación sin autonomía.
- **Después:** [25-meeting-summarizer](../../../25-meeting-summarizer/docs/humano/README.md), una
  aplicación completa, y [13-sales-knowledge-curator](../../../13-sales-knowledge-curator/docs/humano/README.md),
  que enseña a mejorar el corpus que este agente consulta.

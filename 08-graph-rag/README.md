# 08 · Graph RAG: encadenar relaciones que viven en documentos distintos

> **Pregunta:** ¿cuándo las relaciones explícitas justifican el costo de construir un grafo?
> **Nivel:** 3 · **Tiempo:** ~60 min · **Necesita Ollama:** solo `ask` (`qwen3.5:4b`); `index` y `search` no

Algunas respuestas no están en ningún fragmento: hay que **unir** un responsable, una aplicación, un
proveedor y una fecha que viven en archivos distintos. Este laboratorio importa Markdown con
*triples* visibles (`` `Sujeto` --predicado--> `Objeto` ``), construye un grafo en SQLite, recorre
rutas de hasta tres saltos en ambos sentidos y pide a Ollama una respuesta citada. Compara esa ruta
con una búsqueda léxica FTS5 sobre los mismos documentos. No usa Neo4j, Microsoft GraphRAG,
embeddings ni otro laboratorio.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\08-graph-rag
uv sync --locked --all-groups
uv run graph-rag index --source .\fixtures\evaluation-corpus
uv run graph-rag search --mode compare "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"   # sin Ollama
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"                    # con Ollama
uv run graph-rag-validate
```

## Qué deberías ver

```text
Indice listo: 5/5 docs, 14 nodos, 11 aristas extraidas, 9 fragmentos.

1.
Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01
...
extracted | AtlasCRM --depends_on--> NortePay | 02-proyectos.md:L14-L14
inferred | Ana Ruiz --owns/depends_on/freeze_date--> 2026-03-01 | hops=3

Comparacion lexica:
1. 03-proveedores.md:L3-L9 score=-2.246
...
```

La ruta del grafo usa `02-proyectos.md`, el eslabón AtlasCRM → NortePay. El ranking léxico **no**
lo trae entre sus cinco primeros: ese hueco es la lección del laboratorio.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/graph_rag/` | Extracción de triples, grafo SQLite, BFS, prompt, pipeline y JSONL |
| `tests/` | Pruebas herméticas: no necesitan Ollama |
| `fixtures/evaluation-corpus/` | Personas, aplicaciones, proveedores, calendario y distractores |
| `examples/questions.txt` | Preguntas de uno, dos y tres saltos |
| `contracts/run-event.schema.json` | Contrato de cada evento exportado |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | Grafo SQLite y trazas sanitizadas (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): nodos, aristas, saltos y aristas inferidas.
2. [Inicio rápido](docs/humano/QUICKSTART.md): indexar, recorrer y comparar.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): rutas reales de uno a tres saltos y sus límites.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [07-vector-rag](../07-vector-rag/README.md).
**Sigue con:** [09-agentic-rag](../09-agentic-rag/README.md), donde un agente decide qué buscar.

## Estado y límites

- **Implementado:** triples deterministas, grafo SQLite con publicación atómica, BFS acotado en ambos
  sentidos, aristas `extracted`/`inferred`, diagramas Mermaid por ruta, contraste léxico, citas y JSONL.
- **Aplazado:** Microsoft GraphRAG, CodeGraph, Graphify, Neo4j, extracción con LLM y dashboard.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

# 06 · RAG léxico: buscar palabras antes de generar

> **Pregunta:** ¿cuánto aporta recuperar texto antes de introducir embeddings?
> **Nivel:** 3 · **Tiempo:** ~45 min · **Necesita Ollama:** solo `ask` (`qwen3.5:4b`); `index` y `search` no

El RAG más pequeño que todavía merece ese nombre. Importa archivos Markdown a un índice SQLite FTS5
propio, **recupera** los fragmentos que comparten palabras con la pregunta, los **añade** al prompt
con su procedencia y pide a Ollama que **genere** una respuesta con citas `[S1]`, `[S2]` a archivo y
líneas. Si no encuentra nada, se abstiene sin llamar al modelo. No usa embeddings, nube, frameworks
RAG ni otro laboratorio.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\06-naive-rag
uv sync --locked --all-groups
uv run naive-rag index --source .\fixtures\evaluation-corpus          # 5 documentos sintéticos
uv run naive-rag search "¿Cuál es el plazo vigente para el primer seguimiento LUNA?"   # sin Ollama
uv run naive-rag ask "¿Cuál es el plazo vigente para el primer seguimiento LUNA?"      # con Ollama
uv run naive-rag-validate                                             # importa el JSONL
```

Con el corpus de libros: `uv run naive-rag index --source ..\docs\humano\Libros` y las preguntas de
`examples/questions.txt`.

## Qué deberías ver

`search` muestra exactamente el contexto que recibiría el modelo:

```text
Recuperador: SQLite FTS5 (BM25) | top_k=4 | Ollama no se invoca
bm25 de SQLite: cuanto mas negativo, mas relevante.
[S1] 01-politica-vigente.md:L3-L6 bm25=-2.681 | Política de seguimiento LUNA
[S2] 02-politica-obsoleta.md:L3-L6 bm25=-0.301 | Política histórica de seguimiento LUNA
[S3] 03-calificacion.md:L3-L3 bm25=-0.000 | Calificación sintética
[S4] 05-distractor.md:L3-L3 bm25=-0.000 | Documento distractor
```

La política obsoleta y un distractor sobre la luna también entran en el top-4: así se ve el límite
de buscar por palabras. `ask` recorre `[1/3 buscar] → [2/3 aumentar] → [3/3 generar]` y lista las
fuentes citadas.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/naive_rag/` | Configuración, índice FTS5, prompt, cliente Ollama, pipeline y JSONL |
| `tests/` | Pruebas herméticas: no necesitan Ollama |
| `fixtures/evaluation-corpus/` | Cinco documentos sintéticos: vigente, obsoleto, calificación, canal y distractor |
| `examples/questions.txt` | Preguntas iniciales para el corpus de libros |
| `contracts/run-event.schema.json` | Contrato de cada evento exportado |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/data/` y `.local/runs/` | Índice SQLite y trazas sanitizadas (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): RAG en tres pasos, BM25 y citas.
2. [Inicio rápido](docs/humano/QUICKSTART.md): indexar, buscar y preguntar.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): top-k, prompt aumentado, citas y abstención.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [05-agent-loops](../05-agent-loops/README.md).
**Sigue con:** [07-vector-rag](../07-vector-rag/README.md), que encuentra ideas aunque cambien las palabras.

## Estado y límites

- **Implementado:** índice FTS5 con publicación atómica, `search` sin modelo, generación con citas
  validadas, abstención sin llamar a Ollama y JSONL sanitizado.
- **Aplazado:** embeddings, PDF/OCR, reranking, conversación, API web y dashboard.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

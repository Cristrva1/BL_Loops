# 07 · RAG vectorial híbrido: encontrar ideas aunque cambien las palabras

> **Pregunta:** ¿cuándo la similitud semántica supera la búsqueda por palabras?
> **Nivel:** 3 · **Tiempo:** ~60 min · **Necesita Ollama:** sí, con `qwen3-embedding:latest` y `qwen3.5:4b`

Compara tres recuperadores sobre los **mismos** fragmentos: léxico (SQLite FTS5), vectorial
(embeddings de 768 dimensiones con `qwen3-embedding:latest` y similitud coseno) e híbrido (fusión
RRF ponderada 0.35 léxico / 0.65 vectorial). Antes de indexar elimina secciones conocidas como
contaminadas y conserva el estado de confianza de cada fuente. Después genera una respuesta con
citas a archivo y líneas.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\07-vector-rag
uv sync --locked --all-groups
ollama list                                          # deben aparecer qwen3-embedding y qwen3.5:4b
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag search --mode lexical "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode vector  "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode hybrid  "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag ask "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag-validate
```

Con el corpus de libros: `uv run vector-rag index --source ..\docs\humano\Libros` (tarda más: un
embedding local por fragmento).

## Qué deberías ver

```text
Indice listo: 4/5 docs, 4 vectores, 2 secciones excluidas, 0 fuentes no revisadas.
```

Esos recuentos no dependen del modelo: la ficha `04-ruido.md` queda sin contenido tras el filtro y
no se indexa. En `search`, cada línea muestra archivo y líneas, `status`, posición léxica y
similitud coseno. La paráfrasis de arriba casi no comparte palabras con `01-escucha.md`: el modo
vectorial e híbrido deberían encontrarla aunque el léxico no.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `src/vector_rag/` | Filtro de calidad, embeddings, índice híbrido, prompt, pipeline y JSONL |
| `tests/` | Pruebas herméticas con un embedder falso: no necesitan Ollama |
| `fixtures/evaluation-corpus/` | Escucha, presión, guion obsoleto, ficha contaminada y venta remota |
| `contracts/run-event.schema.json` | Contrato de cada evento exportado |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | Índice con texto y vectores, y trazas sanitizadas (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): embeddings, coseno y RRF explicados con dibujos.
2. [Inicio rápido](docs/humano/QUICKSTART.md): indexar y comparar los tres modos.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): filtro, coseno y RRF calculados paso a paso.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [06-naive-rag](../06-naive-rag/README.md), cuya búsqueda por palabras falla con paráfrasis.
**Sigue con:** [08-graph-rag](../08-graph-rag/README.md), para respuestas que exigen encadenar relaciones.

## Estado y límites

- **Implementado:** filtro de secciones, embeddings locales normalizados, coseno exacto, RRF
  ponderado, perfil durable del índice, publicación atómica, citas y JSONL sanitizado.
- **Aplazado:** reranker, LangChain, almacén vectorial externo y TurboVec.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

# Metodología y decisión

## Evidencia previa

- Volumen: 49 Markdown, 48 únicos y cientos de fragmentos; FTS5 tiene capacidad suficiente.
- Cinco paráfrasis de ventas no devolvieron los libros esperados en top-4 léxico.
- `qwen3-embedding:latest` local, a 1024 dimensiones en el spike, dio coseno 0.587 al pasaje
  pertinente y 0.0922 al distractor.
- Se verificaron contaminaciones temáticas en tres fichas de libros.

La conclusión no es “vector siempre es mejor”. Se adopta híbrido porque el corpus mezcla títulos y
términos exactos con preguntas semánticas; el filtro se adopta porque ningún recuperador corrige
datos incorrectos.

## Decisiones

- `qwen3-embedding:latest`, 768 dimensiones para la proyección durable.
- Instrucción solo para consultas; documentos sin instrucción, según Qwen3 Embedding.
- Vectores L2 normalizados y almacenados como `float32` en SQLite.
- FTS5 y vector sobre exactamente los mismos fragmentos filtrados.
- RRF ponderado con constante 60: 0.35 léxico y 0.65 vectorial; la coincidencia en ambos rankings
  sigue sumándose.
- Construcción completa temporal y reemplazo atómico.
- Sin LangChain, base vectorial externa, reranker ni dependencias runtime.

## Fuentes oficiales

- [Ollama embeddings](https://docs.ollama.com/capabilities/embeddings).
- [API `/api/embed`](https://docs.ollama.com/api/embed).
- [Qwen3 Embedding](https://github.com/QwenLM/Qwen3-Embedding).
- [SQLite FTS5](https://www.sqlite.org/fts5.html).

## Límites

El corpus sigue siendo mayoritariamente una biblioteca de fichas y algunos artículos, no el texto
completo de todos los libros. La recuperación semántica mejora acceso a lo existente; no convierte
metadatos en conocimiento detallado ni valida afirmaciones.

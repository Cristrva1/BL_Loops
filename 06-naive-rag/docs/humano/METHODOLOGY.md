# Metodología y decisiones

## Pregunta experimental

¿Cuánto aporta recuperar texto exacto antes de introducir embeddings? Para contestarla, esta
variante reduce las piezas al mínimo observable:

```text
Python estándar + SQLite FTS5 + API HTTP local de Ollama + citas
```

No se seleccionó un repositorio externo ni una librería RAG. La base propia permite aprender qué
hace cada paso antes de comparar LangChain, Flowise o una búsqueda vectorial.

## Corpus objetivo

El censo inicial de `docs/humano/Libros` encontró 49 archivos Markdown, aproximadamente 0.66 MiB,
repartidos entre ventas, ventas digitales, ventas inmobiliarias, persuasión y psicología o
neuromarketing. Algunos son fichas breves o metadatos y no capítulos completos. Una subcarpeta
también conserva PDF, pero esta variante solo importa Markdown para evitar OCR y contenido doble.

La carpeta de libros es una **entrada de importación**, no una dependencia del runtime. La
proyección durable vive en `.local/data/books.sqlite3` y puede reconstruirse desde otra carpeta al
copiar el laboratorio.

En la verificación local del 30 de agosto de 2026, la importación descubrió 49 Markdown, indexó 48
documentos únicos en 782 fragmentos y omitió una copia exacta de
`The_Honest_Real_Estate_Agent.md`. Estos conteos son un snapshot del corpus, no una constante del
código.

## Decisiones del corte

1. Dividir por encabezados y párrafos con un máximo configurable de caracteres.
2. Conservar ruta relativa y líneas para que cada fragmento sea verificable.
3. Omitir documentos exactamente duplicados mediante SHA-256.
4. Construir una base temporal y reemplazar la anterior solo al completar la importación.
5. Convertir la pregunta en términos FTS escapados; nunca insertar sintaxis del usuario.
6. Recuperar top-k con BM25, dando más peso al título y la sección.
7. No llamar a Ollama cuando FTS5 devuelve cero fragmentos.
8. Exigir citas `[S#]` y marcar, sin ocultar, cuando el modelo no las cumple.
9. Exportar eventos y métricas sanitizados para una comparación futura.

## Fuentes técnicas verificadas

- [SQLite FTS5](https://www.sqlite.org/fts5.html): tablas virtuales, tokenización, `MATCH` y BM25.
- [API de chat de Ollama](https://docs.ollama.com/api/chat): `POST /api/chat`, mensajes, respuesta
  final y métricas de tokens/duración.

También se verificó localmente que Python 3.12 ofrece FTS5 y que `qwen3.5:4b` está instalado en
Ollama. No se descargó ningún modelo adicional.

## Límites deliberados

- Una paráfrasis sin palabras compartidas puede no recuperar el texto relevante.
- No se indexan PDF, imágenes, tablas estructuradas ni enlaces remotos.
- No hay solapamiento semántico, reranker, memoria conversacional ni respuesta en streaming.
- Una cita válida señala un fragmento existente, pero no sustituye la revisión de fidelidad.
- La interfaz visual de este corte es la secuencia de nodos y estados en la terminal; un dashboard
  web y SSE pertenecen a una ampliación posterior.

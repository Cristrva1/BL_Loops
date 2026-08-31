# Metodología y decisiones

## Pregunta de arquitectura

¿La cantidad de información exige RAG? No. El corpus observado ocupa aproximadamente 0.66 MiB;
FTS5 puede buscarlo sin dificultad. La razón para añadir embeddings fue otra: las preguntas
naturales de ventas suelen expresar la intención con vocabulario distinto al de las fuentes.

En una prueba, la consulta “vender una vivienda sin presionar y construir una relación
duradera” hizo que la búsqueda lexical devolviera primero textos de neuromarketing, mientras
la vectorial e híbrida colocaron `Ninja_Selling.md` en primer lugar con similitud cercana a
0.68. Esa mejora concreta justificó crear primero `07-vector-rag` y reutilizar el método —no
su runtime— dentro de este agente autónomo.

## Método seguido

1. Inventariar tamaño, formatos, duplicados y estados.
2. Leer muestras relevantes y descubrir contaminación semántica.
3. Probar un embedding local antes de elegir arquitectura.
4. Construir recuperación híbrida con un filtro explícito y reemplazo atómico.
5. Escribir pruebas del contrato del agente antes de implementarlo.
6. Añadir una única herramienta local y un fallback gobernado por runtime.
7. Ejecutar fixture, corpus real, respuesta citada y validación JSONL.

## Fuentes técnicas

- [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling): contrato de llamada
  y mensaje con rol `tool`.
- [Ollama embeddings](https://docs.ollama.com/capabilities/embeddings): uso consistente del
  modelo y similitud coseno.
- [Ollama Embed API](https://docs.ollama.com/api/embed): batch, dimensiones y `truncate`.
- [Qwen3 Embedding](https://github.com/QwenLM/Qwen3-Embedding): instrucción para queries y
  documentos sin instrucción.
- [SQLite FTS5](https://www.sqlite.org/fts5.html): índice lexical y función BM25.

## Decisiones

- Python estándar en runtime: hace visible cada contrato HTTP, SQLite y JSONL.
- `qwen3.5:4b` decide y redacta; `qwen3-embedding:latest` recupera.
- FTS5 + barrido vectorial exacto + RRF: suficiente para cientos de fragmentos.
- Peso vectorial 0.65 y lexical 0.35: prioriza intención sin perder coincidencias exactas.
- Una herramienta por turno: permite estudiar agencia sin introducir bucles incontrolados.
- Fallback determinista: el modelo no puede saltarse la recuperación.
- Sin persistencia de conversación: evita confundir memoria del usuario con conocimiento.

## Límites verificados

El corpus no contiene el texto completo de la mayoría de los libros. Hay fichas con
descripciones editoriales; algunas solo conservan una línea útil. También se detectaron
contextos de Wikipedia claramente equivocados (por ejemplo, biografías o política sin relación
con el libro). El filtro evita indexar esas secciones, por lo que 25 de 49 archivos actuales no
aportan contenido sustantivo al índice.

Por tanto, este agente puede ser riguroso respecto a la biblioteca, pero todavía no es una
autoridad exhaustiva en ventas. El siguiente salto de calidad debería ser curar y enriquecer
fuentes permitidas, con procedencia y revisión, no añadir más orquestación ni una base vectorial
más pesada.


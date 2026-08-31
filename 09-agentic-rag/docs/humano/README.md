# Guía humana: agente local experto en ventas

## Objetivo

Aprender la diferencia entre un chat, un RAG y un agente. Aquí el modelo no recibe todos los
libros ni puede actuar fuera del equipo. Decide una consulta, llama una herramienta local
acotada, observa la evidencia y produce una respuesta citada.

El término “experto” describe su rol y método —ventas consultivas, éticas e inmobiliarias—,
no una garantía de que el corpus sea completo. Con las fuentes actuales puede sintetizar
principios presentes en descripciones editoriales; no puede reconstruir capítulos que no
existen en los Markdown.

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
2. Ejecuta una pregunta con `sales-agent ask` y localiza los cuatro nodos impresos.
3. Comprueba que la respuesta use `[S1]` y que debajo aparezcan archivo, líneas y estado.
4. Abre una conversación con `sales-agent chat`, consulta `/estado` y después `/limpiar`.
5. Valida la última corrida con `sales-agent-validate`.
6. Usa [EXERCISES.md](EXERCISES.md) y [EVALUATION.md](EVALUATION.md) para comparar resultados.

## Qué aprenderás

- Por qué 0.66 MiB de texto no exige una base vectorial por capacidad.
- Por qué una pregunta parafraseada sí puede justificar embeddings.
- Cómo el runtime, no el modelo, limita herramientas y efectos.
- Cómo la higiene del corpus puede importar más que el algoritmo de búsqueda.
- Cómo separar memoria conversacional, índice de conocimiento y observabilidad.


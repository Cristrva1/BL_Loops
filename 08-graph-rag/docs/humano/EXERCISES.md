# Ejercicios

## Básico

Indexa el fixture y busca la pregunta de Ana Ruiz en `graph` y `lexical`. Explica por qué el
documento `02-proyectos.md` aparece en la ruta y no en el ranking léxico.

## Intermedio

Consulta `¿Quién es responsable de AtlasCRM?`. Confirma que el hop se recorre en sentido inverso
y sigue etiquetado como `extracted`.

## Avanzado

Añade un triple nuevo en un documento temporal y reconstruye el índice. Comprueba que una pregunta
de tres saltos falla si `GRAPH_RAG_MAX_HOPS=2` y funciona otra vez con `3`. No edites el validador
para forzar el aprobado.

## Experimento

Formula tres preguntas: una de un salto, una de dos y una que no tenga semilla en el grafo.
Registra hops, documentos recuperados por FTS5 y si la respuesta se abstuvo. No evalúes la prosa
del modelo hasta ver primero la ruta.

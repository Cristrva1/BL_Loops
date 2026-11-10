# Ejercicios

Antes de empezar, indexa el corpus sintético (necesita Ollama con `qwen3-embedding:latest`):

```powershell
uv run vector-rag index --source .\fixtures\evaluation-corpus
```

Los ejercicios marcados **sin Ollama** se resuelven con los fragmentos de [EXAMPLES.md](EXAMPLES.md).
Cada uno tiene una solución plegada.

## Básico 1 — la misma frase en tres modos

Busca `necesidad real` en los tres modos:

```powershell
uv run vector-rag search --mode lexical "necesidad real"
uv run vector-rag search --mode vector "necesidad real"
uv run vector-rag search --mode hybrid "necesidad real"
```

Explica por qué el modo lexical puede fallar y el vector recuperar `01-escucha.md`.

<details>
<summary>Solución</summary>

Ningún fragmento contiene «necesidad» ni «real», así que el modo léxico no devuelve resultados. El
embedding de «necesidad real» queda cerca del de «escucha diagnóstica… contexto del comprador»
porque ambos hablan de entender qué necesita alguien. El modo híbrido hereda ese hallazgo del ranking
vectorial, aunque el léxico no aporte nada.
</details>

## Básico 2 — calcular un RRF (sin Ollama)

Un fragmento es 4.º en el ranking léxico y 2.º en el vectorial. Otro es 1.º en el vectorial y no
aparece en el léxico. ¿Cuál queda primero en el modo híbrido?

<details>
<summary>Solución</summary>

- Primero: `0.35 / 64 + 0.65 / 62 = 0.005469 + 0.010484 = 0.015953`.
- Segundo: `0.65 / 61 = 0.010656`.

Gana el primero: aparecer en los dos rankings compensa no ser el mejor en ninguno. Puedes comprobarlo
con la función `rrf()` del [ejemplo 3](EXAMPLES.md#ejemplo-3--fusión-rrf-paso-a-paso):
`rrf(4, 2)` y `rrf(None, 1)`.
</details>

## Intermedio — la sección contaminada

Consulta `quarterback` en los tres modos. Confirma que el contenido de `Contexto (Wikipedia)` fue
excluido y que el distractor no aparece por coincidencia léxica.

<details>
<summary>Solución</summary>

El modo léxico no devuelve nada: la única frase con «quarterback» vivía en una sección excluida y
nunca se indexó (el [ejemplo 1](EXAMPLES.md#ejemplo-1--el-filtro-de-calidad) muestra `bloques=0`
para `04-ruido.md`). Los modos vector e híbrido pueden devolver *algún* fragmento, porque siempre
existe un vecino más cercano, pero con un coseno bajo y sin hablar de fútbol. Un resultado vectorial
no garantiza relevancia: siempre hay que mirar la puntuación y el texto.
</details>

## Avanzado — perfil incompatible

Cambia temporalmente `VECTOR_RAG_EMBEDDING_DIMENSIONS` después de indexar. Comprueba que la consulta
falla por perfil incompatible; reconstruye y compara tamaño, latencia y ranking.

<details>
<summary>Solución</summary>

```powershell
$env:VECTOR_RAG_EMBEDDING_DIMENSIONS = "1024"
uv run vector-rag search --mode vector "necesidad real"
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag stats
uv run vector-rag search --mode vector "necesidad real"
Remove-Item Env:VECTOR_RAG_EMBEDDING_DIMENSIONS
uv run vector-rag index --source .\fixtures\evaluation-corpus
```

La primera búsqueda termina con `Operacion fallida: El indice no coincide con el perfil de embeddings
configurado.` Tras reconstruir, `stats` muestra `vectores de 1024d` y el archivo SQLite crece. El
ranking puede cambiar ligeramente. Al final se reconstruye con el perfil por defecto (768) para dejar
el laboratorio como estaba.
</details>

## Experimento — recall@5 léxico, vectorial e híbrido

Formula cinco pares de pregunta literal/paráfrasis sobre el corpus de libros. Registra recall@5 por
modo. No evalúes la calidad de la respuesta hasta comprobar primero que el fragmento esperado fue
recuperado.

<details>
<summary>Cómo organizarlo</summary>

1. Para cada par, decide **antes** de buscar qué archivo y líneas contienen la respuesta.
2. Ejecuta `search` en los tres modos y anota «sí» si ese fragmento está en el top-5.
3. Calcula recall@5 = aciertos / preguntas para cada modo, como en el
   [ejemplo 4](EXAMPLES.md#ejemplo-4--recallk-a-mano).

Resultado típico: el léxico acierta las literales y falla paráfrasis; el vectorial al revés con
nombres propios; el híbrido suele igualar o superar a ambos. Si no es así en tu corpus, esa es tu
evidencia: documenta los pesos usados y no cambies la conclusión para que «quede bonita».
</details>

## Autoevaluación

<details>
<summary>1. ¿Por qué no se suman directamente BM25 y coseno?</summary>

Porque están en escalas distintas (BM25 negativo y sin límite fijo; coseno entre −1 y 1). Sumarlos
daría más peso a quien tenga números más grandes. RRF usa solo posiciones.
</details>

<details>
<summary>2. ¿Qué problema resuelve el filtro de calidad que los vectores no resuelven?</summary>

La contaminación: si una ficha contiene texto ajeno (una sección de Wikipedia sobre otra cosa), un
buen recuperador lo encontrará *mejor*, no lo descartará. Solo una política explícita lo retira.
</details>

<details>
<summary>3. ¿Por qué el índice falla cerrado si cambia la dimensión?</summary>

Porque comparar vectores de perfiles distintos produce números sin sentido. Es preferible un error
claro a un ranking silenciosamente incorrecto.
</details>

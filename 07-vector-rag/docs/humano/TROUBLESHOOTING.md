# Diagnóstico

## Falta el modelo de embeddings

`ollama list` no muestra `qwen3-embedding:latest` y la indexación falla al pedir el primer vector.
Descárgalo solo si autorizas el peso adicional (`ollama pull qwen3-embedding:latest`). No sustituyas
el modelo por otro sin reconstruir el índice: el perfil quedaría distinto.

## El modo léxico no devuelve nada

Con paráfrasis es lo esperado: la pregunta no comparte palabras con el corpus. Compara con
`--mode vector`. Si **ningún** modo devuelve algo, el índice probablemente no existe: ejecuta
`uv run vector-rag stats`.

## Perfil incompatible

Modelo, dimensiones o instrucción cambiaron. El mensaje exacto es `El indice no coincide con el
perfil de embeddings configurado.` Restaura `.env` (o elimina la variable de proceso) o reconstruye
todo el índice; nunca mezcles vectores antiguos y nuevos.

## Timeout al indexar

El índice anterior queda intacto. Comprueba `ollama list`, reduce
`VECTOR_RAG_EMBEDDING_BATCH_SIZE` y vuelve a iniciar una reconstrucción completa. No se reintenta
automáticamente un batch ambiguo.

## Resultados semánticos extraños

Compara `lexical`, `vector` e `hybrid`. Abre las líneas citadas y revisa `source_status`. Un vector
cercano puede compartir tema sin responder la pregunta.

## Una ficha contaminada aparece

Identifica la sección exacta. Si pertenece a un patrón repetible, añade un filtro con fixture y
prueba; no hardcodees nombres de personas para maquillar un único resultado.

## Ollama o JSONL

```powershell
ollama list
uv run vector-rag stats
uv run vector-rag-validate
```

El endpoint debe ser HTTP local y el JSONL debe terminar en `run.completed` o `run.failed`.


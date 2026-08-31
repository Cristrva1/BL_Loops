# Arquitectura

## Corte vertical

El laboratorio implementa un agente single-shot por turno con memoria multi-turno opcional.
No hay framework de agentes, servidor web, cola, navegador ni conectores externos.

| Nodo | Entrada | Salida | Puede fallar por |
|---|---|---|---|
| `decide` | sistema, historial RAM, pregunta, schema de herramienta | una consulta o texto inválido | Ollama, timeout, contrato |
| `search_sales_library` | consulta normalizada | hasta `top_k` fragmentos | índice ausente/incompatible, embeddings |
| `ground` | fragmentos | JSON delimitado como `untrusted_evidence` | contrato interno |
| `answer` | conversación + resultado tool | respuesta con `[S#]` | Ollama, cita ausente |
| `run.completed` | métricas y conteos | JSONL terminal | escritura local |

## Autoridad del runtime

El modelo puede proponer la consulta, pero no ejecuta funciones. El runtime acepta únicamente:

```json
{
  "name": "search_sales_library",
  "arguments": {"query": "texto de 2 a 600 caracteres"}
}
```

Debe haber exactamente una llamada con ese nombre. Cero, dos, un nombre desconocido o
argumentos inválidos activan `runtime_fallback`, que usa la pregunta original. En ambos casos
se ejecuta una sola búsqueda. La segunda llamada al modelo ya no recibe herramientas.

## Recuperación

```text
consulta
  ├─ términos útiles ─ FTS5/BM25 ─ ranking lexical ─┐
  └─ instrucción query ─ embedding 768d ─ coseno ───┼─ RRF: 0.35 lexical + 0.65 vector
                                                    └─ top_k
```

Los documentos se embeben sin instrucción; la consulta lleva una instrucción de recuperación.
Los vectores se normalizan y guardan como `float32` en SQLite. Para 594 fragmentos, un barrido
local exacto es deliberadamente más sencillo que instalar una base vectorial especializada.

El índice guarda modelo, dimensión, perfil de instrucción, hash del corpus y versión de schema.
Una discrepancia falla cerrada y exige reindexar.

## Higiene y procedencia

Antes de fragmentar se excluyen por encabezado:

- `Contexto (Wikipedia)`;
- `Metadatos`;
- `Temas (Open Library)`;
- `Fuentes y Adquisición`.

También se omiten autor y pies de pipeline. Los estados `received`, `generated` y `unreviewed`
viajan hasta la salida. El filtro no certifica verdad: reduce ruido conocido.

## Memoria y persistencia

- Índice: persistente, privado de este laboratorio.
- Historial: hasta `SALES_AGENT_HISTORY_TURNS` pares, solo en RAM.
- Corrida: JSONL persistente con estados, duraciones, conteos y modelos, sin contenido crudo.
- Corpus: permanece en su ubicación fuente; el agente solo guarda su proyección.

## Seguridad

La URL se limita a HTTP loopback, los modelos `cloud` se rechazan y los paths de índice/runs
no pueden salir del laboratorio. El opener ignora proxies y rechaza redirecciones. Los textos
recuperados se etiquetan como no confiables para mitigar instrucciones incrustadas.


# ADR-0005 — pgvector para memoria semántica global

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema necesita almacenar embeddings vectoriales para la memoria semántica global (búsqueda por similitud). Se necesita una solución que conviva con PostgreSQL (donde ya vive el event store y los perfiles) para minimizar la complejidad operativa.

---

## Decisión

**Adoptamos pgvector** (extensión de PostgreSQL) para almacenar y consultar embeddings vectoriales en la tabla `semantic_memory`. No se agrega una base de datos vectorial separada (Pinecone, Qdrant, Weaviate, Chroma).

---

## Consecuencias positivas

- **Simplicidad operativa**: una sola base de datos (PostgreSQL) para todos los datos del sistema.
- **Transacciones ACID**: se pueden combinar operaciones sobre embeddings con operaciones relacionales en la misma transacción.
- **Sin integración adicional**: no hay que gestionar un servicio adicional, credenciales adicionales ni backups adicionales.
- **Suficiente para la escala inicial**: pgvector con índice `ivfflat` soporta millones de vectores con tiempos de búsqueda < 100ms.
- **SQL familiar**: los embeddings se consultan con SQL estándar + operadores vectoriales.
- **Metadatos ricos**: se puede filtrar por metadata JSONB junto con la búsqueda vectorial en una sola query.

---

## Consecuencias negativas

- **Escala limitada**: para billones de vectores o búsquedas en tiempo real a escala masiva, soluciones especializadas (Pinecone, Qdrant) serían más eficientes.
- **Índice aproximado**: `ivfflat` es ANN (Approximate Nearest Neighbor); `hnsw` (más preciso) tiene mayor costo de memoria.
- **Sin funciones avanzadas**: sin filtrado híbrido nativo, sin re-ranking automático, sin soporte multi-tenant vectorial nativo.

---

## Condición de reevaluación

Si en algún momento se cumplen todas estas condiciones:
1. La tabla `semantic_memory` supera 100M de filas.
2. La latencia de búsqueda supera el SLO de 300ms en p95.
3. El volumen de escrituras vectoriales supera 10K/hora.

En ese punto, se evalúa migrar a una base de datos vectorial dedicada con PostgreSQL como fuente de verdad.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Pinecone | Vendor lock-in; costo en producción; servicio adicional a operar |
| Qdrant | Servicio adicional; complejidad operativa extra en fases tempranas |
| Weaviate | Complejidad alta; curva de aprendizaje; overkill para el volumen inicial |
| Chroma (in-process) | No apto para producción distribuida; sin HA |
| Redis Vector Search | Requiere módulo RediSearch; ya se usa Redis para caché, agregar vectores mezcla responsabilidades |

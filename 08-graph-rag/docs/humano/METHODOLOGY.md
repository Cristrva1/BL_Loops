# Metodología y decisión

## Pregunta del laboratorio

¿Cuándo las relaciones explícitas justifican el costo de construir un grafo?

El caso `A-RAG-GRAPH-001` pide una dependencia indirecta repartida entre documentos. Un recuperador
de fragmentos puede devolver a Ana Ruiz y una fecha de congelación sin el eslabón AtlasCRM →
NortePay. El grafo hace visible ese eslabón.

## Decisiones

- Base propia en SQLite, como 06 y 07. Microsoft GraphRAG queda como referencia de investigación
  en modo mantenimiento, no como runtime.
- Triples visibles y deterministas. Extraer entidades con un LLM ocultaría el costo y rompería las
  pruebas herméticas.
- Aristas `inferred` solo en consulta: no se materializan en el índice.
- Comparación léxica interna. Una comparación puntuada contra el índice híbrido de 07 se hace
  exportando JSONL, no importando ese laboratorio.
- Sin Neo4j, MCP, CodeGraph ni dashboard en este corte.

## Fuentes

- [Caso A-RAG-GRAPH-001](../../../docs/CASOS_DE_EVALUACION.md).
- [Plan maestro, sección 8.8](../../../docs/PLAN_MAESTRO_DIDACTICO.md).
- [SQLite](https://www.sqlite.org/fts5.html).
- Clon local de Microsoft GraphRAG (`6dad6d2b0595`), consultado como referencia, no instalado.

## Límites

El grafo solo contiene lo que alguien escribió como triple. No descubre relaciones ocultas en la
prosa, no resume comunidades y no valida que una arista sea verdadera.

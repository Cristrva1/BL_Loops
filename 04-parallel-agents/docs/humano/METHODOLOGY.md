# Metodología y decisiones

## Pregunta educativa

¿Cuándo extraer tres documentos independientes en paralelo reduce el tiempo de pared sin perder hechos ni presentar un fallo como éxito?

El plan maestro lista LangGraphJS y CrewAI/AG2 como variantes futuras. Este corte es **A: FastAPI + asyncio + un modelo Ollama compartido**. Instalar un framework ahora ocultaría el semáforo, el timeout y la procedencia.

## Método aplicado

1. Fijar el caso `I-PARALLEL-002` y tres fixtures con hechos disjuntos.
2. Implementar primero la extracción secuencial con la misma lista de `fact_id`.
3. Añadir fan-out con `asyncio.to_thread` y `asyncio.wait_for`.
4. Unir con código: el agregador no llama al modelo.
5. Mostrar el grafo a partir de eventos SSE, no de una animación.
6. Exportar JSONL sanitizado e importarlo con el validador del propio laboratorio.

## Selección de componentes

No se eligió un repositorio de orquestación del menú portable. La base mínima es Python 3.12, FastAPI, Pydantic, React Flow y Ollama local.

| Pieza | Rol | Decisión |
|---|---|---|
| `asyncio.gather` | Runtime | El fan-out cabe en el lenguaje, sin framework |
| `qwen3.5:4b` | Modelo | Escalera básica del workspace; un solo peso compartido |
| FastAPI + SSE | Observabilidad | Las tres ramas deben verse en `queued` a la vez |
| React Flow | Grafo | El mismo lenguaje visual que la orquestación previa |
| Agregador determinista | Evaluación | Evita que el modelo invente la fila de una rama caída |

Al no reutilizar LangGraph ni CrewAI, no hay SHA de dependencia que registrar para esta variante. Esos frameworks quedan como hipótesis de la fase 2, no como código de este laboratorio.

## Fuentes vivas

- [API de chat de Ollama](https://docs.ollama.com/api/chat): historial, `stream`, `think` y métricas.
- [Caso I-PARALLEL-002](../../../docs/CASOS_DE_EVALUACION.md): tres fuentes, fan-out/fan-in y tiempos.
- Plan maestro, sección 8.4: trabajo paralelo con un modelo compartido.

Verificadas el 2 de septiembre de 2026.

## Progresión didáctica

- **Explicación:** mapa fuentes → serie → fan-out → unión.
- **Ejemplo:** caso `I-PARALLEL-002` en el dashboard.
- **Ejercicio:** bajar `PARALLEL_MAX_IN_FLIGHT` a 1 y ver desaparecer el overlap.
- **Experimento:** comparar `wall_ms` y `overlap_observed` de las dos ramas.
- **Evaluación:** tests deterministas, demo real y JSONL importable.

## Límites deliberados

- Un modelo a la vez; no hay multi-modelo en VRAM.
- Tres fuentes fijas; no hay planificador que decida el fan-out.
- Sin tools ni filesystem fuera de `examples/sources`.
- Sin frameworks de orquestación de terceros.
- Sin comparación todavía de los cuatro modelos iniciales.

Una capacidad posterior debe justificar qué permite aprender o medir.

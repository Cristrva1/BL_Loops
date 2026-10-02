# Metodología y decisiones

## Pregunta educativa

¿Qué diferencia medible aparece cuando una guía se produce con un agente único frente a un pipeline de tres roles con contratos de handoff?

El plan maestro lista LangGraph, CrewAI y AG2 como variantes futuras. Este corte es **A0: orquestador propio**. Instalar un framework ahora ocultaría el handoff, el gate y la línea base.

## Método aplicado

1. Fijar el caso `I-ORCH-001` y una lista de checks ejecutable por código.
2. Implementar primero el agente único con la misma entrada.
3. Añadir planificador, autor y revisor en secuencia, con un modelo compartido.
4. Permitir una sola corrección si el gate falla.
5. Mostrar el grafo a partir de eventos SSE, no de una animación.
6. Exportar JSONL sanitizado e importarlo con el validador del propio laboratorio.

## Selección de componentes

No se eligió un repositorio de orquestación del menú portable. La base mínima es Python 3.12, FastAPI, Pydantic, React Flow y Ollama local.

| Pieza | Rol | Decisión |
|---|---|---|
| Orquestador propio | Runtime | Transparente; cada nodo es una función |
| `qwen3.5:4b` | Modelo | Escalera básica del workspace para tutoriales |
| FastAPI + SSE | Observabilidad | La corrida dura lo suficiente para justificar eventos |
| React Flow | Grafo | El mismo lenguaje visual que la fábrica |
| Lista determinista | Evaluación | Evita que el modelo sea juez de su propia guía |

Al no reutilizar CrewAI, LangGraph ni AG2, no hay SHA de dependencia que registrar para esta variante. Esos frameworks quedan como hipótesis de la fase 2, no como código de este laboratorio.

## Fuentes vivas

- [API de chat de Ollama](https://docs.ollama.com/api/chat): historial, `stream`, `think` y métricas.
- [Caso I-ORCH-001](../../../docs/CASOS_DE_EVALUACION.md): plan, producción, revisión y línea base.
- Plan maestro, sección 8.3: orquestación multiagente y obligación de comparar contra agente único.

Verificadas el 2 de septiembre de 2026.

## Progresión didáctica

- **Explicación:** mapa tarea → dos variantes → gate.
- **Ejemplo:** caso `I-ORCH-001` en el dashboard.
- **Ejercicio:** desactivar una variante y observar el ganador `incomplete`.
- **Experimento:** comparar tokens y latencia de las dos ramas.
- **Evaluación:** tests deterministas, demo real y JSONL importable.

## Límites deliberados

- Un modelo a la vez; no hay fan-out paralelo.
- Una corrección, no un loop.
- Sin tools ni filesystem.
- Sin frameworks de orquestación de terceros.
- Sin comparación todavía de los cuatro modelos iniciales.

Una capacidad posterior debe justificar qué permite aprender o medir.

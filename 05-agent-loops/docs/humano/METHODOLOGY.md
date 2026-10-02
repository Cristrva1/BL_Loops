# Metodología y decisiones

## Pregunta educativa

¿Qué hace que un ciclo de mejora sea un loop de ingeniería y no un `while True` disfrazado?

El plan maestro lista LangGraph y OpenEvolve como variantes futuras. Este corte es **A0: loop Python tipado**. Instalar un framework ahora ocultaría el presupuesto, el score y la conservación del mejor candidato.

## Método aplicado

1. Fijar el caso `I-LOOP-003` y cinco assertions ejecutables por código.
2. Empezar con un prompt débil para que el score inicial sea visible.
3. Separar generador (modelo) y evaluador (código).
4. Reescribir el prompt solo si el umbral no se alcanzó y queda presupuesto.
5. Conservar el máximo score visto, no el último intento.
6. Mostrar el grafo a partir de eventos SSE y exportar JSONL sanitizado.

## Selección de componentes

No se eligió un runtime de `loop-engineering` ni OpenEvolve. La base mínima es Python 3.12, FastAPI, Pydantic, React Flow y Ollama local.

| Pieza | Rol | Decisión |
|---|---|---|
| Loop propio | Runtime | Transparente; cada nodo es una función |
| `qwen3.5:4b` | Modelo | Escalera básica del workspace para tutoriales |
| FastAPI + SSE | Observabilidad | La corrida dura lo suficiente para justificar eventos |
| React Flow | Grafo | El mismo lenguaje visual que los laboratorios previos |
| Lista determinista | Evaluación | Evita que el modelo sea juez de su propia salida |
| `loop-engineering` | Referencia | Criterios de diseño; SHA `1485cd64e9a8`; no es dependencia |

Al no reutilizar LangGraph ni OpenEvolve, no hay SHA de dependencia ejecutable. Esos proyectos quedan como hipótesis de la fase 3, no como código de este laboratorio.

## Fuentes vivas

- [API de chat de Ollama](https://docs.ollama.com/api/chat): historial, `stream`, `think` y métricas.
- [Caso I-LOOP-003](../../../docs/CASOS_DE_EVALUACION.md): score, presupuesto y parada.
- Plan maestro, sección 8.5: loops de agentes.
- Referencia de solo lectura `loop-engineering` en `C:/Users/criss/Desktop/Claude/Repositorios_Prueba/loop-engineering`, SHA `1485cd64e9a8`.

Verificadas el 2 de septiembre de 2026.

## Progresión didáctica

- **Explicación:** mapa generate → score → decide → improve.
- **Ejemplo:** caso `I-LOOP-003` en el dashboard.
- **Ejercicio:** partir de un prompt ya bueno y observar una sola iteración.
- **Experimento:** comparar tokens y número de vueltas entre un prompt débil y uno estructurado.
- **Evaluación:** tests deterministas, demo real y JSONL importable.

## Límites deliberados

- Un modelo a la vez; no hay fan-out paralelo.
- Sin tools ni filesystem.
- Sin frameworks de loops de terceros.
- Sin comparación todavía de los cuatro modelos iniciales.

Una capacidad posterior debe justificar qué permite aprender o medir.

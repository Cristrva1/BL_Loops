# Aprende a diseñar un loop que sabe parar

Este laboratorio responde una pregunta concreta: **¿cómo se diseña un ciclo que mejore resultados sin quedarse atrapado ni gastar recursos indefinidamente?**

Al terminar podrás explicar y ejecutar estos cinco pasos:

1. Se declara objetivo, score inicial, presupuesto y condición de parada.
2. Un prompt débil produce una salida.
3. Un evaluador en código cuenta cinco assertions estructurales.
4. Si no se alcanza el umbral, otro llamado reescribe el prompt.
5. Se conserva el mejor candidato, no necesariamente el último, y se explica por qué paró.

## Antes de empezar

- **Laboratorio previo:** [03-orchestration](../../../03-orchestration/docs/humano/README.md), donde
  ya viste un gate determinista y una única corrección. Aquí la corrección se convierte en un ciclo.
- **Software:** `uv`, Ollama con `qwen3.5:4b` y, para el dashboard, Node.js.
- **Vocabulario:** [loop](../../../docs/humano/maestro/GLOSARIO.md#loop),
  [presupuesto](../../../docs/humano/maestro/GLOSARIO.md#presupuesto),
  [maker/checker](../../../docs/humano/maestro/GLOSARIO.md#makerchecker) y
  [mejor candidato](../../../docs/humano/maestro/GLOSARIO.md#mejor-candidato).
- **Sin Ollama** puedes ver un loop completo con el modelo guionizado del
  [ejemplo 3](EXAMPLES.md#ejemplo-3--un-loop-completo-sin-gpu).

## Mapa visual

```mermaid
flowchart TB
    T[Tarea + prompt inicial] --> G[Generar]
    G --> S[Puntuar]
    S --> D{Umbral o presupuesto}
    D -->|continuar| I[Mejorar prompt]
    I --> G
    D -->|parar| B[Mejor candidato]
    S --> B
    B --> J[JSONL local]
```

## Cuatro conceptos

### Declaración

Un loop sin presupuesto es un `while True`. Antes de la primera llamada hay que poder decir qué se busca, cuánto se puede gastar y cuándo se deja de intentar.

### Maker / checker

El modelo escribe. El código puntúa. Si el mismo agente se pone la nota, el ciclo se felicita a sí mismo.

### Mejor candidato

La última iteración puede empeorar el score. El laboratorio guarda el máximo visto, no el intento más reciente.

### Presupuesto

Cinco iteraciones, dos errores o tres minutos. El primero que se agote gana. El motivo de salida queda en el snapshot y en el JSONL.

## Una analogía

Es como practicar un tiro libre con un entrenador que cuenta aciertos: tienes cinco intentos, un
tiempo límite y te quedas con **tu mejor serie**, no con la última. Si a la segunda serie ya metes
las cinco, paras. El entrenador no opina sobre el estilo: cuenta.

## Recorrido guiado

1. Sigue [QUICKSTART.md](QUICKSTART.md).
2. Ejecuta los [ejemplos 1 y 3](EXAMPLES.md) para ver las assertions y un loop completo sin GPU.
3. Carga el caso `I-LOOP-003` en el dashboard.
4. Observa el score inicial del prompt débil.
5. Mira si el mejor candidato coincide con la última iteración.
6. Valida el JSONL y continúa con [EXERCISES.md](EXERCISES.md).

## Qué no hace

- No usa LangGraph ni OpenEvolve.
- No instala el CLI de `loop-engineering`; solo toma criterios de diseño.
- No llama a APIs cloud ni tiene fallback pagado.
- No muestra el pensamiento privado del modelo.
- No conserva el prompt ni la salida completa dentro del JSONL.

La arquitectura exacta está en [ARCHITECTURE.md](ARCHITECTURE.md).

## Dónde encaja en la ruta

- **Antes:** [04-parallel-agents](../../../04-parallel-agents/docs/humano/README.md).
- **Después:** [06-naive-rag](../../../06-naive-rag/docs/humano/README.md), que abre la familia RAG:
  antes de generar, el sistema busca evidencia y la cita.

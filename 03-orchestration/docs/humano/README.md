# Aprende a orquestar sin perder la línea base

Este laboratorio responde una pregunta concreta: **¿qué mejora realmente al separar una tarea entre agentes especializados?**

Al terminar podrás explicar y ejecutar estos cinco pasos:

1. La misma tarea alimenta un agente único y un pipeline de tres roles.
2. El planificador entrega un JSON con secciones obligatorias.
3. El autor escribe Markdown a partir de ese plan.
4. Un revisor modelo opina, pero el aprobado lo decide una lista de checks en código.
5. El dashboard muestra nodos, handoffs, latencia y el JSONL sanitizado.

## Mapa visual

```mermaid
flowchart TB
    T[Tarea humana] --> B[Agente único]
    T --> P[Planificador]
    P --> A[Autor]
    A --> R[Revisor]
    R -->|gate falla| C[Una corrección]
    R -->|gate pasa| S[Comparación]
    C --> S
    B --> S
    S --> J[JSONL local]
```

## Cuatro conceptos

### Agente único

Un solo llamado al modelo produce toda la guía. Es la línea base. Sin ella, añadir roles solo añade teatro.

### Handoff

El plan no es un comentario: es un objeto JSON con título, audiencia, outline y checks. El autor no improvisa la estructura; la recibe.

### Gate determinista

El revisor puede devolver JSON. Si ese JSON es inválido, el experimento no se rinde: el código busca headings, Ollama, PowerShell, una condición de parada y la ausencia de marcas cloud.

### Una corrección

Si el gate falla, el autor recibe los checks rotos y reescribe una vez. Un ciclo con presupuesto de iteraciones pertenece al laboratorio de loops.

## Recorrido guiado

1. Sigue [QUICKSTART.md](QUICKSTART.md).
2. Carga el caso `I-ORCH-001` en el dashboard.
3. Observa cómo el nodo de agente único y el de planificador parten del mismo intake.
4. Compara los checks de las dos variantes.
5. Valida el JSONL y continúa con [EXERCISES.md](EXERCISES.md).

## Qué no hace

- No ejecuta agentes en paralelo.
- No usa LangGraph, CrewAI ni AG2.
- No llama a APIs cloud ni tiene fallback pagado.
- No muestra el pensamiento privado del modelo.
- No conserva el Markdown completo dentro del JSONL.

La arquitectura exacta está en [ARCHITECTURE.md](ARCHITECTURE.md).

# Metodología · Laboratorio 25 (`25-meeting-summarizer`)

Este documento explica las decisiones metodológicas detrás del procesamiento de transcripciones con modelos de lenguaje locales.

## 1. El problema de las reuniones sin registro

En los equipos de trabajo remotos, las videollamadas son frecuentes pero gran parte del valor se pierde si no se genera un registro inmediato. Los problemas habituales son:
- Nadie toma notas activas por estar participando en la conversación.
- Los compromisos quedan vagos (*"yo lo reviso luego"* sin fecha ni responsable explícito).
- Las grabaciones completas casi nunca se vuelven a escuchar debido a su duración (30 a 60 minutos).

## 2. Ventajas del enfoque con IA local

Frente a soluciones en la nube de terceros (Fireflies, tl;dv cloud, Otter, etc.), la IA local ofrece:
1. **Privacidad estricta**: Los temas comerciales, de nómina, código fuente o finanzas discutidos en llamada nunca se suben a servidores externos.
2. **Costo cero de inferencia**: No hay suscripciones mensuales por usuario ni límites de minutos.
3. **Control total del modelo**: Posibilidad de elegir entre modelos rápidos (`qwen3.5:4b`) o de mayor profundidad (`qwen3.5:9b`).

## 3. Principio de fidelidad factual (Cero Alucinaciones)

En minutas corporativas, una alucinación (inventar una fecha de entrega o un responsable erróneo) es inaceptable.
Para mitigar esto, la metodología aplica:
1. **System Prompt restringido**: Se prohíbe explícitamente al modelo asumir acuerdos que no aparezcan en la conversación.
2. **Temperatura baja (`0.2`)**: Reduce la aleatoriedad y prioriza la extracción determinista.
3. **Campo `context` y `rationale`**: Cada tarea y decisión debe incluir el motivo o contexto que la respalda en la conversación.
4. **Respuesta estructurada en JSON**: Evita dispersión de texto libre y obliga al LLM a clasificar en categorías fijas.

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

## 4. Privacidad de la evidencia

Una minuta contiene nombres, tareas y acuerdos. Por eso el laboratorio separa dos destinos:

| Destino | Contenido | Para qué |
|---|---|---|
| `.local/data/meetings.db` | Informe completo | Consultar y reutilizar la minuta en tu equipo |
| `.local/runs/*.jsonl` | Recuentos, modelo, duración y `report_sha256` | Comparar modelos sin exponer a nadie |

Antes del 2026-11-05 el JSONL incluía el informe completo; se retiró para cumplir la regla del
repositorio de trazas sanitizadas.

## 5. Ver antes de generar

`meeting-summarizer parse` muestra el formato detectado, los hablantes y el plan de bloques **sin**
llamar al modelo. Es la misma idea que `naive-rag search` en el laboratorio 06: comprobar primero qué
recibirá el modelo, para distinguir un fallo de entrada (el parser no reconoció a los hablantes) de un
fallo de generación (el modelo inventó un responsable).

## 6. Límites deliberados

- No transcribe audio ni se conecta a Meet, Zoom o Teams: parte de un texto ya exportado.
- No envía la minuta por correo ni mensajería; se copia a mano.
- La evaluación de calidad es manual, con la clave de `meet_compromisos_ambiguos.txt`.

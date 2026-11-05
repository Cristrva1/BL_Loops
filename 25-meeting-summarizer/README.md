# 25 · Resúmenes de videollamadas con IA local

> **Pregunta:** ¿cómo convertir una transcripción larga en decisiones y compromisos verificables sin
> que el modelo invente responsables ni fechas?
> **Nivel:** 4 · **Tiempo:** ~60 min · **Necesita Ollama:** solo `summarize` (`qwen3.5:9b` o `qwen3.5:4b`)

Aplicación local y visual que convierte transcripciones de Google Meet, Zoom (WebVTT), Microsoft
Teams o texto libre en: resumen ejecutivo, temas, decisiones, matriz de compromisos (responsable,
plazo y prioridad), preguntas abiertas y una minuta lista para compartir. Primero **normaliza** los
formatos con un parser determinista; después decide entre **una sola pasada** (hasta 3 200
palabras) o **map-reduce** con bloques solapados, y extrae con `temperature=0.2` y salida JSON.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\25-meeting-summarizer
uv sync --all-groups
uv run meeting-summarizer parse .\fixtures\zoom_standup.vtt                          # sin Ollama
uv run meeting-summarizer parse .\fixtures\meet_sprint_planning.txt --max-words 120   # ver map-reduce
uv run meeting-summarizer summarize .\fixtures\meet_compromisos_ambiguos.txt          # con Ollama
uv run meeting-summarizer list
```

Dashboard (dos terminales):

```powershell
uv run uvicorn meeting_summarizer.main:app --host 127.0.0.1 --port 8025 --reload
npm --prefix frontend install
npm --prefix frontend run dev        # abre http://127.0.0.1:5177
```

## Qué deberías ver

```text
Analisis local: Ollama no se invoca y no se guarda nada.
Archivo: zoom_standup.vtt
Formato detectado: zoom_vtt
Turnos: 7 | Palabras: 103 | Duracion: 49 s
...
Plan de analisis (limite 3200 palabras por bloque, solapamiento 250):
  single-pass: 1 bloque -> 1 llamada a Ollama
```

`parse` muestra exactamente qué recibiría el modelo: formato detectado, hablantes, turnos y el plan
de bloques. `summarize` recorre `parsed → chunking → analyzing → structuring → completed`, guarda el
informe en SQLite y exporta una traza JSONL **sin** nombres ni texto de la reunión.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/meeting_summarizer/` | Parser, troceador, prompts, cliente Ollama, motor, SQLite, API y CLI |
| `backend/tests/` | Pruebas deterministas: no necesitan Ollama |
| `fixtures/` | Cinco transcripciones sintéticas: Meet, Zoom VTT, Teams, compromisos ambiguos y notas sin hablantes |
| `frontend/` | Dashboard React + Vite con progreso SSE |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/data/meetings.db` y `.local/runs/` | Informes completos y trazas sanitizadas (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): objetivo, conceptos y recorrido.
2. [Inicio rápido](docs/humano/QUICKSTART.md): backend, dashboard y CLI.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): formatos, plan de bloques y privacidad de la traza.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** la familia RAG (06–09).
**Sigue con:** [13-sales-knowledge-curator](../13-sales-knowledge-curator/README.md), donde una persona
aprueba qué conocimiento se publica.

## Estado y límites

- **Implementado:** parser multi-formato, plan de bloques con solapamiento, single-pass y map-reduce,
  validación de endpoint y modelo locales, SQLite local, dashboard SSE, CLI `parse`/`summarize`/`list`
  y JSONL sanitizado.
- **No hace:** transcribir audio, unirse a reuniones, enviar correos ni mensajes, ni usar servicios
  cloud. La minuta se copia a mano.
- Usa transcripciones sintéticas o propias con consentimiento; las reuniones reales contienen datos
  personales.
- Reglas para futuras sesiones de agentes de código: [AGENTS.md](AGENTS.md).

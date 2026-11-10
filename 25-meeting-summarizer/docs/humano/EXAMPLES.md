# Ejemplos resueltos · Resúmenes de videollamadas

> Los ejemplos 1 a 5 se ejecutan **sin Ollama** y su salida es exactamente reproducible. El ejemplo 6
> depende del modelo: se muestra la forma esperada. Ejecuta todo desde `25-meeting-summarizer`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Zoom WebVTT | Normalizar marcas de tiempo y hablantes |
| 2 | Teams en dos líneas | Un formato distinto, el mismo contrato |
| 3 | Notas sin hablantes | El respaldo de texto plano |
| 4 | Forzar map-reduce | Bloques y solapamiento a escala pequeña |
| 5 | Configuración insegura | El endpoint debe ser local |
| 6 | Resumir con compromisos ambiguos | Lo que el modelo debe dejar «sin asignar» |

---

## Ejemplo 1 · Zoom WebVTT

```powershell
uv run meeting-summarizer parse .\fixtures\zoom_standup.vtt
```

```text
Analisis local: Ollama no se invoca y no se guarda nada.
Archivo: zoom_standup.vtt
Formato detectado: zoom_vtt
Turnos: 7 | Palabras: 103 | Duracion: 49 s
Participantes (2):
  - Elena Gómez: 4 turnos
  - Marcos Peña: 3 turnos
Primeros turnos normalizados:
  1. [00:00:02.000] Elena Gómez: Buen día equipo, standup rápido de 10 minutos. Empecemos por diseño.
  2. [00:00:08.000] Marcos Peña: Hola Elena. Terminé los prototipos del dashboard con tema oscuro y tabla interactiva de c…
  3. [00:00:16.000] Elena Gómez: ¿Pudiste validar los contrastes de color y la accesibilidad de los badges?
Plan de analisis (limite 3200 palabras por bloque, solapamiento 250):
  single-pass: 1 bloque -> 1 llamada a Ollama
```

**Qué observar:** el archivo WebVTT trae numeración de cues y flechas `00:00:02.000 --> 00:00:07.500`.
El parser descarta la numeración, conserva la marca de inicio y separa `Hablante: texto`. La duración
sale de la diferencia entre la primera y la última marca.

## Ejemplo 2 · Teams en dos líneas

```powershell
uv run meeting-summarizer parse .\fixtures\teams_architecture_sync.txt
```

```text
Formato detectado: teams
Turnos: 8 | Palabras: 147 | Duracion: 2 min 5 s
Participantes (2):
  - Andrés Morales: 3 turnos
  - Daniela Castro: 5 turnos
Primeros turnos normalizados:
  1. [00:10] Daniela Castro: Hola a todos. Hoy debemos definir la estrategia de partición de contexto para transcripci…
...
```

**Qué observar:** Teams escribe `Nombre  00:10` en una línea y el texto en la siguiente. Tras el
parser, ambos formatos producen la misma estructura (`turn_index`, `speaker`, `timestamp`, `text`): el
resto del sistema no necesita saber de dónde vino la transcripción.

## Ejemplo 3 · Notas sin hablantes

```powershell
uv run meeting-summarizer parse .\fixtures\notas_lluvia_de_ideas.txt
```

```text
Formato detectado: plain_text
Turnos: 5 | Palabras: 67 | Duracion: 1 min 0 s
Participantes (1):
  - Transcripción: 5 turnos
```

**Qué observar:** sin `Nombre:` ni marcas de tiempo, cada párrafo se convierte en un turno del
hablante genérico `Transcripción` y la duración se **estima** a 130 palabras por minuto (con un mínimo
de un minuto). En la minuta resultante ningún compromiso podrá tener un responsable fiable: el texto
nunca dice quién se compromete.

## Ejemplo 4 · Forzar map-reduce en una reunión corta

Las reuniones reales pasan a map-reduce a partir de 3 200 palabras. Para verlo con un fixture
pequeño, baja el límite solo en `parse` (el resumidor sigue usando 3 200):

```powershell
uv run meeting-summarizer parse .\fixtures\meet_sprint_planning.txt --max-words 120 --overlap-words 30
```

```text
Turnos: 13 | Palabras: 235 | Duracion: 2 min 50 s
...
Plan de analisis (limite 120 palabras por bloque, solapamiento 30):
  map-reduce: 2 bloques -> 2 resumenes parciales + 1 consolidacion
    Bloque 1/2: turnos 1-6, 129 palabras
    Bloque 2/2: turnos 6-13, 123 palabras
```

**Qué aprender:**

- Un bloque se cierra al **alcanzar** el límite, así que puede pasarlo un poco (129 > 120): nunca se
  corta un turno por la mitad.
- El turno 6 aparece en los dos bloques: es el **solapamiento**. Si un compromiso cae en el borde, al
  menos un bloque lo contiene completo.
- Map-reduce cuesta `n + 1` llamadas al modelo (aquí 3) frente a 1: más contexto total, más tiempo.

## Ejemplo 5 · Configuración insegura

```powershell
$env:OLLAMA_BASE_URL = "http://example.com:11434"
uv run meeting-summarizer parse .\fixtures\zoom_standup.vtt
uv run meeting-summarizer summarize .\fixtures\zoom_standup.vtt
Remove-Item Env:OLLAMA_BASE_URL
```

`parse` no usa la configuración de Ollama y sigue funcionando. `summarize` se detiene **antes** de
llamar a nadie, con código de salida `2`:

```text
Configuracion invalida: OLLAMA_BASE_URL debe ser HTTP local, por ejemplo http://127.0.0.1:11434.
```

Lo mismo ocurre con una etiqueta de modelo cloud:

```text
Configuracion invalida: OLLAMA_MODEL debe referirse a un modelo local, no cloud.
```

Ambas reglas están cubiertas por `backend/tests/test_config.py`. Las variables de proceso ganan al
`.env`, por eso `$env:` basta para el experimento y `Remove-Item` deja la terminal limpia.

## Ejemplo 6 · Resumir una reunión con compromisos ambiguos (necesita Ollama)

```powershell
uv run meeting-summarizer parse .\fixtures\meet_compromisos_ambiguos.txt
uv run meeting-summarizer summarize .\fixtures\meet_compromisos_ambiguos.txt --model qwen3.5:4b
```

La parte determinista:

```text
Formato detectado: meet
Turnos: 11 | Palabras: 135 | Duracion: 2 min 3 s
Participantes (3):
  - Lucía Ferrer: 6 turnos
  - Nora Salas: 3 turnos
  - Tomás Ibarra: 2 turnos
```

Lo que debería extraer una minuta **fiel** (compáralo con la salida de tu modelo):

| Elemento | Esperado | Trampa |
|---|---|---|
| Decisión | Publicar el boletín en Markdown dentro del repositorio | — |
| Idea **no** aprobada | Encuesta de satisfacción | No debe aparecer como decisión |
| Compromiso | Tomás corrige el tono de novedades, jueves 10:00 | — |
| Compromiso | Nora prepara la lista de destinatarios, viernes por la mañana | — |
| Compromiso ambiguo | Revisar enlaces rotos | «Alguien debería…»: responsable `Sin asignar` |
| Pregunta abierta | Quién avisa al equipo de diseño | No hay responsable ni plazo |

**Qué observar:** la forma de la salida es

```text
Procesando '<título>' con modelo qwen3.5:4b...
[ 25%] [#####               ] Formato: MEET · 135 palabras · 3 participantes.
...
COMPROMISOS / TAREAS:
  [<PRIORIDAD>] <responsable>: <tarea> (Plazo: <fecha o N/A>)
...
Minuta guardada en SQLite local. ID: <meeting_id>
```

y la traza de `.local/runs/` contiene solo recuentos (`action_items_count`, `decisions_count`…) y
`report_sha256`, nunca los nombres ni las tareas.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).

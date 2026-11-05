# Ejercicios prácticos · Laboratorio 25 (`25-meeting-summarizer`)

Todos los ejercicios usan transcripciones **sintéticas**. Si quieres probar una reunión propia, que
sea con el consentimiento de todas las personas y sin datos de clientes. Los marcados **sin Ollama**
solo usan `parse`. Cada uno tiene una solución plegada; los recorridos completos están en
[EXAMPLES.md](EXAMPLES.md).

---

## Básico 1 · Normalizar cuatro formatos (sin Ollama)

**Objetivo:** comprobar que formatos distintos producen la misma estructura.

1. Ejecuta `uv run meeting-summarizer parse` sobre `meet_sprint_planning.txt`, `zoom_standup.vtt`,
   `teams_architecture_sync.txt` y `notas_lluvia_de_ideas.txt`.
2. Anota para cada uno: formato detectado, turnos, palabras y participantes.

<details>
<summary>Solución</summary>

| Fixture | Formato | Turnos | Palabras | Participantes |
|---|---|---|---|---|
| `meet_sprint_planning.txt` | `meet` | 13 | 235 | 3 |
| `zoom_standup.vtt` | `zoom_vtt` | 7 | 103 | 2 |
| `teams_architecture_sync.txt` | `teams` | 8 | 147 | 2 |
| `notas_lluvia_de_ideas.txt` | `plain_text` | 5 | 67 | 1 (`Transcripción`) |

Las notas sin hablantes caen al respaldo de texto plano: el sistema no puede saber quién dijo qué y,
por tanto, ningún compromiso tendrá un responsable fiable.
</details>

---

## Básico 2 · Tu primera minuta (con Ollama)

**Objetivo:** generar una minuta completa y revisar la tabla de compromisos.

1. Ejecuta `uv run meeting-summarizer summarize .\fixtures\meet_sprint_planning.txt`.
2. Compara cada compromiso con la transcripción: ¿responsable y plazo aparecen literalmente?

<details>
<summary>Qué deberías encontrar</summary>

En la transcripción hay tres compromisos explícitos: Valeria crea los índices en SQLite y mide la
latencia antes del miércoles a las 3:00 PM; Roberto termina la suite de pruebas para el jueves al
mediodía; Carlos prepara la documentación para el viernes por la mañana. Y una decisión: CSS nativo
sin librerías de gráficos. Cualquier compromiso adicional o con otro plazo es una alucinación.
</details>

---

## Intermedio 1 · Compromisos ambiguos (con Ollama)

**Objetivo:** detectar lo que una minuta **no** debe inventar.

1. Ejecuta `parse` y después `summarize` sobre `meet_compromisos_ambiguos.txt`.
2. Busca en la salida la encuesta de satisfacción, los enlaces rotos y el aviso al equipo de diseño.

<details>
<summary>Solución</summary>

- La **encuesta** se discutió pero se dejó «para más adelante»: no puede figurar como decisión.
- «Alguien debería revisar los enlaces rotos» no tiene responsable: lo correcto es `Sin asignar` o
  una pregunta abierta, nunca un nombre elegido por el modelo.
- El **aviso a diseño** no tiene responsable ni plazo: es una pregunta abierta.
- Los compromisos válidos son el de Tomás (tono de novedades, jueves 10:00) y el de Nora (lista de
  destinatarios, viernes por la mañana).

La tabla del [ejemplo 6](EXAMPLES.md#ejemplo-6--resumir-una-reunión-con-compromisos-ambiguos-necesita-ollama)
sirve como clave de corrección.
</details>

---

## Intermedio 2 · Comparar modelos (`qwen3.5:4b` frente a `qwen3.5:9b`)

**Objetivo:** medir velocidad y fidelidad con la misma entrada.

1. Procesa `meet_compromisos_ambiguos.txt` con `--model qwen3.5:4b` y después con `--model qwen3.5:9b`.
2. Para cada modelo anota: tiempo total, compromisos extraídos, compromisos inventados y si la encuesta
   aparece como decisión.

<details>
<summary>Cómo concluir</summary>

Usa la clave del ejercicio anterior. Un modelo «gana» solo si es más fiel **y** suficientemente
rápido; una minuta más fluida con un responsable inventado es peor que una minuta seca y correcta.
Repite cada corrida al menos dos veces: la variación entre corridas también es un resultado.
</details>

---

## Avanzado · Ver y ajustar el plan map-reduce (sin Ollama)

**Objetivo:** entender el costo del troceado.

1. Ejecuta `parse .\fixtures\meet_sprint_planning.txt` con `--max-words 120 --overlap-words 30`,
   después con `--max-words 80 --overlap-words 30` y por último con `--max-words 120 --overlap-words 0`.
2. Anota número de bloques, turnos repetidos y llamadas al modelo que costaría cada plan.

<details>
<summary>Solución</summary>

| Límite / solapamiento | Bloques | Turnos repetidos | Llamadas al modelo |
|---|---|---|---|
| 120 / 30 | 2 (turnos 1-6 y 6-13) | el 6 | 3 |
| 80 / 30 | 4 (1-4, 4-7, 7-12 y 11-13) | 4, 7, 11 y 12 | 5 |
| 120 / 0 | 2 (turnos 1-6 y 7-13) | ninguno | 3 |

Al bajar el límite aparecen más bloques y más llamadas. Con solapamiento 0 los bloques no comparten
turnos: el mismo costo aquí, pero un compromiso que empieza en un turno y se confirma en el siguiente
(«Valeria, encárgate…» / «Entendido, lo agendo…») podría quedar partido entre dos resúmenes. El
resumidor real usa 3 200/250: las reuniones de este laboratorio siempre van en una sola pasada.
</details>

---

## Experimento · La traza no guarda la reunión

1. Tras un `summarize`, abre el JSONL más reciente de `.local/runs/`.
2. Busca en él el nombre de un participante.

<details>
<summary>Resultado esperado</summary>

No aparece: la traza solo contiene recuentos (`action_items_count`, `decisions_count`,
`participants_count`…), el modelo, la duración, `report_sha256` y `raw_content_stored: false`. El
informe completo está en `.local/data/meetings.db`. Así la traza puede compartirse con el comparador
sin exponer a nadie; lo verifica `backend/tests/test_run_log.py`.
</details>

## Autoevaluación

<details>
<summary>1. ¿Cuándo usa el resumidor map-reduce?</summary>

Cuando la reunión supera 3 200 palabras: se divide en bloques con 250 palabras de solapamiento, se
resume cada bloque y una última llamada consolida.
</details>

<details>
<summary>2. ¿Por qué la temperatura es 0.2?</summary>

Para que la extracción sea estable y literal. Una minuta no debe ser creativa: debe repetir lo que se
acordó.
</details>

<details>
<summary>3. ¿Qué diferencia hay entre una decisión y una idea discutida?</summary>

Una decisión se aprueba explícitamente en la reunión («decisión aprobada», «de acuerdo, haremos…»).
Una idea que se deja para más adelante no es una decisión, aunque se hable de ella.
</details>

# Ejercicios del repositorio maestro

Los ejercicios enseñan a orientarse, diseñar y verificar sin depender de una IA cloud ni modificar
repositorios de referencia. Cada uno tiene objetivo, actividad, criterio de aprobado y una
**solución plegada**: intenta resolverlo antes de abrirla.

## Nivel básico 1 — Clasificar archivos

### Objetivo

Distinguir documentación humana, decisión, runtime y estado generado.

### Actividad

Clasifica estas rutas:

```text
AGENTS.md
docs/PLAN_MAESTRO_DIDACTICO.md
docs/humano/sistema.md
01-prompt-agent-factory/backend/src/
01-prompt-agent-factory/docs/humano/ARCHITECTURE.md
01-prompt-agent-factory/.local/exports/
06-naive-rag/fixtures/evaluation-corpus/
```

### Aprobado

Puedes explicar por qué el runtime nunca debe importar ninguno de los documentos humanos.

<details>
<summary>Solución</summary>

| Ruta | Clasificación |
|---|---|
| `AGENTS.md` | Regla operativa |
| Plan maestro | Decisión transversal |
| `sistema.md` | Fuente humana primaria |
| `backend/src` | Runtime |
| Arquitectura del laboratorio | Enseñanza humana |
| `.local/exports` | Estado generado, ignorado por Git |
| `fixtures/evaluation-corpus` | Dato de prueba versionado (operativo, no enseñanza) |

El runtime no importa documentos humanos porque entonces cambiar una explicación podría cambiar el
comportamiento del programa, y copiar el laboratorio sin su manual lo rompería. La documentación
explica el runtime; el runtime no depende de la documentación.
</details>

## Nivel básico 2 — Leer una traza JSONL

### Objetivo

Entender qué guarda una corrida y qué no guarda.

### Actividad

Esta línea tiene la forma real de una traza del laboratorio 02 (abreviada y con valores
ilustrativos):

```json
{"schema_version": "1.0", "sequence": 5, "event_type": "model.completed", "lab_id": "02-single-agent", "payload": {"turn": 1, "response_chars": 187, "response_model": "gemma4:e4b"}, "metrics": {"wall_duration_ms": 2380.4, "ollama_duration_ms": 2311.0, "prompt_tokens": 96, "output_tokens": 52}}
```

Responde:

1. ¿Qué paso de la conversación representa?
2. ¿Puedes saber qué preguntó la persona?
3. ¿Por qué `wall_duration_ms` es mayor que `ollama_duration_ms`?

<details>
<summary>Solución</summary>

1. La respuesta del modelo al primer turno (`turn: 1`) ya terminó: es el evento `model.completed`.
2. No. La traza está **sanitizada**: guarda longitudes (`response_chars`), tokens y tiempos, nunca
   el texto. Así puede compartirse para comparar modelos sin exponer la conversación.
3. `wall_duration_ms` lo mide el cliente e incluye el viaje HTTP, la serialización y la espera;
   `ollama_duration_ms` lo informa el servidor y solo cubre su propio trabajo.
</details>

## Nivel intermedio 1 — Diseñar un laboratorio mínimo

### Objetivo

Convertir una pregunta educativa en una estructura pequeña.

### Actividad

Elige la pregunta:

> ¿Cuándo debe un agente detenerse sin llamar otra vez al modelo?

Escribe, sin implementar todavía:

1. Una entrada sintética.
2. Tres estados visibles.
3. Una condición de parada.
4. Un error intencional.
5. Una métrica.
6. Los archivos mínimos necesarios.
7. Los documentos humanos que actualizarías.

### Restricción

No puedes añadir una base de datos, un framework multiagente ni SSE salvo que justifiques qué
observación concreta permiten.

### Aprobado

Tu propuesta cabe en un corte vertical y separa claramente runtime y aprendizaje.

<details>
<summary>Una solución posible</summary>

1. **Entrada:** `{"task": "Resume este párrafo en 20 palabras", "text": "…"}` sintético.
2. **Estados:** `queued` → `running` → `done` | `blocked`.
3. **Parada:** si la entrada está vacía o supera 2 000 caracteres, el agente pasa a `blocked`
   **sin** llamar al modelo (como la abstención del laboratorio 06).
4. **Error intencional:** Ollama apagado → `failed` con diagnóstico, sin reintento.
5. **Métrica:** `model_calls` por corrida; el caso de parada debe registrar `0`.
6. **Archivos:** `pyproject.toml`, `src/<paquete>/cli.py`, `config.py`, `run_log.py`, un fixture
   en `examples/` y `tests/test_stop.py`. Nada de SQLite ni SSE: una CLI basta para observarlo.
7. **Documentos:** `README.md`, `AGENTS.md` y `docs/humano/` con `README`, `QUICKSTART`,
   `EXAMPLES`, `ARCHITECTURE`, `METHODOLOGY`, `EXERCISES`, `TROUBLESHOOTING` y `EVALUATION`.
</details>

## Nivel intermedio 2 — Planificar tu propia ruta

### Objetivo

Usar la [ruta de aprendizaje](RUTA_DE_APRENDIZAJE.md) para preparar una sesión de estudio.

### Actividad

Tienes dos horas y **no** puedes usar la GPU hoy. Elige laboratorios y comandos de la «Ruta sin
Ollama» que te permitan entender qué es un gate determinista y qué es un top-k.

<details>
<summary>Una solución posible</summary>

1. 01 (`factory-demo --all`, 20 min): contrato y preguntas guiadas.
2. 03, ejemplos de `score_guide()` en su `EXAMPLES.md` (30 min): un gate determinista que aprueba o
   rechaza siempre igual.
3. 05, ejemplos de `score_output()` (20 min): assertions y mejor candidato.
4. 06 (`naive-rag index` + `naive-rag search`, 30 min): qué fragmentos entran en el top-k y por qué
   aparecen el documento obsoleto y el distractor.
5. Checkpoints de los niveles 1 a 3 de la ruta (20 min).
</details>

## Nivel avanzado — Auditar independencia

### Objetivo

Demostrar que un laboratorio es copiable.

### Actividad

En una copia temporal fuera de BL_Loops:

1. Copia un único laboratorio.
2. Crea su `.env` desde `.env.example`.
3. Ejecuta `uv sync --all-groups`.
4. Ejecuta pruebas y demostración.
5. Comprueba que no busca rutas de otro laboratorio.
6. Registra qué artefactos genera dentro de su `.local`.

No realices esta prueba sobre una carpeta con cambios no preservados.

### Aprobado

La copia funciona sin importar código, bases o servicios de BL_Loops, excepto Ollama local y la
configuración que acabas de copiar.

<details>
<summary>Pistas para la comprobación</summary>

```powershell
$destino = Join-Path $env:TEMP "bl-loops-copia"
Copy-Item -Recurse -LiteralPath .\06-naive-rag -Destination $destino
Set-Location (Join-Path $destino "06-naive-rag")
Copy-Item -LiteralPath .env.example -Destination .env
uv sync --locked --all-groups
uv run pytest
uv run naive-rag index --source .\fixtures\evaluation-corpus
uv run naive-rag search "plazo vigente LUNA"
```

Busca referencias a otros laboratorios con
`rg -n "0[0-9]-|1[0-9]-|2[0-9]-" src tests` y revisa que cada coincidencia sea solo texto
explicativo, nunca una ruta que el programa abra.
</details>

## Experimento — `.venv` aislada frente a entorno compartido

### Hipótesis

Una `.venv` por laboratorio conserva reproducibilidad; una común introduce cambios cruzados.

### Diseño seguro

No contamines proyectos reales. Crea dos proyectos sintéticos temporales con dependencias
incompatibles, sincroniza cada uno en su `.venv` y compara:

- `sys.prefix`.
- Versiones instaladas.
- Lockfiles.
- Resultado después de actualizar solo uno.

### Reflexión

Responde:

1. ¿Qué ahorro ofrece la caché de `uv` aunque existan dos entornos?
2. ¿Qué evidencia perderías si ambos proyectos usaran una ruta absoluta común?
3. ¿Por qué un entorno compartido contradice la autonomía de BL_Loops?

<details>
<summary>Respuestas orientativas</summary>

1. Los paquetes ya descargados se reutilizan desde la caché global: el segundo `uv sync` es mucho
   más rápido y casi no usa red, aunque cada `.venv` esté separada.
2. Perderías la correspondencia entre `uv.lock` y lo instalado: el último `uv sync` sobrescribe el
   entorno del otro proyecto y ya no sabes con qué versiones corrió cada experimento.
3. Porque un laboratorio dejaría de poder copiarse solo: su comportamiento dependería de lo que otro
   proyecto instaló.
</details>

## Autoevaluación

Marca cada afirmación solo si puedes demostrarla:

- [ ] Sé qué documento tiene autoridad sobre una propuesta del corpus.
- [ ] Sé dónde debe vivir un tutorial y dónde un schema ejecutable.
- [ ] Sé preparar un laboratorio sin crear una `.venv` raíz.
- [ ] Sé explicar qué comparte el `.env` y qué no comparte.
- [ ] Sé qué estrategia de `.env` usa el laboratorio en el que trabajo.
- [ ] Sé leer una línea JSONL y decir qué contenido **no** guarda.
- [ ] Sé definir una verificación antes de implementar.

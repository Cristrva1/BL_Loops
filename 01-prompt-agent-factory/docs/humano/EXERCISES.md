# Ejercicios

> Documento didáctico; no se importa ni se lee durante la ejecución de la aplicación.

Cada ejercicio sigue el mismo patrón: objetivo, acción, evidencia de aprobado y una **solución
plegada**. Intenta resolverlo antes de abrirla. Los niveles básico e intermedio no requieren
modificar código. Si necesitas ver un recorrido completo primero, repasa
[EXAMPLES.md](EXAMPLES.md).

## Básico 1 · Encontrar los componentes

**Objetivo:** distinguir briefing y artefacto.

1. Carga el ejemplo de prompt en el dashboard.
2. Borra el contexto y analiza la intención.
3. Localiza la pregunta que aparece y lee su “por qué”.
4. Restaura el contexto y construye el borrador.
5. En el JSON, identifica `inputs`, `constraints`, `output_contract` y `stop_conditions`.

**Evidencia de aprobado:** puedes explicar en una frase por qué cada uno de esos cuatro campos no es
intercambiable.

<details>
<summary>Solución</summary>

- `inputs`: **qué datos** recibe el artefacto en tiempo de ejecución (por ejemplo
  `folder_inventory`). Son datos, no órdenes.
- `constraints`: **qué no puede hacer** nunca, aunque los datos lo pidan.
- `output_contract`: **qué forma** debe tener el resultado para poder verificarlo con código.
- `stop_conditions`: **cuándo termina**, incluido “falta información” o “no tengo permiso”.

Si mezclas `inputs` y `constraints`, un dato malicioso podría pasar por regla; si falta
`output_contract`, nadie puede comprobar el resultado sin leerlo a mano.
</details>

## Básico 2 · Completar un briefing incompleto

**Objetivo:** responder las preguntas guiadas hasta llegar al 100 %.

1. Copia el briefing incompleto a una carpeta ignorada por Git:

   ```powershell
   New-Item -ItemType Directory -Force .local | Out-Null
   Copy-Item .\examples\intakes\incomplete_agent_brief.json .\.local\mi_briefing.json
   ```

2. Ejecuta `uv run factory-demo --intake .local/mi_briefing.json` y anota las siete preguntas.
3. Rellena los campos que faltan con valores **sintéticos** y decide si el agente puede mover
   archivos o solo leerlos.
4. Repite el comando hasta que termine con `Exportado: .local/exports/agent_….json`.

**Evidencia de aprobado:** el agente exportado tiene una restricción explícita sobre mover o borrar
archivos y `tools_confirmed: true`.

<details>
<summary>Solución posible</summary>

```json
{
  "artifact_type": "agent",
  "idea": "Quiero un agente que me ayude a organizar mis archivos de la carpeta de descargas.",
  "title": "Organizador de descargas",
  "audience": "Persona que revisa el informe antes de mover nada a mano",
  "context": "El agente recibe un inventario sintético de nombres y tamaños; solo propone una organización.",
  "input_name": "downloads_inventory",
  "output_format": "markdown",
  "success_criteria": [
    "Agrupa los archivos por tipo y antigüedad",
    "Marca los posibles duplicados sin borrarlos"
  ],
  "constraints": [
    "Solo lectura: no mover, renombrar ni borrar archivos",
    "No acceder a rutas fuera del inventario recibido"
  ],
  "allowed_tools": ["local_file_reader"],
  "tools_confirmed": true,
  "requires_human_approval": true
}
```

La decisión importante es la primera restricción: el briefing original decía «organizar», que un
modelo podría interpretar como permiso para mover archivos.
</details>

## Intermedio · Diseñar un agente sin tools

**Objetivo:** comprender que una lista vacía también es una decisión de seguridad.

1. Elige `agent`.
2. Define un agente que clasifique texto ya incluido en la entrada.
3. Deja vacía la lista de tools, pero marca su confirmación.
4. Construye el `AgentSpec`.
5. Comprueba `permissions.default_effect`, `tools`, `memory` y `max_steps`.

**Evidencia de aprobado:** el agente tiene cero tools, red desactivada, memoria solo de corrida y
máximo cuatro pasos.

<details>
<summary>Solución</summary>

`examples/intakes/agent_ticket_triage.json` es una solución completa. Al construirlo
(`uv run factory-demo --intake agent_ticket_triage.json`) obtienes `tools = []`,
`permissions.default_effect = "deny"`, `runtime_network = false`,
`memory.retention = "run_only"` y `max_steps = 4`. El
[ejemplo 3](EXAMPLES.md#ejemplo-3--un-agente-sin-herramientas) muestra la salida.
</details>

## Avanzado · Añadir una regla al contrato

**Objetivo:** practicar una evolución controlada del schema.

Añade a `PromptSpec` un campo `language` limitado inicialmente a `es` o `en`.

1. Escribe primero una prueba que falle.
2. Modifica el contrato.
3. Decide si el campo es obligatorio u opcional y documenta por qué.
4. Actualiza la fábrica y la interfaz.
5. Regenera JSON Schema.
6. Ejecuta pruebas y build.

**Evidencia de aprobado:** no existen divergencias entre Pydantic, API, TypeScript, JSON Schema y
documentación.

<details>
<summary>Pistas y orden recomendado</summary>

1. Prueba en `backend/tests/test_contracts.py`: construir un `PromptSpec` con `language="fr"` debe
   lanzar `ValidationError`.
2. En `contracts.py`, un `Literal["es", "en"]` es suficiente para empezar. Si lo haces opcional con
   valor por defecto `"es"`, los artefactos antiguos siguen validando; si lo haces obligatorio,
   debes subir `schema_version` y explicar la migración.
3. `uv run factory-export-schemas` y revisa `git diff -- contracts/generated`.
4. Añade el campo a `frontend/src/types.ts` y al formulario.
5. `uv run pytest`, `uv run ruff check .` y `npm --prefix frontend run build`.

Recuerda que la huella cambia: dos artefactos idénticos salvo el idioma tienen `content_hash`
distinto.
</details>

## Experimento · Restricción vaga contra restricción verificable

Crea dos briefings idénticos excepto por una restricción:

- A: “Sé breve”.
- B: “Devuelve como máximo cinco hallazgos y una frase por hallazgo”.

En esta parte no juzgues respuestas de un LLM. Compara únicamente qué restricción puede convertirse
en una prueba automática. Conserva el caso para repetirlo con los cuatro modelos en la Parte 2.

<details>
<summary>Conclusión esperada</summary>

Solo B es verificable por código: contar hallazgos (`<= 5`) y frases por hallazgo es una función
determinista. “Breve” depende de quien lee. Cuando en la Parte 2 un modelo genere la respuesta, B
permitirá un gate como los de los laboratorios 03 y 05; A solo permitirá una opinión.
</details>

## Fallo intencional · Huella alterada

1. Construye un artefacto.
2. Copia el JSON.
3. Cambia el título sin recalcular `content_hash`.
4. Intenta exportarlo mediante `/api/v1/artifacts/export` en Swagger (`http://127.0.0.1:8011/docs`).

**Resultado esperado:** HTTP 422 con `content_hash_mismatch`. La lección es que validación e
integridad son controles diferentes. El [ejemplo 5](EXAMPLES.md#ejemplo-5--huella-alterada) muestra
el mismo fallo desde la consola.

## Autoevaluación

<details>
<summary>1. ¿Por qué la Parte 1 no usa un modelo?</summary>

Para que cada transformación sea visible, repetible y fácil de probar. Primero se fija el contrato;
después, en la Parte 2, el modelo propondrá contenido que ese contrato validará.
</details>

<details>
<summary>2. ¿Qué tres restricciones añade siempre la fábrica?</summary>

No inventar datos fuera de la entrada o las fuentes declaradas, declarar la incertidumbre en lugar
de adivinar y no realizar efectos externos ni revelar datos sensibles.
</details>

<details>
<summary>3. ¿Qué diferencia a un AgentSpec de un PromptSpec?</summary>

El `AgentSpec` añade modelo, objetivo, herramientas, memoria, permisos, presupuesto de pasos,
aprobación humana y una condición de parada por presupuesto (`step_budget_reached`).
</details>

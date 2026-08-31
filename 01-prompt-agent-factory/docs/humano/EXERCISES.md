# Ejercicios

> Documento didáctico; no se importa ni se lee durante la ejecución de la aplicación.

Cada ejercicio sigue el mismo patrón: objetivo, acción, evidencia y reflexión. No necesitas modificar archivos para el nivel básico.

## Básico · Encontrar los componentes

**Objetivo:** distinguir briefing y artefacto.

1. Carga el ejemplo de prompt.
2. Borra el contexto y analiza la intención.
3. Localiza la pregunta que aparece y lee su “por qué”.
4. Restaura el contexto y construye el borrador.
5. En el JSON, identifica `inputs`, `constraints`, `output_contract` y `stop_conditions`.

**Evidencia de aprobado:** puedes explicar en una frase por qué cada uno de esos cuatro campos no es intercambiable.

## Intermedio · Diseñar un agente sin tools

**Objetivo:** comprender que una lista vacía también es una decisión de seguridad.

1. Elige `agent`.
2. Define un agente que clasifique texto ya incluido en la entrada.
3. Deja vacía la lista de tools, pero marca su confirmación.
4. Construye el `AgentSpec`.
5. Comprueba `permissions.default_effect`, `tools`, `memory` y `max_steps`.

**Evidencia de aprobado:** el agente tiene cero tools, red desactivada, memoria solo de corrida y máximo cuatro pasos.

## Avanzado · Añadir una regla al contrato

**Objetivo:** practicar una evolución controlada del schema.

Añade a `PromptSpec` un campo `language` limitado inicialmente a `es` o `en`.

1. Escribe primero una prueba que falle.
2. Modifica el contrato.
3. Decide si el campo es obligatorio u opcional y documenta por qué.
4. Actualiza la fábrica y la interfaz.
5. Regenera JSON Schema.
6. Ejecuta pruebas y build.

**Evidencia de aprobado:** no existen divergencias entre Pydantic, API, TypeScript, JSON Schema y documentación.

## Experimento · Restricción vaga contra restricción verificable

Crea dos briefings idénticos excepto por una restricción:

- A: “Sé breve”.
- B: “Devuelve como máximo cinco hallazgos y una frase por hallazgo”.

En esta parte no juzgues respuestas de un LLM. Compara únicamente qué restricción puede convertirse en una prueba automática. Conserva el caso para repetirlo con los cuatro modelos en la Parte 2.

## Fallo intencional · Huella alterada

1. Construye un artefacto.
2. Copia el JSON.
3. Cambia el título sin recalcular `content_hash`.
4. Intenta exportarlo mediante `/api/v1/artifacts/export` en Swagger.

**Resultado esperado:** HTTP 422 con `content_hash_mismatch`. La lección es que validación e integridad son controles diferentes.

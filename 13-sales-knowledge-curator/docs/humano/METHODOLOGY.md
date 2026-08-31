# Metodología

## Pregunta educativa

¿Cómo se construye un paquete de conocimiento de ventas que una persona pueda auditar, revertir y negarse a publicar cuando la evidencia no alcanza?

## Decisiones de este corte

| Tipo | Decisión |
|---|---|
| Confirmada | Laboratorio autónomo, Ollama local, red apagada, exportar archivos. |
| Propuesta aplicada | Orquestador Python propio, roles visibles, dominio ficticio de vivienda. |
| Pendiente humano | Dominio real, allowlist web, jurisdicción, quién aprueba releases. |

Una propuesta de `Prompts/` o de un repositorio de `menu_portable` no se ejecutó como dependencia. `gpt-researcher` se usó como referencia de planner → investigadores → publisher, no como runtime.

## Fixtures primero

Antes del motor se escribieron:

- una fuente vigente
- una obsoleta
- dos fuentes competentes en conflicto
- una copia sindicada
- una inyección
- una fuente vacía
- derechos inciertos
- una afirmación de proveedor sin método
- una anécdota

Los schemas Pydantic rechazan `truth_score` y tipos inventados.

## Extracción

Los fixtures declaran bloques `CLAIM` con tipo, tema, población y fechas. El parser anota el localizador de líneas. Eso hace evaluable el corte sin un LLM. El extractor Ollama, si se activa después, debe devolver la misma forma o fracasar.

## Independencia

`origin_source_id` y el hash del texto deciden si hay una sola cadena de procedencia. La copia sindicada no convierte `supported_single_source` en `corroborated`.

## Publicación

1. Staging con manifiesto y hashes.
2. Gate técnico.
3. Aprobación humana del hash del candidato.
4. `os.replace` del puntero `current.json`.
5. El release anterior permanece para rollback.

## Lo que no se hizo

No se instaló Crawl4AI, MarkItDown, CrewAI, ArchiveBox ni Langfuse. No se tocó `09-agentic-rag`. No se recontó el corpus humano de `docs/humano/Ventas/` como si ya estuviera curado: este laboratorio trabaja con fixtures sintéticos.

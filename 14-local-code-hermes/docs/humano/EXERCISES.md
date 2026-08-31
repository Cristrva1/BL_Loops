# Ejercicios

## Básico — leer una corrida bloqueada

1. Ejecuta el preflight exploratorio.
2. Valida el JSONL.
3. Cuenta nodos `passed`, `warning` y `blocked`.
4. Explica por qué el terminal puede ser `run.blocked` aunque el programa haya funcionado bien.

**Aprobado:** distingues un bloqueo de prerrequisitos de un fallo interno.

## Intermedio — probar una frontera sin servicios

1. Copia el fixture con un identificador nuevo.
2. Ejecuta el verificador y observa que falla.
3. Cambia solo la condición que rechaza 100 % y añade `test_discount_above_100_is_rejected`.
4. Ejecuta de nuevo el verificador.

**Aprobado:** solo cambian `src/pricing.py` y `tests/test_pricing.py`, las cuatro pruebas pasan y 101 % sigue rechazado.

## Avanzado — diseñar evidencia comparable

Sin ejecutar agentes, redacta una ficha para una futura corrida que incluya:

- SHA exacto y estado del árbol;
- cliente y versión;
- modelo, digest, contexto configurado y efectivo;
- `ollama ps` y residencia GPU;
- conteos de truncación y HTTP 500;
- RAM, commit, pagefile y VRAM durante la corrida;
- evidencia separada de inferencia local y cero egress;
- permisos, tool calls, archivos cambiados y tests.

**Aprobado:** ninguna afirmación depende de suposiciones y sabes qué campos impiden comparar dos corridas.

## Experimento posterior — A/B de runtime

Solo después de completar la cohorte Ollama, diseña el mismo caso con LM Studio. Mantén modelo, cuantización, contexto, SHA y permisos; nunca cargues ambos runtimes simultáneamente. llama.cpp directo se usa primero para diagnóstico, no para mezclar resultados.

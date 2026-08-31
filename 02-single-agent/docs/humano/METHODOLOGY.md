# Metodología y decisiones

## Pregunta educativa

¿Cuál es la implementación más pequeña que demuestra una conversación coherente de varios turnos con un modelo local desde Windows 11?

La decisión explícita para este corte fue: **solo chat CLI con `gemma4:e4b`**. Por eso no se anticiparon tools, FastAPI, React, SSE, SQLite ni frameworks de agentes.

## Método aplicado

1. Separar la necesidad observable: escribir, enviar historial y mostrar respuesta.
2. Elegir una única ruta de ejecución local.
3. Proteger el límite de red antes de hacer la solicitud.
4. Conservar contexto solo durante la sesión.
5. Exportar estados y métricas sin conservar conversación cruda.
6. Probar configuración, contrato HTTP, memoria, errores y JSONL con dobles deterministas.
7. Ejecutar además una conversación real breve contra Ollama.

## Selección de componentes

No fue necesario seleccionar un repositorio externo del menú: Python 3.12 ya incluye JSON, HTTP, terminal y archivos. Añadir un SDK o framework no cambiaría la capacidad enseñada y sí ocultaría el contrato.

| Pieza | Rol | Decisión |
|---|---|---|
| Implementación propia | Runtime ejecutable | Base mínima y transparente en `02-single-agent/` |
| Python 3.12 | CLI y cliente HTTP | Biblioteca estándar, sin dependencia de runtime |
| Ollama local | Servidor de inferencia | Único endpoint permitido |
| `gemma4:e4b` | Modelo | Nombre pedido y confirmado en el catálogo oficial |
| pytest + Ruff | Desarrollo | Solo pruebas y lint; no participan en el chat |

Al no reutilizar un repositorio candidato, no existen remoto, SHA o licencia de una dependencia de código que registrar para esta variante. Ollama y el modelo son prerrequisitos locales, no código copiado dentro del laboratorio.

## Fuentes vivas verificadas

- [API oficial de chat de Ollama](https://docs.ollama.com/api/chat): endpoint, historial, respuesta, métricas y control de `stream`/`think`.
- [Catálogo oficial de Gemma 4](https://ollama.com/library/gemma4): existencia del tag `gemma4:e4b` y parámetros recomendados.
- [Errores de la API de Ollama](https://docs.ollama.com/api/errors): códigos HTTP y formato del campo `error`.

Estas fuentes se verificaron el 29 de agosto de 2026. Deben revisarse de nuevo si cambia la API o el modelo.

## Progresión didáctica

- **Explicación:** mapa humano → historial → Ollama → respuesta.
- **Ejemplo:** recordar un dato durante dos turnos.
- **Ejercicio:** cambiar idioma y comprobar contexto.
- **Experimento:** comparar primer turno frío con el segundo turno caliente.
- **Evaluación:** pruebas deterministas, chat real y JSONL importable.

## Límites deliberados

- Solo texto.
- Una conversación por proceso.
- Historial sin poda; las sesiones educativas deben ser breves.
- Sin persistencia, tools, RAG, autonomía o interfaz web.
- Sin comparación todavía contra los otros modelos iniciales.

Estos límites mantienen el objetivo comprensible. Una capacidad posterior debe justificar por separado su complejidad.

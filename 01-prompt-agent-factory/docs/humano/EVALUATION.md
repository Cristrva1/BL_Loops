# Evaluación de la Parte 1

> Documento didáctico y de verificación; las pruebas ejecutables viven en `backend/tests/`.

## Qué evaluamos ahora

Esta parte mide contratos y comportamiento determinista, no calidad de generación de un modelo. Los casos canónicos son:

- `F-PROMPT-001`: idea a `PromptSpec`.
- `F-AGENT-002`: `AgentSpec` seguro.
- `F-SKILL-003`: skill portable y auditable.

## Criterios de aprobado

### `F-PROMPT-001`

- Briefing incompleto produce preguntas explicadas.
- Briefing completo produce JSON válido.
- Incluye incertidumbre, fuentes, evaluación y parada.
- Prohíbe efectos externos.
- La huella coincide con el contenido.

### `F-AGENT-002`

- Tools confirmadas explícitamente, incluso si la lista está vacía.
- `default_effect` es `deny`.
- Red y escrituras externas están desactivadas.
- Memoria no conserva PII y dura una corrida.
- Existe presupuesto máximo de pasos y parada por falta de autoridad.

### `F-SKILL-003`

- Tiene disparadores observables.
- Separa instrucciones y recursos.
- Explica revelado progresivo.
- No convierte referencias en dependencias de runtime.

## Pruebas automáticas

```powershell
uv run pytest
uv run ruff check .
npm --prefix frontend run build
```

El aprobado técnico exige cero fallos. Un build verde no sustituye la revisión del recorrido humano.

## Revisión humana

Usa esta lista después de probar la pantalla:

- ¿Se entiende que la idea es dato y no instrucción?
- ¿Cada pregunta explica por qué existe?
- ¿El grafo coincide con el resultado real de la API?
- ¿El JSON permite localizar permisos y parada sin leer código?
- ¿La interfaz distingue claramente qué está implementado y qué está aplazado?
- ¿Una persona principiante puede completar el ejemplo sin conocer Pydantic?

## Métricas

Las nueve métricas globales tienen el mismo peso cuando aplican. En esta parte:

| Métrica | Cómo se observa |
|---|---|
| Éxito de tarea | Contrato construido y exportado |
| Calidad | Cobertura de campos y claridad humana |
| Fidelidad | Artefacto conserva intención, restricciones y fuentes |
| Uso de tools | Declaración segura; no ejecución |
| Latencia | Tiempo de API determinista |
| Tokens | No aplica porque no hay inferencia |
| Recursos | RAM del proceso y tamaño del artefacto |
| Estabilidad | Repeticiones sin fallos estructurales |
| Valoración humana | Lista anterior, escala 0–1 |

Los campos no aplicables se marcan como tales; no reciben cero porque eso distorsionaría la comparación.

## Exportación JSONL

`RunRecord` ya está definido y su JSON Schema se genera. La escritura formal de corridas JSONL se implementará junto con el calificador mínimo, después de integrar una ejecución real con Ollama. Hasta entonces no fabricaremos métricas de tokens o VRAM inexistentes.

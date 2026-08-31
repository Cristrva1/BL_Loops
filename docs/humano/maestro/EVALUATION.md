# Evaluación del repositorio maestro y de una sesión de trabajo

Este documento evalúa la calidad estructural y didáctica de BL_Loops. Los casos de rendimiento de agentes y el contrato común JSONL viven en [`docs/CASOS_DE_EVALUACION.md`](../../CASOS_DE_EVALUACION.md).

## Puertas obligatorias

Una entrega se rechaza si falla cualquiera de estas puertas aplicables:

| Puerta | Evidencia |
|---|---|
| Separación | El runtime no importa ni parsea `docs/humano/` |
| Autonomía | El laboratorio no importa código o estado de otro laboratorio |
| Seguridad | No hay secretos, PII, cloud fallback ni efectos no autorizados |
| Reproducibilidad | Dependencias y comandos están versionados y explicados |
| Veracidad visual | La UI representa estados reales del backend |
| Verificación | Se ejecutaron pruebas proporcionales al cambio |
| Documentación | La explicación humana corresponde al comportamiento actual |

## Rúbrica didáctica

Puntúa cada dimensión de 0 a 2:

| Dimensión | 0 | 1 | 2 |
|---|---|---|---|
| Claridad | No se entiende el objetivo | Se entiende con inferencias | Objetivo, límites y resultado son explícitos |
| Visualización | Decorativa o ausente | Parcial | Estados y relaciones reales son visibles |
| Progresión | Mezcla niveles | Tiene algunos pasos | Explicación, ejemplo, ejercicio, experimento y evaluación |
| Sencillez | Complejidad prematura | Alguna pieza sobrante | Cada componente tiene una razón educativa |
| Diagnóstico | Solo “funciona/no funciona” | Hay logs | Errores, causas y recuperación están explicados |
| Evidencia | Afirmaciones sin prueba | Prueba parcial | Tests, demo y artefactos reproducibles |

Resultado orientativo:

- `10–12`: listo para enseñar dentro del alcance declarado.
- `7–9`: funcional, pero necesita refuerzo didáctico.
- `0–6`: no debe declararse terminado.

Las puertas obligatorias prevalecen sobre la puntuación. Una entrega insegura no aprueba aunque sea visualmente excelente.

## Lista de cierre para Codex

- [ ] Leí el `AGENTS.md` aplicable.
- [ ] Revisé `git status` antes y después.
- [ ] Preservé archivos ajenos.
- [ ] Implementé únicamente el alcance pedido.
- [ ] Actualicé la documentación didáctica afectada.
- [ ] No creé dependencias entre laboratorios.
- [ ] No compartí una `.venv` entre proyectos.
- [ ] No mostré valores del `.env`.
- [ ] Ejecuté tests, lint, build o demostración según el tipo de cambio.
- [ ] Verifiqué enlaces locales si edité Markdown.
- [ ] Detuve servidores temporales.
- [ ] Separé en la entrega final lo terminado y lo aplazado.

## Prueba de independencia

Cuando un laboratorio alcance una versión enseñable:

1. Copiarlo a una ubicación temporal segura fuera de BL_Loops.
2. Crear su `.env` desde `.env.example`.
3. Sincronizar su propia `.venv`.
4. Ejecutar pruebas, build y demostración.
5. Confirmar que no resuelve rutas hacia otro laboratorio.
6. Exportar una corrida JSONL cuando esa capacidad aplique.

## Prueba de documentación

Una persona nueva debe poder responder usando solo los documentos:

- ¿Qué aprenderé?
- ¿Qué comando ejecuto primero?
- ¿Qué componentes participan?
- ¿Por qué se incluyó cada uno?
- ¿Qué está deliberadamente aplazado?
- ¿Cómo sé que el resultado es correcto?
- ¿Qué hago cuando falla?

Si necesita reconstruir estas respuestas desde el código, la documentación aún no cumple su función educativa.

## Evidencia de esta guía maestra

La guía se considera coherente cuando:

- Todos sus enlaces locales existen.
- `README.md`, `docs/INDEX.md`, el plan y `AGENTS.md` apuntan al mismo modelo de trabajo.
- La política de `.env`/`.venv` coincide con la implementación de los laboratorios.
- Los documentos humanos permanecen separados de los archivos operativos.

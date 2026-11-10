# Índice documental de BL_Loops

## Guía didáctica del repositorio maestro

- [Biblioteca humana](humano/README.md): separa intención, guía vigente y referencias recibidas.
- [Entrada y recorrido](humano/maestro/README.md): objetivo, mapa general y orden de aprendizaje.
- [Ruta de aprendizaje](humano/maestro/RUTA_DE_APRENDIZAJE.md): orden de los laboratorios, tiempos, checkpoints y ruta sin Ollama.
- [Glosario](humano/maestro/GLOSARIO.md): vocabulario común con ejemplo y laboratorio donde verlo.
- [Inicio rápido](humano/maestro/QUICKSTART.md): reconocimiento seguro del workspace, primer comando de cada laboratorio y mapa de puertos.
- [Arquitectura](humano/maestro/ARCHITECTURE.md): límites entre raíz, laboratorios, configuración y resultados.
- [Metodología](humano/maestro/METHODOLOGY.md): forma simple y progresiva de construir cada parte.
- [Flujo de futuras sesiones de Codex](humano/maestro/CODEX_WORKFLOW.md): apertura, implementación, verificación y cierre.
- [Configuración y entornos](humano/maestro/ENVIRONMENTS.md): `.env` compartido, `.venv` aisladas y cachés reutilizables.
- [Mapa de documentos](humano/maestro/DOCUMENT_MAP.md): autoridad, función y ciclo de actualización.
- [Ejercicios](humano/maestro/EXERCISES.md), [diagnóstico](humano/maestro/TROUBLESHOOTING.md) y [evaluación](humano/maestro/EVALUATION.md).

## Reglas y decisiones vigentes

- [Reglas operativas](../AGENTS.md): autoridad para futuras sesiones de agentes de código.
- [Plan maestro didáctico](PLAN_MAESTRO_DIDACTICO.md): alcance, arquitectura, laboratorios, combinaciones y fases.
- [Casos de evaluación](CASOS_DE_EVALUACION.md): suite genérica, métricas, protocolo y contrato JSONL.
- [Sistema original](humano/sistema.md): intención inicial del usuario.
- [Novedades](NOVEDADES.md): registro de cambios visibles para estudiantes y mantenedores.

## Aplicaciones y descubrimiento

- [Menú portable](../menu_portable/REPO_MENU.md): catálogo de repositorios y protocolo de selección.
- [Laboratorio 01: fábrica de prompts y agentes](../01-prompt-agent-factory/README.md): primera aplicación educativa y visual.
- [Laboratorio 02: agente único CLI](../02-single-agent/README.md): conversación mínima y local con `gemma4:e4b`.
- [Laboratorio 03: orquestación multiagente](../03-orchestration/README.md): planificador, autor y revisor
  frente a un agente único, grafo SSE y gate determinista del caso `I-ORCH-001`.
- [Laboratorio 04: agentes en paralelo](../04-parallel-agents/README.md): fan-out/fan-in de tres
  fuentes, tiempo secuencial frente a paralelo y agregador que no completa una rama fallida.
- [Laboratorio 05: loops acotados](../05-agent-loops/README.md): mejora un prompt hasta un umbral
  con score por iteración, presupuesto y el mejor candidato, no el último.
- [Laboratorio 06: RAG léxico sencillo](../06-naive-rag/README.md): importación Markdown,
  SQLite FTS5, Ollama local, citas por líneas y exportación JSONL.
- [Laboratorio 07: RAG vectorial híbrido](../07-vector-rag/README.md): FTS5, Qwen3 Embedding,
  RRF ponderado, filtro de secciones contaminadas y comparación de recuperación.
- [Laboratorio 08: Graph RAG](../08-graph-rag/README.md): triples visibles, grafo SQLite,
  rutas multi-hop, aristas extraídas frente a inferidas y contraste léxico.
- [Laboratorio 09: agente experto en ventas](../09-agentic-rag/README.md): tool calling local,
  una búsqueda híbrida por turno, memoria en RAM, citas y trazas sanitizadas.
- [Laboratorio 13: curador de conocimiento de ventas](../13-sales-knowledge-curator/README.md):
  auditoría local, afirmaciones trazables, conflictos y `KnowledgeRelease` versionado.
- [Laboratorio 14: Hermes local](../14-local-code-hermes/README.md): preflight, sandbox Docker sin red,
  una corrida controlada y JSONL solo bajo `.local/` para el benchmark Ollama 64k.
- [Laboratorio 22: estudio de video HyperFrames](../22-hyperframes-video-studio/README.md): director
  Ollama, composición HTML/GSAP con texto escapado, lint local antes del render, HyperFrames sin
  telemetría y fallback calibrado visible.
- [Laboratorio 23: estudio Remotion](../23-remotion-superpowers-studio/README.md): plan de escenas,
  cálculo de fotogramas y video programático con React y `@remotion/cli` (render verificado).
- [Laboratorio 24: estudio Open Generative AI](../24-open-generative-ai-studio/README.md): Prompt
  Studio, storyboard de cuatro planos validado contra un contrato y animatic MP4 con FFmpeg.
- [Laboratorio 25: resúmenes de videollamadas](../25-meeting-summarizer/README.md): transcripciones
  de Google Meet, Zoom y Teams, extracción de acuerdos, matriz de compromisos y minutas con IA local.

## Benchmark local-code aprobado

| Laboratorio | Cliente | Estado documental |
|---|---|---|
| [`14-local-code-hermes`](../14-local-code-hermes/README.md) | Hermes | Preflight y harness de una corrida; benchmark puntuado pendiente. |
| `15-local-code-opencode` | OpenCode | Planificado; todavía no es una aplicación disponible. |
| `16-local-code-claude` | Claude Code | Planificado; todavía no es una aplicación disponible. |

El contrato común está incorporado en el [plan maestro](PLAN_MAESTRO_DIDACTICO.md) y en los
[casos de evaluación](CASOS_DE_EVALUACION.md). Los laboratorios planificados no se enlazan hasta
que exista su entrada técnica para evitar enlaces muertos.

## Mundos simulados y audiovisual (planificados)

Aprobados en el plan 0.2.5. Todavía no hay carpetas ejecutables para estos IDs.

> **Conflicto de numeración pendiente de decisión.** Las carpetas existentes
> `22-hyperframes-video-studio` y `23-remotion-superpowers-studio` son estudios exploratorios que
> ocupan los números reservados abajo para `22-video-generation-studio` y `23-video-edit-studio`.
> Las preguntas planificadas siguen vigentes; su numeración definitiva requiere una decisión
> explícita del usuario.

| ID | Carpeta | Pregunta corta |
|---|---|---|
| 10 | `10-sales-deal-gym` | Trato con comprador, competidor y coach en un mercado simulado. |
| 17 | `17-store-ops-gym` | Tienda con stock, demanda, reorden y margen. |
| 18 | `18-campaign-gym` | Campaña de oleadas con presupuesto y veto de marca. |
| 19 | `19-image-generation-studio` | Brief a imagen local con director y crítico. |
| 20 | `20-image-edit-studio` | Editar una imagen existente sin regenerarla. |
| 21 | `21-voice-studio` | Transcribir y sintetizar un diálogo con voces de fixture. |
| 22 | `22-video-generation-studio` | Clip corto local; stills primero, video generativo después. |
| 23 | `23-video-edit-studio` | Cortar, subtitular y montar un reel. |

MCP ya no tiene laboratorio propio. El caso `I-MCP-006` sigue en la suite de evaluación.

## Corpus y referencias

- `../Prompts/`: 36 documentos para estudiar prompts, contexto, agentes, RAG, loops, MCP, observabilidad y seguridad.
- [IA local](humano/IA_Local.md): análisis de hardware recibido; sus datos temporales deben verificarse antes de instalar o decidir.
- [Prompt inicial viejo](humano/Prompt_Inicial_viejo.md): borrador histórico conservado sin cambios; no es fuente canónica para BL_Loops.
- Los demás archivos de `docs/humano/`, excepto `sistema.md` y la guía `maestro/`, son fuentes, referencias o propuestas previas. No son decisiones vinculantes salvo incorporación explícita al plan maestro.

## Estado

Estado al 2026-11-05: existen quince laboratorios ejecutables (01–09, 13, 14 y 22–25). Todos
incluyen `docs/humano/EXAMPLES.md` con ejemplos resueltos y pruebas que pasan en un clon limpio sin
Ollama. Solo `14-local-code-hermes` tiene un corte ejecutable del benchmark local-code; OpenCode y
Claude Code siguen planificados. Cada corrida y revisión debe registrar su SHA exacto. Todavía no
existe una comparación formal ni una recomendación entre clientes.

Este índice distingue reglas, decisiones, enseñanza y materiales de estudio. Cuando una decisión
cambie, primero se actualiza el plan maestro, después el laboratorio afectado y finalmente las
guías e índice correspondientes.

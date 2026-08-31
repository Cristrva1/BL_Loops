# Índice documental de BL_Loops

## Guía didáctica del repositorio maestro

- [Biblioteca humana](humano/README.md): separa intención, guía vigente y referencias recibidas.
- [Entrada y recorrido](humano/maestro/README.md): objetivo, mapa general y orden de aprendizaje.
- [Inicio rápido](humano/maestro/QUICKSTART.md): reconocimiento seguro del workspace y primer laboratorio.
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

## Aplicaciones y descubrimiento

- [Menú portable](../menu_portable/REPO_MENU.md): catálogo de repositorios y protocolo de selección.
- [Laboratorio 01: fábrica de prompts y agentes](../01-prompt-agent-factory/README.md): primera aplicación educativa y visual.
- [Laboratorio 02: agente único CLI](../02-single-agent/README.md): conversación mínima y local con `gemma4:e4b`.
- [Laboratorio 06: RAG léxico sencillo](../06-naive-rag/README.md): importación Markdown,
  SQLite FTS5, Ollama local, citas por líneas y exportación JSONL.
- [Laboratorio 07: RAG vectorial híbrido](../07-vector-rag/README.md): FTS5, Qwen3 Embedding,
  RRF ponderado, filtro de secciones contaminadas y comparación de recuperación.
- [Laboratorio 09: agente experto en ventas](../09-agentic-rag/README.md): tool calling local,
  una búsqueda híbrida por turno, memoria en RAM, citas y trazas sanitizadas.
- [Laboratorio 13: curador de conocimiento de ventas](../13-sales-knowledge-curator/README.md):
  auditoría local, afirmaciones trazables, conflictos y `KnowledgeRelease` versionado.
- [Laboratorio 14: Hermes local](../14-local-code-hermes/README.md): preflight, sandbox Docker sin red,
  una corrida controlada y JSONL solo bajo `.local/` para el benchmark Ollama 64k.

## Benchmark local-code aprobado

| Laboratorio | Cliente | Estado documental |
|---|---|---|
| [`14-local-code-hermes`](../14-local-code-hermes/README.md) | Hermes | Preflight y harness de una corrida; benchmark puntuado pendiente. |
| `15-local-code-opencode` | OpenCode | Planificado; todavía no es una aplicación disponible. |
| `16-local-code-claude` | Claude Code | Planificado; todavía no es una aplicación disponible. |

El contrato común está incorporado en el [plan maestro](PLAN_MAESTRO_DIDACTICO.md) y en los
[casos de evaluación](CASOS_DE_EVALUACION.md). Los laboratorios planificados no se enlazan hasta
que exista su entrada técnica para evitar enlaces muertos.

## Corpus y referencias

- `../Prompts/`: 36 documentos para estudiar prompts, contexto, agentes, RAG, loops, MCP, observabilidad y seguridad.
- [IA local](humano/IA_Local.md): análisis de hardware recibido; sus datos temporales deben verificarse antes de instalar o decidir.
- [Prompt inicial viejo](humano/Prompt_Inicial_viejo.md): borrador histórico conservado sin cambios; no es fuente canónica para BL_Loops.
- Los demás archivos de `docs/humano/`, excepto `sistema.md` y la guía `maestro/`, son fuentes, referencias o propuestas previas. No son decisiones vinculantes salvo incorporación explícita al plan maestro.

## Estado

Estado al 2026-08-30: solo `14-local-code-hermes` tiene un corte ejecutable de Hermes; OpenCode y
Claude Code siguen planificados. La rama `main` ya tiene un commit base; cada corrida y revisión
debe registrar su SHA exacto. Todavía no existe una comparación formal ni una recomendación entre
clientes.

Este índice distingue reglas, decisiones, enseñanza y materiales de estudio. Cuando una decisión
cambie, primero se actualiza el plan maestro, después el laboratorio afectado y finalmente las
guías e índice correspondientes.

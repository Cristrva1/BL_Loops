## Plan: Maqueta Web Multiagente 16N

Construir una maqueta web React + FastAPI con 16 agentes predefinidos, orquestados con patrón Blackboard y LangGraph, enfocada en tus flujos reales: clarificar ideas, generar prompts por modelo/plataforma, enriquecer con research, analizar conversaciones, mejorar prompts maestros y recomendar el mejor modelo. La maqueta inicial debe usar memoria simple persistida y contratos claros; no conviene meter GraphRAG/Neo4j/Zep en la primera entrega porque inflan complejidad sin resolver primero el flujo base.

**Hallazgos que gobiernan el plan**
- `docs/Petición/chat.md` contiene el problema original y los requisitos funcionales más valiosos, pero mezcla exploración con respuesta.
- `docs/Petición/chat_2.md` es el documento con mejor criterio arquitectónico: Blackboard + LangGraph + MCP + memoria separada por propósito.
- `docs/Petición/chat_consolidado.md` es ahora la fuente canónica consolidada; `chat3.md` y `Chat 4.md` quedan archivados como insumos.
- `docs/multiagent-framework.md` ya bajó la arquitectura a un MVP de 10 agentes, pero se quedó corto frente a tu requerimiento completo de aprendizaje de prompts, benchmark continuo y recomendación de modelos.
- El hueco principal en todos los chats es el modelo de datos: faltan contratos exactos para catálogo de modelos, historial de conversaciones, scoring de modelos, prompts maestros y memoria del chat principal.

**Agentes predefinidos de la maqueta**
1. `Architect_Orchestrator` — recibe la intención del usuario, decide flujo, activa subgrafo y aplica reglas globales.
2. `Workflow_Splitter` — divide la tarea en subtareas, dependencias y orden de ejecución.
3. `AI_Translator` — normaliza entrada/salida entre español neutro para usuario e inglés técnico interno cuando haga falta.
4. `Librarian_Memory` — guarda observaciones, ajustes, decisiones y notas del chat principal; conecta documentos internos y futuros conectores como Obsidian.
5. `Clarity_Agent` — reescribe ideas con máxima claridad, estructura y fidelidad al objetivo real.
6. `Research_Agent` — investiga y enriquece el tema con evidencia externa o interna.
7. `Prompt_Optimizer` — genera prompts especializados según modelo, versión, plataforma y contexto de uso.
8. `Model_Catalog_Agent` — resuelve catálogo de proveedor → versión → plataforma → pricing → capacidades → mejores prácticas.
9. `Conversation_Analysis_Agent` — analiza conversaciones completas y extrae comparativas, patrones y calidad de respuesta.
10. `Benchmark_Analyst` — cruza resultados de tus pruebas con benchmarks oficiales y métricas internas por tipo de tarea.
11. `Prompt_Learning_Agent` — aprende del resultado real del modelo y propone mejoras al prompt maestro sin sobreescribirlo automáticamente.
12. `Model_Recommender` — sugiere el mejor modelo pago y gratuito según tarea, restricciones y evidencia acumulada.
13. `MCP_Tool_Router` — abstrae herramientas y conectores; en maqueta puede operar con adaptadores simulados o limitados.
14. `Review_QA_Agent` — valida consistencia, huecos, contradicciones y calidad mínima de salida.
15. `Arbiter_Agent` — resuelve conflicto entre agentes o salidas incompatibles; escala al usuario si hace falta.
16. `Editor_Agent` — entrega salida final limpia, neutra, accionable y lista para copiar o guardar.

**Botones y flujos de usuario**
1. `Clarificar Idea`
   - Cadena recomendada: `Architect_Orchestrator` → `Librarian_Memory` → `Clarity_Agent` → `Review_QA_Agent` → `Editor_Agent`
2. `Crear Prompt`
   - Cadena recomendada: `Architect_Orchestrator` → `Model_Catalog_Agent` → `Prompt_Optimizer` → `Review_QA_Agent` → `Editor_Agent`
   - Requiere selector encadenado: proveedor → versión → plataforma → modalidad (`web`, `IDE`, `CLI`, `desktop app`, `ollama`) → pago/gratis
3. `Investigar y Enriquecer`
   - Cadena recomendada: `Architect_Orchestrator` → `Research_Agent` → `Librarian_Memory` → `Review_QA_Agent` → `Editor_Agent`
4. `Analizar Conversaciones`
   - Cadena recomendada: `Architect_Orchestrator` → `Conversation_Analysis_Agent` → `Benchmark_Analyst` → `Review_QA_Agent` → `Editor_Agent`
5. `Mejorar Prompt Maestro`
   - Cadena recomendada: `Architect_Orchestrator` → `Prompt_Learning_Agent` → `Model_Catalog_Agent` → `Review_QA_Agent` → `Editor_Agent`
6. `Recomendar Mejor Modelo`
   - Cadena recomendada: `Architect_Orchestrator` → `Model_Catalog_Agent` → `Benchmark_Analyst` → `Model_Recommender` → `Editor_Agent`

**Diseño de la maqueta**
1. Fase 1 — Consolidación documental
   - Consolidar `docs/Petición/chat3.md` y `docs/Petición/Chat 4.md` en una sola fuente viva.
   - Tomar `docs/Petición/chat.md` como fuente de requisitos y `docs/Petición/chat_2.md` como fuente de decisiones arquitectónicas.
   - Reposicionar `docs/multiagent-framework.md` como base del MVP y ampliarlo a 16 agentes.
2. Fase 2 — Modelo de datos y contratos
   - Definir `AgentState` del Blackboard con: `session_id`, `raw_input`, `normalized_brief`, `selected_flow`, `active_agents`, `agent_outputs`, `decisions_log`, `user_profile`, `prompt_master_refs`, `model_selection`, `conversation_artifacts`, `scorecards`, `recommended_models`, `final_output`.
   - Definir entidades persistentes mínimas: `SessionJournal`, `ProjectBrief`, `PromptMaster`, `ConversationEvaluation`, `ModelScorecard`, `ModelCatalogEntry`, `AgentRunLog`.
   - Exigir output estructurado por agente; no dejar handoffs narrativos libres.
3. Fase 3 — Orquestación y subgrafos
   - Crear un subgrafo por botón/flujo, todos supervisados por `Architect_Orchestrator`.
   - Añadir `Review_QA_Agent` y `Editor_Agent` como cierre obligatorio en cada flujo.
   - Ejecutar `Arbiter_Agent` solo cuando haya conflicto o baja confianza.
   - Mantener `MCP_Tool_Router` desacoplado para que la maqueta no dependa de 60 APIs reales.
4. Fase 4 — Memoria simple persistente
   - Persistir historial y decisiones del chat principal en almacenamiento local simple, preferentemente SQLite + archivos Markdown/JSON.
   - Registrar todas tus observaciones y peticiones como eventos recuperables por `Librarian_Memory`.
   - Guardar prompts maestros por combinación `modelo + versión + plataforma + modalidad + pricing`.
   - Guardar scorecards por tarea/categoría: escritura, programación, matemáticas, razonamiento, ideas, sistemas, investigación.
5. Fase 5 — Catálogo de modelos y selector inteligente
   - Construir catálogo de modelos orientado a datos, no hardcodeado en el frontend.
   - Cada entrada debe incluir: proveedor, versión, ventana de contexto, fortalezas, debilidades, disponibilidad, costo estimado, plataformas soportadas, mejores prácticas de prompting, fecha de vigencia.
   - Añadir bandera de confianza para distinguir datos confirmados frente a supuestos temporales.
6. Fase 6 — UI de maqueta
   - Diseñar una app web con tres zonas: captura/controles, estado del Blackboard/agentes y salida/historial.
   - Mostrar 16 agentes con estado `idle`, `queued`, `running`, `waiting`, `done`, `blocked`.
   - Hacer visible el selector del flujo de prompt y el analizador de conversaciones como herramientas de primera clase, no como extras escondidos.
   - Incluir historial de sesiones, scorecards por modelo y bitácora del chat principal.
7. Fase 7 — Aprendizaje controlado
   - El sistema puede sugerir cambios a prompts maestros, pero no debe autoaprobarlos.
   - Cada propuesta de mejora debe registrar: versión anterior, evidencia usada, motivo del cambio, impacto esperado y aprobación humana.
   - El score de un modelo debe separarse entre benchmarks externos y desempeño observado en tus tareas reales.
8. Fase 8 — Verificación y endurecimiento
   - Probar cada botón con entradas fijas y cadenas de agentes esperadas.
   - Verificar que la memoria recupere observaciones previas y no reescriba de forma destructiva tu intención original.
   - Probar el selector completo `proveedor → versión → plataforma → pricing`.
   - Probar el flujo `prompt maestro + salida real del modelo + mejora propuesta`.
   - Validar que el recomendador explique por qué sugiere un modelo pago y uno gratuito usando scorecards y benchmark.

**Arquitectura que conviene reutilizar**
- `docs/Petición/chat_2.md` — base técnica para Blackboard, LangGraph, MCP y memoria por capas.
- `docs/Petición/chat.md` — base funcional de botones, análisis conversacional y mejora continua.
- `docs/Petición/chat_consolidado.md` — fuente canónica del problema, decisiones y maqueta multiagente.
- `docs/Repos/summary_consolidado.md` — fuente canónica del stack de herramientas y shortlist tecnológica.
- `docs/multiagent-framework.md` — base para la app web React + FastAPI, layout de 3 paneles y activación automática de agentes.
- `docs/TALLER_MULTI_AGENTE_2026.md` — evidencia técnica para justificar por qué la memoria fuerte y GraphRAG van después de validar el flujo base.

**Archivos relevantes**
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\Petición\chat.md` — requisitos funcionales base.
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\Petición\chat_2.md` — decisiones arquitectónicas base.
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\Petición\chat_consolidado.md` — fuente canónica consolidada para producto y arquitectura.
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\Repos\summary_consolidado.md` — fuente canónica consolidada para selección de herramientas y stack.
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\multiagent-framework.md` — blueprint operativo base para la maqueta web.
- `c:\Users\criss\Desktop\Claude\Framework MultiAgentes\docs\TALLER_MULTI_AGENTE_2026.md` — referencia técnica para memoria, MCP, DSPy, observabilidad y seguridad.
- Nuevos módulos a crear en la implementación: backend de orquestación, catálogo de modelos, almacenamiento persistente simple, frontend de control y visualización del Blackboard.

**Verificación**
1. Ejecutar un caso por cada botón y confirmar secuencia de agentes, payloads y salida final.
2. Validar que el sistema conserve observaciones del usuario entre sesiones y las reinyecte solo cuando sean relevantes.
3. Confirmar que el análisis de conversaciones produzca scorecards persistentes por modelo y categoría.
4. Confirmar que el recomendador no use solo benchmark externo; debe cruzar evidencia interna y externa.
5. Probar el sistema sin llaves reales con modo mock y con al menos un proveedor real conectado.
6. Revisar que ninguna mejora de prompt maestro se publique sin evidencia y aprobación.

**Decisiones**
- Incluido: maqueta web React + FastAPI, 16 agentes predefinidos, memoria simple persistente, Blackboard central, selector de modelo/versión/plataforma, scorecards, prompts maestros y recomendador.
- Excluido del primer corte: Neo4j, GraphRAG, Zep/Mem0, Promptfoo CI completo, OAuth amplio, observabilidad avanzada tipo Phoenix, 60 APIs productivas.
- Regla de diseño: primero resolver el flujo y los contratos; después escalar memoria, tool use y observabilidad.
- Regla de producto: tu chat principal y tus observaciones deben tratarse como fuente prioritaria de verdad, no como contexto descartable.

**Further Considerations**
1. `Librarian_Memory` puede quedarse en almacenamiento local al inicio y dejar Obsidian como integración de fase 2; es la decisión correcta para no frenar la maqueta.
2. `Mejorar Prompt Maestro` debe existir como botón propio y no quedar enterrado dentro de `Analizar Conversaciones`, porque es un ciclo distinto de aprendizaje.
3. Si más adelante quieres abrir la puerta a 60 APIs reales, conviene hacerlo a través de `MCP_Tool_Router` y no incrustando lógica de proveedor dentro de cada agente.
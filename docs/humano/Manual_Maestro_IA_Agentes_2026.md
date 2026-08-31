# Manual Maestro de IA Aplicada 2026

### Software, hardware, virtualización, orquestación de agentes corporativos, RAG, automatización y laboratorios

**Autor del encargo:** Christian Trasviña Morales (Guadalajara, MX) — Century 21 Si-Now · ESDATA · Binarias Labs
**Fecha de corte de la investigación:** 17 de junio de 2026
**Alcance:** convertirte en operador *senior* de sistemas de IA, sin hardware monstruoso (a lo sumo correr Gemma 4 E4B en tu RTX 3080 Ti).

---

## 0. Cómo usar este manual

Este documento no es una lista de herramientas de moda; es un **marco de decisión**. Cada vez que veas un tema importante, lo presento en tres rutas, en este orden de prioridad —que es exactamente el que pediste:

1. **Ruta open-source / self-hosted (costo cero, control total).** Repositorios y software libre. Lo que un senior monta para entender y para no depender de nadie.
2. **Ruta costo-beneficio (free oficial + un poco de pago donde rinde).** Tiers gratuitos oficiales y suscripciones baratas donde aceleran de verdad.
3. **Ruta premium (la "mejor forma" absoluta).** Lo que harías si el presupuesto no fuera la restricción.

Convenciones:

- `[NO VERIFICADO]` marca cualquier dato que no pude confirmar con suficiente confianza. No inventé cifras, fechas, nombres ni benchmarks; cuando algo es estimación lo digo.
- Los **comandos y nombres técnicos** van en inglés (es lo correcto y lo portable).
- Las herramientas y modelos cambian semanalmente. Trata cualquier precio, límite de tier o número de versión como **perecedero**: el manual te enseña a pensar, no a memorizar tablas que caducan.

> **Regla cero del senior:** la arquitectura le gana a la herramienta. La pregunta nunca es "¿qué IDE está de moda?", sino "¿qué arquitectura minimiza riesgo, costo y fricción a largo plazo?".

---

## 1. La tesis central: deja de pensar en "un IDE" y piensa en un "sistema operativo de agentes"

En 2026 el paradigma ya no es *autocompletado dentro de un editor*. Es **delegar tareas completas a agentes** que leen repos, editan múltiples archivos, ejecutan comandos, corren pruebas, abren navegadores, crean ramas y PRs, y operan en paralelo y en segundo plano. Google lo llevó al extremo presentando Antigravity 2.0 con agentes paralelos construyendo el núcleo de un sistema operativo desde cero por menos de 1,000 USD en tokens; Codex ejecuta tareas de horas; Claude Code corre tareas programadas con `/loop` y controla escritorios remotos. La superficie (IDE, terminal, app) es lo de menos.

Lo que sí importa es diseñar tu **sistema operativo de IA** con estas ocho capas. Si dominas las ocho, eres senior; si solo dominas la primera, eres usuario.

| # | Capa | Qué incluye | Tu objetivo |
|---|------|-------------|-------------|
| 1 | **Superficie** | IDE (VS Code), CLI (Claude Code, Codex), app de escritorio (Cowork), navegador, GitHub, WhatsApp/Telegram/Slack | Elegir la superficie por tarea, no por costumbre |
| 2 | **Modelo** | Claude, GPT/Codex, Gemini, Grok, y modelos open vía Ollama (Gemma 4, Qwen) | Multi-modelo; nunca un solo proveedor como "cerebro" |
| 3 | **Herramientas** | Terminal, filesystem, Git, Docker, navegador, APIs, **MCP**, SQL, vector DB, grafo | Conectar capacidades con permisos mínimos |
| 4 | **Contexto** | `AGENTS.md`, `CLAUDE.md`, skills, docs del repo, embeddings, memoria | Poco, claro, actualizado, accionable, versionado en Git |
| 5 | **Ejecución** | Local, contenedor Docker, VM, VPS, GitHub Actions, cloud agent, serverless sandbox | Aislar el riesgo según la tarea |
| 6 | **Control humano** | Permisos, aprobaciones, worktrees, ramas, PRs, CI/CD, *human-in-the-loop* | Toda acción destructiva pasa por un humano |
| 7 | **Observabilidad** | Trazas, costo, latencia, errores, evaluaciones (Langfuse / OpenTelemetry) | Medir todo: token/tarea, latencia p95, accuracy, self-correction rate |
| 8 | **Seguridad** | Secretos aislados, sandbox, RBAC, auditoría de MCP/skills/plugins | Tratar todo agente como código no confiable hasta probar lo contrario |

El resto del manual es, en el fondo, profundizar en cada una de estas capas y darte las rutas (open-source → free → premium) para construirlas.

---

## 2. Estado real del ecosistema (junio 2026)

Antes de las recomendaciones, fija el mapa verificado. Esto es lo que existe **hoy**, con las correcciones a errores comunes que circulan en manuales más viejos.

### 2.1 Modelos frontier vigentes

| Laboratorio | Modelos vigentes (jun 2026) | Notas |
|-------------|------------------------------|-------|
| **Anthropic** | Claude **Opus 4.8**, Sonnet 4.6, Haiku 4.5 | Opus 4.8 llegó con *Dynamic Workflows* y *Fast Mode* más barato; los workflows escalan hasta ~1,000 subagentes |
| **OpenAI** | **GPT-5.5** y GPT-5.5 Pro (base reentrenada, abr 2026, "agentic-first"), GPT-5.4 / 5.4-mini | GPT-5.3-Codex y GPT-5.2 quedaron *deprecated* como modelos seleccionables en Codex |
| **Google DeepMind** | **Gemini 3 Pro**, Gemini 3.1 Pro, **Gemini 3.5 Flash** (I/O 2026) | 3.5 Flash apunta a velocidad para flujos agentic; Gemma 4 se construyó "a partir de la investigación de Gemini 3" |
| **xAI** | Grok 4, Grok 4.1 Fast; modelo de código `grok-code-fast-1` (*deprecated* may-2026, retiro ago-2026) | xAI itera muy rápido; el nombre "Grok Build / grok-build-0.1" de manuales previos es `[NO VERIFICADO]` como producto formal |

### 2.2 Correcciones a mitos que circulan

Manuales y posts viejos arrastran errores. Los corrijo de entrada porque construir sobre datos falsos te cuesta tiempo:

- **"Gemini 2.5 es la base de Antigravity"** → Falso hoy. Antigravity corre sobre **Gemini 3 Pro** (con soporte para Claude Sonnet 4.5 y modelos open de OpenAI).
- **"Antigravity 2.0 usó 93 subagentes"** → El número 93 es `[NO VERIFICADO]`. Lo confirmado: en I/O 2026 demostraron agentes en paralelo construyendo el núcleo de un OS por **menos de 1,000 USD** en tokens, y corriendo un clon de Doom encima.
- **"Windsurf se rebrandeó a Devin Desktop"** → Inexacto. **Cognition** (creadora de Devin) **adquirió Windsurf en julio 2025**; lo está integrando con Devin, pero Windsurf sigue como IDE. Dato curioso y revelador: el ex-CEO de Windsurf, Varun Mohan, se fue a Google y fue quien **presentó Antigravity 2.0** en I/O 2026.
- **"MCP/skills se comparten automáticamente entre todos los IDEs"** → Medio mito. La verdad matizada está en la §6: el *protocolo* es compartido, pero la *configuración* de cada cliente no lo es.
- **"Helicone es tu stack de observabilidad"** → Quedó obsoleto: **Helicone entró en modo mantenimiento el 3 de marzo de 2026**. Usa Langfuse (§17).
- **"Gemma 4 e4B" es confusión con Gemma 3n** → Falso. **Gemma 4 es real** (familia E2B/E4B/12B/26B-A4B/31B, lanzada ~junio 2026, Apache 2.0). Tu `gemma4:e4b` en Ollama es legítimo (§15).

### 2.3 Stack recomendado de un vistazo (sin hardware monstruoso)

Esta es la versión ejecutiva; cada fila se justifica en su capítulo.

| Capa | Recomendación práctica | Por qué |
|------|------------------------|---------|
| Sistema base diario | **Windows 11 Pro + WSL2 Ubuntu 24.04** *o* Ubuntu 24.04 LTS nativo | Windows te da Hyper-V + apps + drivers NVIDIA; Ubuntu te da ecosistema dev más limpio |
| IDE principal | **VS Code** | Máxima compatibilidad con Copilot, MCP, Docker, WSL, SSH, extensiones |
| Agente de código principal | **Claude Code (CLI) + Codex CLI** | Dos ejecutores/revisores independientes; Claude fuerte en razonamiento largo, Codex en ejecución autónoma larga |
| Agente cloud/paralelo | **Codex Web/App, Copilot cloud agent** | Issue-to-PR, tareas paralelas, CI en sandbox |
| Plataforma agent-first (si vives en Google) | **Antigravity** | Multi-agente nativo + Gemini 3 |
| Automatización no-code | **n8n (self-hosted)** | Webhooks, cron, WhatsApp/Gmail/CRM, AI Agent nodes, MCP Client |
| Orquestación programática | **LangGraph** *o* **OpenAI Agents SDK** | LangGraph para flujos durables con estado; Agents SDK para handoffs/guardrails/tracing sobre OpenAI |
| Observabilidad | **Langfuse (self-hosted)** | Trazas, prompts, datasets, evals, costo/latencia. MIT |
| RAG inicial | **Supabase/Postgres + pgvector** | SQL + vectores + auth + storage + RLS |
| RAG avanzado | **Qdrant + Neo4j GraphRAG** | Qdrant para vector/híbrido a escala; Neo4j para relaciones multi-hop |
| Local LLM | **Ollama + Gemma 4 E4B / Qwen2.5-Coder** | Privacidad, offline, edge. No para competir con frontier |
| Hosting | **Vercel (frontend/AI) + Railway o VPS (backend/persistente)** | Vercel con Active CPU; Railway/VPS para procesos vivos |
| VPS laboratorio | **4 vCPU / 8–16 GB RAM** | n8n + DBs + MCP + workers + Ollama ligero |

---

## 3. IDE vs CLI vs agentes cloud vs agentes de escritorio

### 3.1 Las cinco categorías (y cómo se asignan por nivel)

No elijas una; **asigna niveles** según profundidad y riesgo de la tarea.

| Categoría | Ejemplos | Mejor uso | Riesgo principal |
|-----------|----------|-----------|------------------|
| **IDE con IA** | VS Code + Copilot, Cursor, Gemini Code Assist | Autocompletar, editar archivo abierto, debugging asistido | Se queda pegado al archivo actual |
| **IDE en modo agente** | Copilot agent mode, Cursor, Windsurf/Cascade | Cambios multiarchivo, terminal, tests, refactors | Si no hay buenas instrucciones, toca de más |
| **CLI agent** | Claude Code, Codex CLI, Aider, Goose, OpenHands CLI | Repo completo, SSH, automatizar scripts, revisar diffs | Comandos peligrosos con permisos amplios |
| **Cloud coding agent** | Codex Web/App, Copilot cloud agent, Devin, OpenHands Cloud | Issue-to-PR, paralelo, CI en sandbox | Costo, fuga de código/secretos |
| **Desktop / cross-app agent** | Claude Cowork, OpenClaw, Hermes | Automatizar apps, archivos, navegador, mensajería | **Altísimo**: controla escritorio, shell, credenciales |

**Escalera profesional de uso:**

- **Nivel 1 — velocidad diaria:** Copilot/Cursor en VS Code para pair programming.
- **Nivel 2 — profundidad de repo:** Claude Code + Codex CLI para arquitectura, refactors grandes, debugging difícil.
- **Nivel 3 — paralelo con PR:** Codex Web / Copilot cloud para backlog, bugs, issues.
- **Nivel 4 — automatización corporativa:** n8n / LangGraph / Agents SDK.
- **Nivel 5 — experimentos cross-app:** Cowork / OpenClaw / Hermes **solo en VM aislada con permisos mínimos**.

### 3.2 Claude Code, Cowork, Claude Design y la app de chat

Anthropic tiene **tres superficies, tres trabajos**:

- **Chat (claude.ai / apps):** conversación, borradores, pensar. En 2026 sumó **Claude Design** (lienzo de diseño), gráficos interactivos inline, *Output Styles*, y comandos `/fork`, `/rewind`, `/recap`, `/btw`.
- **Claude Code (terminal + IDE):** el agente de programación. Pasó de "asistente en terminal" a **plataforma agentic por capas**. Sus primitivas (todas oficiales) son:
  - `CLAUDE.md` — la "constitución" del repo; se lee cada sesión.
  - **Skills** — un `SKILL.md` con *frontmatter* bajo `.claude/skills/<nombre>/`; se invocan con `/<nombre>` o de forma autónoma. Soporta skills anidadas (en subcarpetas) con nombres calificados por directorio cuando colisionan.
  - **Subagents** — agentes especializados (reviewer, tester, architect, security-auditor) a los que se delega; la *descripción* del subagente controla cuándo Claude lo invoca.
  - **Hooks** — comandos shell/HTTP/prompt que se disparan en puntos del ciclo de vida (antes de editar, después de editar, antes de ejecutar, al terminar). Sirven para control determinista: lint automático, bloqueo de secretos, snapshots, logging.
  - **Slash commands** — atajos a flujos.
  - **MCP servers** — conexión a herramientas/datos externos.
  - **Plugins** — empaquetan varias de las anteriores en una unidad instalable.
  - El mismo loop se expone vía **Claude Agent SDK** (Python/TS) para construir agentes propios.
  - Novedades 2026: `/loop` (tareas programadas tipo cron), **Computer Use** (control de escritorio remoto), **Voice Mode**, control remoto desde móvil, agentes en segundo plano, *Auto Mode*, `/ultrareview`, *Ultrathink*, *Routines*.
- **Cowork (escritorio):** arquitectura agentic similar a Claude Code pero sin terminal, pensada para no-devs y operaciones. Organiza archivos, corre **tareas programadas** (mientras la app esté abierta y la máquina despierta), se conecta a apps vía **connectors** (Gmail, Notion, Calendar, Figma) y soporta los mismos **plugins/skills/subagents/memoria**.

**Criterio:** para código serio, **Claude Code** con Git + worktrees + hooks + tests. Para flujos de oficina/escritorio, **Cowork**, pero idealmente bajo un usuario aislado. Christian: Cowork encaja con tus flujos de Si-Now (agendado por WhatsApp, follow-up, consulta de inventario) si lo combinas con connectors y un par de skills propias.

### 3.3 OpenAI Codex

Codex es hoy el **sistema agentic unificado** de OpenAI: una sola cuenta y un solo modelo base detrás de múltiples superficies — CLI en terminal, extensión de IDE, delegación cloud vía ChatGPT, bot de GitHub, *computer-use* por lectura de pantalla, y **app de escritorio** (macOS feb-2026, Windows mar-2026). Corre sobre **GPT-5.5** (base reentrenada agentic-first). Cifras: ~4 millones de desarrolladores semanales (abr 2026).

- **Codex CLI** (open source, en Rust): agente local que lee/edita/ejecuta dentro del directorio seleccionado; lee `AGENTS.md`; soporta MCP nativo (config por servidor, OAuth para HTTP streamable); modos de sandbox; búsqueda en historial local.
- **Codex App/Web:** centro de comando para gestionar varios agentes en paralelo y tareas largas; **Automations** con triggers cloud para correr en segundo plano aunque tu PC esté apagada.
- **Codex Security** (mar 2026): agente de seguridad de aplicaciones que detecta y corrige vulnerabilidades.
- **Limitación clave:** Codex está acoplado a modelos GPT. **No es model-agnostic**. Para eso, usa Claude Code, Cline o agentes open. (Dato útil: **Amazon Bedrock** ya cataloga GPT-5.5, así que puedes consumirlo por ahí también.)

**Criterio:** **Claude Code + Codex CLI** es el par más potente para un solo operador. No los pongas a competir; úsalos como **dos revisores independientes**: das la misma tarea a ambos, comparas diffs, y el que aluciné menos gana esa ronda.

### 3.4 GitHub Copilot y "Agent HQ"

Copilot vive en dos mundos:

1. **Agent mode en IDE** (GA en VS Code y JetBrains): edita archivos, ejecuta comandos, colabora en tiempo real; algunos comandos de terminal piden aprobación.
2. **Cloud coding agent:** le asignas issues/tareas en GitHub; corre en **GitHub Actions**, analiza el repo, hace plan → rama → cambios → **PR**.

GitHub se mueve hacia un **"Agent HQ"** donde Copilot, Claude, Codex y agentes custom conviven dentro de GitHub/VS Code. Úsalo así: Copilot IDE para velocidad diaria, Copilot cloud para backlog/bugs, Claude/Codex para lo profundo.

### 3.5 Google Antigravity (y el fin de Gemini CLI)

**Antigravity** es la apuesta agent-first de Google. Original lanzado **noviembre 2025** (IDE forkeado de VS Code, con *Editor View* + *Manager Surface* para orquestar agentes asíncronos + *Artifacts* para verificar + *Knowledge Base*). En **I/O 2026 (19 may)** llegó **Antigravity 2.0**: ya no es solo un IDE, es una plataforma de cinco superficies — **app de escritorio, CLI, SDK, Managed Agents en la Gemini API, y Gemini Enterprise Agent Platform**. La app corre subagentes dinámicos en paralelo, agenda tareas en segundo plano y acepta comandos de voz; se integra con AI Studio, Firebase y Android.

**Transición forzada que debes anotar:** el acceso de consumidor a **Gemini CLI y a las extensiones de Gemini Code Assist en IDE termina el 18 de junio de 2026** para los tiers AI Pro, AI Ultra y gratuito. Empresas con licencia Gemini Code Assist Standard/Enterprise lo conservan. Plan: AI Ultra arranca en **100 USD/mes** (5× el límite del plan Pro en Antigravity).

**Criterio:** si vives en Google Cloud / Vertex / Workspace / Android → Antigravity + Gemini ADK tienen sentido. Si quieres independencia de proveedor, **no pongas todo sobre la superficie de Google**: esta transición (Gemini CLI → Antigravity) es la prueba de que las superficies cambian rápido. Mantén tu abstracción en **MCP + AGENTS.md portables**.

### 3.6 Cursor, Windsurf / Cognition / Devin, y Grok Code

- **Cursor:** sigue siendo el IDE-IA de referencia para muchos (líder de mercado por ARR). En 2026 sumó CLI con *cloud handoff*, evaluación de agentes en paralelo y sesiones lado a lado.
- **Windsurf (Cognition):** **Cognition** —creadora de **Devin**, el "primer ingeniero de software AI" autónomo— adquirió Windsurf en julio 2025. Hoy integran Devin dentro del IDE de Windsurf; posicionamiento "rápido y bien financiado" a **15 USD/mes** vs los 20 de Cursor, con sesiones multi-agente. Devin tiene sentido si tienes presupuesto, tareas de ingeniería repetibles, buena suite de tests y quieres PRs en paralelo — nunca como "cerebro central" sin CI y revisión humana.
- **xAI Grok Code:** `grok-code-fast-1` (ago 2025) es un modelo de código rápido y barato, construido desde cero, disponible vía Copilot/Cursor/Cline/etc. Quedó *deprecated* en may-2026 (retiro ago-2026), con una variante multimodal con uso de herramientas en paralelo en entrenamiento. Úsalo como **proveedor adicional** en un sistema multi-modelo, no como dependencia única.

---

## 4. Agentes autónomos de propósito general

Aquí entran las herramientas que ejecutan acciones reales en tu vida digital (no solo código). Son las más poderosas y las más peligrosas. La regla es absoluta: **VM o contenedor aislado, sin credenciales productivas, siempre.**

### 4.1 OpenClaw — y el caso de estudio de seguridad de 2026

**Qué es:** agente autónomo open-source creado por Peter Steinberger (originalmente "Clawdbot", luego "Moltbot" por presión de marca de Anthropic, hoy OpenClaw). Lanzado nov-2025. Ejecuta comandos shell, lee/escribe archivos, navega la web, manda correos, gestiona calendarios; se conecta a 20+ plataformas de mensajería (Telegram, Slack, Discord). Memoria por archivos Markdown tipo diario en `~/.openclaw`. Creció más rápido que cualquier repo en la historia de GitHub (180K → 267K+ → 346K stars en semanas). En feb-2026 Steinberger se fue a OpenAI a liderar agentes personales y el proyecto pasó a una fundación independiente patrocinada por OpenAI.

**Por qué es un caso de estudio obligatorio** (esto te enseña seguridad de agentes mejor que cualquier teoría):

- **CVE-2026-25253** (CVSS 8.8): RCE de un clic vía falla de validación de origen en WebSocket, explotable **incluso en instancias atadas a localhost** con solo visitar una web maliciosa. Parchado en **v2026.1.29** (30 ene 2026). En días aparecieron 9 CVEs más; para abril se rastreaban ~138 vulnerabilidades en 63 días (~2.2/día).
- **ClawHavoc** (ataque a la cadena de suministro de skills): el marketplace **ClawHub** fue inundado con **1,184 skills maliciosas** (~12–20% del registro), con nombres inocuos ("solana-wallet-tracker") que instalaban keyloggers en Windows o el *Atomic macOS Stealer*. Patrón típico: ofuscación Base64 → decodificar → `curl` a script remoto → ejecutar.
- **Exposición:** ~135,000 instancias expuestas a internet (feb), **93% sin autenticación**; ~63,070 en marzo (Censys). Brecha "Moltbook": 35,000 emails y 1.5M tokens de agente filtrados. Meta restringió su uso interno.
- **Mitigaciones del proyecto:** alianza con VirusTotal (feb-2026), verificación de publishers (mar-2026), modo sandbox `OPENCLAW_SANDBOX=true`.

**Lecciones senior (aplican a TODO agente, no solo OpenClaw):**
1. La barrera para publicar una skill maliciosa es subir un archivo de texto: **trata cada skill/plugin/MCP como código no confiable**.
2. Parchear el RCE **no** revoca permisos ya concedidos ni borra skills ya instaladas: el problema es de **gobernanza de permisos**, no solo de parches.
3. **Nunca** expongas un agente a 0.0.0.0 sin auth. Revisa con `osquery`/Censys si tienes instancias expuestas.
4. Fija versiones de skills, nunca auto-update, audita el código fuente antes de instalar.

**Criterio:** OpenClaw es genuinamente útil y educativo, pero **jamás en tu máquina principal con tus llaves**. VM aislada, usuario limitado, repos de prueba, tokens read-only.

### 4.2 Hermes Agent (Nous Research) — el agente que aprende

**Qué es:** agente self-hosted y self-improving de Nous Research (lab detrás de los modelos Hermes/Nomos/Psyche). Lanzado **25 feb 2026**, MIT. ~175K–188K+ stars (jun 2026) — el framework de agente open-source de más rápido crecimiento del año. Su diferencial es un **loop de aprendizaje cerrado**: crea skills a partir de la experiencia, las mejora durante el uso, persiste conocimiento, busca en sus propias conversaciones pasadas y construye un modelo de quién eres a través de sesiones.

- Corre como **daemon persistente** en tu infraestructura: desde un VPS de 5 USD hasta clúster GPU o **7 backends serverless** (Vercel Sandbox, Daytona, Modal…). Háblale desde Telegram mientras trabaja en una VM cloud.
- **Model-agnostic** (Nous Portal, OpenRouter 200+ modelos, NVIDIA NIM/Nemotron, Xiaomi MiMo, z.ai/GLM, Kimi, MiniMax, OpenAI, Bedrock).
- 18 plataformas de mensajería + MS Teams por plugin.
- Skills en `~/.hermes/skills/`, **compatibles con el estándar abierto `agentskills.io`** (portables, comunitarias vía Skills Hub — 90,000+ skills).
- v0.12+ trae un **Curator** autónomo que puntúa, fusiona y poda la librería de skills en un cron semanal. Soporta subagentes/paralelización, *Programmatic Tool Calling* (`execute_code`), MCP y migración automática desde OpenClaw.
- Componente aparte: `hermes-agent-self-evolution` usa **DSPy + GEPA** (ICLR 2026) para evolucionar skills/prompts leyendo trazas de ejecución y abriendo PRs contra el repo (ver §18).

**Criterio:** Hermes es el mejor laboratorio para estudiar agentes que aprenden. Mantenlo actualizado y **sandboxéalo** (mismo riesgo de permisos amplios que OpenClaw). Para producción corporativa, primero valida permisos, trazas, control de secretos y reproducibilidad.

### 4.3 La capa open-source madura (empieza aquí, costo cero)

Antes de tocar OpenClaw/Hermes en serio, estos proyectos te dan **más control y menos incidentes masivos**:

- **OpenHands** (open source, model-agnostic): plataforma completa de agente de software con sandbox, SDK y ejecución local/remota. Ideal para *aprender* la anatomía de un agente: planner, executor, browser, terminal, repo, logs.
- **Aider** (CLI, open source): pair programming en terminal con Git de primera clase; excelente para diffs limpios y commits atómicos.
- **Cline / Roo Code / Kilo Code** (extensiones VS Code, open source): agentes en el IDE, model-agnostic, conectan a APIs gratis.
- **Continue.dev + Tabby** (open source): autocompletado local con tu GPU/Ollama.
- **Goose** (Block, open source): agente CLI extensible vía MCP.

**Ruta recomendada de adopción:** Aider/Cline (entender) → OpenHands (anatomía completa, sandbox) → Hermes/OpenClaw (experimentos de auto-mejora y cross-app, en VM).


---

## 5. Cómo promptean y trabajan los expertos

### 5.1 Mejores prácticas de prompting por laboratorio

Los grandes labs convergen, pero con acentos distintos:

- **Anthropic (Claude):** separa visualmente *inputs* de *instrucciones*; usa etiquetas tipo XML (`<contexto>`, `<tarea>`, `<ejemplos>`, `<formato>`); aprovecha **prompt caching** (reduce costo y latencia de forma drástica en prompts largos repetidos); pon ejemplos concretos (few-shot); pide razonamiento explícito en tareas difíciles. Para agentes: `CLAUDE.md` corto y accionable; subagentes con descripción precisa; hooks deterministas.
- **OpenAI (GPT-5.5 / Codex):** instrucciones al inicio con delimitadores claros (`###`); herramientas en JSON schema explícito; caching automático; `AGENTS.md` para contexto de repo; usa `/init` para inicializar proyectos en Codex.
- **Google (Gemini):** few-shot casi siempre (zero-shot explícitamente menos preferido); **coloca los datos de entrada *después* de las instrucciones**; system instructions para multimodal (audio/imagen/texto juntos).
- **xAI (Grok):** aprovecha contexto largo para repos completos; delega a subagentes en paralelo cuando aplica.

**Reglas universales 2026:** intención clara y específica; estructura con headers; **ejemplos antes que reglas**; formato de salida explícito (JSON/Markdown/XML); contexto mínimo pero suficiente.

### 5.2 El patrón profesional de desarrollo con agentes

```text
1.  Escribir issue/tarea con criterios de aceptación claros
2.  Crear rama o worktree dedicado
3.  Pasar contexto MÍNIMO al agente (AGENTS.md + lo justo)
4.  Pedir PLAN antes de código
5.  Ejecutar cambios en lotes pequeños
6.  Correr tests
7.  Revisar el diff (siempre)
8.  Pedir a un SEGUNDO agente que actúe de reviewer
9.  Abrir PR
10. CI/CD
11. Merge humano
```

### 5.3 El patrón multiagente que sí funciona (y el que no)

No pongas 10 agentes "conversando" sin control. La investigación reciente es contundente: los sistemas multiagente siguen siendo **frágiles** (problemas de coordinación, infraestructura, mantenimiento y bugs), y en una evaluación de decenas de frameworks de agentes en Python **ninguno dominó todas las tareas** — el rendimiento varía mucho por tarea y costo. Más aún: para tareas **procedurales**, meter el procedimiento completo directamente en el prompt puede superar a un orquestador externo. Traducción: **no uses un framework si un script con buenas instrucciones basta.**

El patrón realista es jerárquico con roles y un humano que decide:

```text
Planner       → define tareas
Coder A       → implementa
Coder B       → alternativa / revisión cruzada
Tester        → crea y corre pruebas
Security      → revisa secretos, permisos, inyección
Architect     → evalúa impacto
Human         → decide el merge
```

### 5.4 Qué hace senior a un operador de agentes

Sabe **cuándo NO usar agentes**. Tiene tests y datos limpios. Usa trazas. Mide costo. Aísla permisos. Escribe prompts cortos y accionables. Mantiene documentación viva. Sabe SQL, Docker y Git. Entiende APIs y seguridad básica. Y evalúa modelos **con sus propias tareas**, no con hype ni benchmarks de marketing.

---

## 6. MCP, Skills, Plugins y archivos de contexto: cómo funcionan **de verdad** y si se comparten

Esta es una de tus preguntas centrales. La respuesta corta: **el protocolo (MCP) y los estándares de skills son compartidos; la configuración de cada cliente NO lo es automáticamente.** Vamos por partes.

### 6.1 MCP (Model Context Protocol)

Es el estándar de facto 2026, el "USB-C de la IA": permite que cualquier cliente compatible (Claude Code, Cursor, Codex CLI, Cline, Aider, n8n, agentes custom) use herramientas y datos externos (GitHub, filesystem, Postgres, navegador, Slack, Drive…) sin copiar-pegar. Datos clave del estado del protocolo:

- Anthropic lo open-sourceó a finales de 2024 (sobre JSON-RPC 2.0) y en **diciembre 2025 lo donó a la Linux Foundation** (Agentic AI Foundation), con gobernanza conjunta de Anthropic, OpenAI, Google, Microsoft, AWS, Cloudflare y Bloomberg. Las propuestas pasan por el proceso **SEP**.
- El SDK de MCP llegó a **~97 millones de descargas mensuales** (mar 2026); hay **20,000+ servidores** en registros públicos.

**Tipos de MCP y aquí está la clave de la compartición:**

| Tipo | Cómo corre | ¿Compartible entre clientes? |
|------|-----------|------------------------------|
| **STDIO local** | Cada cliente lanza su propio proceso (`node server.js`, `python server.py`, `npx ...`) | **No directamente**: cada cliente lo arranca por su cuenta. Compartes el *binario/código*, no la instancia |
| **HTTP / streaming HTTP** | Un servidor remoto o local expuesto por URL | **Sí**: un solo servidor, muchos clientes apuntando a la misma URL |
| **Dockerized** | En contenedor (Docker MCP Toolkit/Catalog) | Sí, vía HTTP o socket |
| **Hosted** | Servicio externo administrado (GitHub, Stripe…) | Sí |

**Conclusión operativa:** si quieres que el **mismo** MCP sirva a Claude Code, Codex, n8n y Cursor a la vez, **exponlo como HTTP** (en tu VPS/Docker con auth + HTTPS). Si lo dejas STDIO, cada cliente necesita su propia config para lanzarlo.

**Servidores MCP que de verdad valen la pena (jun 2026):**

- **El "starter pack" de 3:** **GitHub MCP** (gestión de repos/PRs/issues/Actions), **Context7** (inyecta documentación versionada — mata las APIs alucinadas; ~54K stars, por Upstash), **Playwright MCP** (automatización de navegador por *accessibility tree*, no por selectores frágiles; de Microsoft, el mejor valorado).
- **Por categoría:** Supabase MCP (todo tu backend), Postgres MCP (cuidado con la explosión de tokens en esquemas grandes), Figma MCP, Brave Search / Perplexity MCP (búsqueda con citas), Sentry MCP, Stripe MCP, Sequential Thinking (Anthropic), Filesystem (sandbox).
- **Catálogos:** `github.com/modelcontextprotocol/servers`, `github.com/appcypher/awesome-mcp-servers`, mcp.directory, PulseMCP.

**Advertencias senior sobre MCP:**
- Cada servidor conectado quema **2,000–5,000 tokens solo en inyección de esquema**. Mantén el set pequeño (**3–6**); más servidores = más latencia y colisiones de nombres de herramientas.
- Anthropic **archivó 13 de sus 20 servidores de referencia** en 2025 (solo 7 activos): muchos tutoriales apuntan a código muerto.
- Seguridad: en abr-2026 OX Security reveló un RCE sistémico en *todas* las implementaciones del SDK de MCP; Check Point reportó RCE en Claude Code vía archivos de config de repo envenenados. **Escanea endpoints MCP expuestos** (`/mcp`, `/sse`, bindings 0.0.0.0); herramientas como `mcp-scan` de Snyk ayudan.

### 6.2 Skills

Una **Skill** empaqueta un *procedimiento* reutilizable: un `SKILL.md` con *frontmatter* YAML (name, description, allowed-tools) + cuerpo de instrucciones + opcionalmente scripts, plantillas, ejemplos. MCP **conecta herramientas**; las Skills **enseñan procedimientos** — son complementarios.

**¿Se comparten skills entre Claude Code, Cowork, Hermes, OpenClaw, Codex?**

- **Conceptualmente, sí.** La *lógica* es portable: objetivo, procedimiento paso a paso, herramientas permitidas, formato de salida, criterios de terminado, errores comunes.
- **Técnicamente, depende.** Está emergiendo un **estándar abierto, `agentskills.io`**, que Hermes ya adopta y que hace las skills portables y compartibles. Claude Code/Cowork las leen de `.claude/skills/`; Hermes de `~/.hermes/skills/`; OpenClaw de su carpeta de skills. La estructura base (`SKILL.md` + frontmatter) es muy parecida, así que migrar es de bajo costo, pero cada ecosistema espera su ubicación y matices.
- **Estrategia recomendada (la que te ordena la vida):** mantén una **versión canónica en un repo Git** y adáptala por cliente. Ver §6.5.

**Ejemplo de skill BUENA** (para tu mundo inmobiliario):

```md
---
name: market-analysis-inmobiliario
description: Analiza mercado con comparables, DOM, precio m² y escenarios para AMG/Jalisco.
allowed-tools: [sql, web_search, vector_search]
---
# Objetivo
Generar un análisis de mercado verificable, con citas y datos no verificados marcados.

# Procedimiento
1. Extraer características del inmueble (colonia, m², recámaras, tipo, preventa/reventa).
2. Buscar comparables directos e indirectos.
3. Calcular precio m² y DOM por rango.
4. Estimar 3 escenarios (conservador/base/optimista).
5. Marcar [NO VERIFICADO] cualquier dato sin fuente.
6. Entregar recomendación accionable.

# Formato de salida
- Resumen ejecutivo
- Tabla de comparables
- Escenarios
- Riesgos
- Estrategia de comercialización
```

**Skill MALA:** `Haz un análisis excelente y profundo.` — sin procedimiento, sin herramientas, sin límites, sin formato. No sirve.

**Repos de skills/agentes famosos (Claude Code, jun 2026):** `anthropics/knowledge-work-plugins` (~20K stars, para Cowork y Code), `Claude-Flow` (~59K, orquestación), colecciones `agents` (~36K) de subagentes production-ready, `claude-code-security-review` (~5K, GitHub Action de seguridad), `defending-code-reference-harness` (~6K, threat modeling). En Hermes: `awesome-hermes-agent`, `SkillClaw` (evoluciona/deduplica tu librería).

### 6.3 Plugins

Un **plugin** empaqueta varias primitivas en una unidad instalable: skills + subagentes + hooks + MCP servers + slash commands + config. Anthropic ya da soporte oficial a plugins (los exploras desde el menú *Customize*; colección oficial en `anthropics/knowledge-work-plugins`). Antigravity mueve sus extensiones hacia plugins. **Regla:** un plugin es software con permisos. No instales plugins de repos desconocidos.

### 6.4 AGENTS.md y CLAUDE.md

`AGENTS.md` se volvió el **estándar portable** para decirle a cualquier agente cómo trabajar en un repo (lo leen Codex, y por convención muchos otros). `CLAUDE.md` es el equivalente específico de Claude Code. Buen contenido:

```md
# AGENTS.md
## Proyecto
Qué hace el sistema y su arquitectura (2–4 líneas).
## Setup
Comandos exactos para instalar y correr.
## Tests
Comandos exactos para probar.
## Estilo
Convenciones (lenguaje, formato, naming).
## Reglas críticas
- No modificar migraciones aplicadas sin autorización.
- No tocar secretos. No commits directos a main. Una rama por tarea.
- Explicar cambios destructivos antes de ejecutarlos.
## Criterios de terminado
- Tests y lint pasan. No hay secretos. Doc actualizada si cambió comportamiento.
```

**Cuidado, hay evidencia:** archivos de contexto **mal diseñados reducen el éxito y suben el costo** por inflar el contexto. Se han identificado "smells" como *context bloat*, *skill leakage* y *lint leakage*. Mantén estos archivos **cortos, exactos y vivos**. Un `AGENTS.md` que dice "eres el mejor programador del mundo, no falles" es ruido.

### 6.5 La organización canónica que te ordena TODO (monorepo de configuración)

Esta es la respuesta a "¿cómo ordeno y comparto memoria/skills/MCP entre varios IDEs, apps y proyectos?". Un **repositorio Git central de configuración de IA**, del que cada herramienta consume lo que necesita:

```text
ai-config/                      # repo Git versionado, tu "fuente de verdad"
├── AGENTS.md                   # plantilla base de instrucciones de agente
├── CLAUDE.md                   # variante específica de Claude (symlink o copia)
├── skills/                     # SKILL.md canónicos (formato agentskills.io)
│   ├── market-analysis-inmobiliario/
│   ├── rag-ingestion/
│   ├── code-review/
│   └── docx-c21-report/        # tu plantilla de reportes de factibilidad
├── mcp-servers/                # tus servidores MCP (idealmente HTTP para compartir)
│   ├── postgres-readonly/
│   ├── supabase-rag/
│   ├── filesystem-sandbox/
│   └── esdata-tools/
├── prompts/                    # prompts y system prompts reutilizables
├── memory/                     # memoria compartida (ver §9)
└── adapters/                   # scripts que "instalan" lo anterior en cada cliente
    ├── install-claude.sh       # copia/symlink skills a ~/.claude/skills/
    ├── install-hermes.sh       # a ~/.hermes/skills/
    └── install-codex.sh        # config MCP en ~/.codex/config.toml
```

**Cómo se comparte cada cosa, en una tabla honesta:**

| Componente | ¿Compartido entre clientes? | Mecanismo real |
|------------|------------------------------|----------------|
| **MCP HTTP** | ✅ Sí | Misma URL en cada cliente |
| **MCP STDIO** | ⚠️ El código sí, la instancia no | Cada cliente lo lanza; config por cliente |
| **Skills** | ⚠️ Lógica portable; ubicación por cliente | Repo canónico + adapters (`agentskills.io` ayuda) |
| **Plugins** | ❌ Específicos del ecosistema | Reempaquetar por cliente |
| **`AGENTS.md`** | ✅ Por repo | Vive en la raíz del proyecto; lo leen varios agentes |
| **`CLAUDE.md` / Cursor rules / .vscode** | ❌ Específicos | Uno por herramienta |
| **Memoria** | ⚠️ Vía MCP memory server + DB central | Disciplina: un tool escribe, otro lee (§9) |

Automatiza con un `make sync` o un hook que ejecute los adapters. Versiona todo en Git. Resultado: cambias una skill en un solo lugar y se propaga a Claude Code, Cowork, Codex y Hermes.

### 6.6 Instalación: el procedimiento correcto

**Repositorio de GitHub (cualquiera):**
```bash
git clone <repo> && cd <repo>
cat README.md                                   # leer antes de ejecutar
find . -maxdepth 2 -type f | grep -E "install|setup|Dockerfile|compose|requirements|pyproject"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                            # configurar variables
# Si trae Docker:  docker compose up -d && docker compose logs -f
```
Si pide `curl | bash`, **no lo ejecutes a ciegas**: `curl -fsSL <url> -o install.sh && less install.sh && bash install.sh`.

**MCP server (STDIO), ejemplo:**
```bash
# 1. instalar (ej. GitHub MCP)
npm install -g @modelcontextprotocol/server-github
# 2. añadir a Claude Code con token de permisos mínimos
claude mcp add github -- env GITHUB_TOKEN=$TOKEN npx -y @modelcontextprotocol/server-github
# 3. en Codex: editar ~/.codex/config.toml  (o  codex mcp ...)
# 4. en Cursor: Settings → MCP → Add Server
# 5. reiniciar cliente → verificar herramientas → probar acción READ-ONLY primero
```

**MCP server (HTTP, compartible):** despliega en VPS/Railway/Docker → añade **auth + HTTPS** → limita scopes → registra la URL en cada cliente → healthcheck → monitorea logs.

**Checklist de oro:** revisa commits e issues recientes (señal fuerte), docs y tests (señal fuerte), Dockerfile y licencia (obligatorio), quién mantiene, si pide llaves API. Las **stars son señal débil** (manipulables y atrasadas); pésalas, no te cases con ellas. Prueba en VM/contenedor si toca el sistema. Empieza siempre con permisos read-only y habilita escritura solo cuando sea necesario.


---

## 7. Frameworks de orquestación: cuándo sí y cuándo no

**Regla senior (repito porque es la más violada):** no uses framework si un prompt + herramientas resuelve la tarea. Sube de complejidad solo cuando la tarea lo exige.

| Framework | Úsalo cuando | Evítalo cuando | Licencia/coste |
|-----------|--------------|----------------|----------------|
| **(nada) prompt + tools** | Tarea lineal o procedural | — | Gratis |
| **LangGraph** | Necesitas agentes **durables, con estado, checkpoints, memoria y human-in-the-loop** | Solo quieres un chatbot simple | Open source |
| **OpenAI Agents SDK** | Agentes con herramientas, **handoffs, guardrails, sandbox, HITL y tracing** sobre OpenAI | Tu stack no es OpenAI / quieres neutralidad | Open source (consumo de API) |
| **Google ADK** | Agentes en ecosistema Gemini/Vertex/GCP con debugging y evals | No estás en Google Cloud | Open source |
| **LangChain** | Conectores, chains, loaders, ecosistema amplio | Necesitas control fino de flujos largos → usa LangGraph | Open source |
| **LlamaIndex** | RAG, indexación de documentos, retrieval | No tienes problema de datos/documentos | Open source |
| **CrewAI** | Prototipos *role-based* (researcher/writer/reviewer) | Producción con estado complejo y auditoría fuerte | Open source |
| **AutoGen / Microsoft Agent Framework / Semantic Kernel** | Mundo Microsoft/.NET/Azure | Stack Python/Node donde LangGraph basta | Open source |
| **Vercel AI SDK** | Apps web (Next/React/Vue/Svelte/Node) con streaming, tool calling, MCP, agentes y UI | Backend pesado persistente o workers largos | Open source |
| **n8n** | Automatización con APIs, webhooks, CRM, WhatsApp/Gmail/Calendar, cron, **AI Agent nodes + MCP Client** | Lógica algorítmica compleja o alto rendimiento | Open source (self-host) |

**Las tres rutas para orquestar:**
- **Open-source / cero costo:** n8n self-hosted (no-code) + LangGraph (código) en Docker. Resuelve el 90% de lo corporativo.
- **Costo-beneficio:** lo anterior + OpenAI Agents SDK para los flujos críticos con tracing nativo.
- **Premium:** plataformas gestionadas (n8n Cloud, LangGraph Platform, Bedrock AgentCore) cuando necesitas SLA, escala y cero ops.

---

## 8. RAG de verdad: vectorial, híbrido, SQL, grafo

### 8.1 El error típico

RAG **no** es "meter PDFs a un vector DB". RAG profesional tiene nueve etapas: ingesta (parsing/OCR/limpieza) → chunking **por estructura** (no por pedazos arbitrarios) → metadata rica (fuente, fecha, autor, versión, permisos, tipo) → embeddings → índices (vector + full-text + SQL + grafo) → retrieval (semántico + keyword + filtros + **reranking**) → grounding con citas → evaluación (recall@k, precisión, alucinaciones, costo, latencia) → gobernanza (permisos, versiones, logs, borrado).

### 8.2 Qué motor usar para qué

| Necesidad | Arquitectura |
|-----------|--------------|
| Documentos internos simples | Supabase/Postgres + **pgvector** + full-text |
| Búsqueda semántica a escala / filtros pesados | **Qdrant** (Rust, HNSW, payload filters fuertes) |
| Preguntas con entidades y relaciones (multi-hop) | **Neo4j GraphRAG** |
| Datos transaccionales / numéricos | **SQL / DuckDB / Polars / pandas** primero. RAG después |
| Documentos + permisos por usuario | Supabase con **RLS** + metadata filtering |
| "Second brain" personal | **Obsidian vault** → MCP server → agentes consultan nativamente |
| RAG corporativo serio | SQL + vector + grafo + **reranker** + evals |

**Cuándo NO usar vector DB:** "ventas por mes", "absorción por zona", "qué asesor convirtió más leads", "agrupa por colonia y precio m²", "regresión/inferencia". Eso es **SQL/DuckDB/Polars/Python**, no significado textual. El vector sirve para *significado*, no para contabilidad exacta.

### 8.3 Supabase, Qdrant, Obsidian — las tres rutas

- **Open-source / cero costo:** Postgres + pgvector + full-text en Docker; o Supabase self-hosted. Qdrant OSS en contenedor para escala. Obsidian vault + un MCP server self-hosted que indexa tus notas (todo local, sin nube).
- **Costo-beneficio:** Supabase free/Pro (Postgres + pgvector + auth + storage + RLS, todo-en-uno) + Qdrant Cloud free tier para vector a escala.
- **Premium:** Qdrant/Neo4j managed + reranker dedicado + pipeline de evals.

### 8.4 Arquitectura RAG ideal para proptech (ESDATA / Oráculo Predial)

```text
FUENTES        Portales · CRM · PDFs de desarrollos · contratos · avalúos ·
               Google Drive · WhatsApp/llamadas transcritas · catastro/mapas/POIs
                              │
INGESTA        Scrapers (tu Scrap Ultra) + parsers + normalizadores + dedup
                              │
ALMACENAMIENTO Postgres/Supabase → propiedades, leads, asesores, proyectos, precios, DOM
               Object storage     → PDFs, imágenes, fichas, contratos
               Qdrant (vector)    → chunks, amenidades, descripciones, comparables
               Neo4j (grafo)      → propietario-proyecto-desarrollo-asesor-lead-zona
                              │
CONSULTA       SQL para números · vector para documentos · grafo para relaciones ·
               reranker para precisión · LLM para síntesis CON CITAS
                              │
CONTROL        permisos por rol · auditoría · logs · trazas · evals
```

Para Oráculo Predial específicamente: el **SQL/grafo** es donde viven los coeficientes urbanísticos, la info registral y los riesgos (datos exactos, con fuente y fecha); el **vector** ayuda a recuperar texto normativo y descripciones; el **LLM** sintetiza con citas y marca lo no verificado. Nunca dejes que el LLM "calcule" un coeficiente: que lo lea de la fuente estructurada.

---

## 9. Memoria compartida entre agentes, proyectos y herramientas

La memoria persistente cross-tool es **posible pero experimental**; requiere disciplina. Patrón recomendado:

```text
        ┌──────────────────────────────────────────┐
        │  Memoria central (fuente de verdad)        │
        │  Postgres + pgvector  (hechos + embeddings)│
        │  + archivos Markdown versionados en Git    │
        └──────────────────────────────────────────┘
                 ▲ escribe            ▼ lee
        ┌────────┴───────┐   ┌────────┴────────┐
        │ MCP memory      │   │ MCP memory       │
        │ server (HTTP)   │   │ server (HTTP)    │
        └────────┬───────┘   └────────┬────────┘
   Claude Code ──┘   Codex ──┘   n8n ──┘   Hermes ──┘
```

- **Mecanismo:** un **MCP memory server** expuesto por HTTP, respaldado por una DB central (Postgres/pgvector o Qdrant). Todos los clientes que hablan MCP pueden leer/escribir esa memoria.
- **Disciplina obligatoria:** define **quién escribe y quién lee** para evitar inconsistencias (un agente "secretario" escribe; los demás leen). Versiona la memoria estructurada en Git cuando sea conocimiento estable.
- **Niveles de memoria:**
  - *De repo*: `CLAUDE.md`/`AGENTS.md` (convenciones, decisiones).
  - *De proyecto*: notas, decisiones de arquitectura, glosario (Obsidian/Notion + MCP).
  - *Operacional/episódica*: lo que el agente aprende por sesión (Hermes lo hace nativo con su Curator; ojo con el *drift*).
- **Cuidado con la sobre-confianza:** memoria persistente que "se vuelve rara" sola es un riesgo real (drift). Acompáñala de chequeos de regresión y linting de prompts/config.

---

## 10. Docker y entornos reproducibles

Docker no es opcional para trabajar senior con agentes. Te da **laboratorios reproducibles** y **sandboxes** para aislar el riesgo.

- **Docker Compose** define servicios, redes y volúmenes en YAML y los levanta con un comando: ideal para Postgres, Qdrant, Neo4j, Redis, n8n, Langfuse, workers, APIs, MCP servers.
- **Docker Model Runner** corre modelos localmente (empaqueta modelos como artefactos OCI) y los conecta a Cline, Continue, Cursor, Aider u Open WebUI.
- **Docker MCP Catalog/Toolkit** ofrece MCP servers verificados y containerizados (resuelve conflictos de entorno y parte del problema de seguridad).

**Usa Docker para:** DBs, vector/grafo, Redis, n8n, Langfuse, Open WebUI, MCP servers, workers, sandboxes de agentes.
**No uses Docker para:** GUI compleja, drivers raros sin necesidad, cargas que exijan latencia ultrabaja local, o cuando ni siquiera entiendes el comando manual todavía.

### 10.1 Tu "laboratorio en una caja" (docker-compose base, cero costo)

Este es el stack que montas una vez y te sirve para casi todos los labs del §22:

```yaml
# docker-compose.yml  (laboratorio IA self-hosted)
services:
  postgres:        # hechos + pgvector
    image: pgvector/pgvector:pg16
    environment: { POSTGRES_PASSWORD: change_me }
    volumes: [ pgdata:/var/lib/postgresql/data ]
  qdrant:          # vector a escala
    image: qdrant/qdrant
    volumes: [ qdrant:/qdrant/storage ]
  neo4j:           # grafo (GraphRAG)
    image: neo4j:5
    environment: { NEO4J_AUTH: neo4j/change_me }
    volumes: [ neo4j:/data ]
  redis:           # colas / memoria efímera
    image: redis:7
  n8n:             # orquestación no-code
    image: n8nio/n8n
    ports: [ "5678:5678" ]
    volumes: [ n8n:/home/node/.n8n ]
  langfuse:        # observabilidad (ver su compose oficial, ~6 servicios)
    image: langfuse/langfuse:3
    ports: [ "3000:3000" ]
  ollama:          # modelos locales (Gemma 4 E4B, Qwen)
    image: ollama/ollama
    ports: [ "11434:11434" ]
    volumes: [ ollama:/root/.ollama ]
    # GPU (tu RTX 3080 Ti): gpus: all + NVIDIA Container Toolkit
volumes: { pgdata: , qdrant: , neo4j: , n8n: , ollama: }
```

> Nota: Langfuse v3 trae su propio compose (Postgres + ClickHouse + etc.). Úsalo en vez de la línea de arriba para producción de trazas. Para Ollama con tu GPU instala el **NVIDIA Container Toolkit** y añade `gpus: all`.

---

## 11. Hosting: Vercel, Railway, VPS y Amazon Bedrock

### 11.1 Vercel — frontend y AI UI

Ideal para Next.js, frontend, APIs serverless ligeras, streaming de UI de IA, chatbots web, y MCP servers sencillos. Lo que lo hace especial para IA en 2026:

- **Fluid Compute** (feb-2025): una instancia atiende múltiples solicitudes concurrentes.
- **Active CPU Pricing** (jun-2025): **solo pagas los milisegundos de CPU activa; el tiempo de espera de I/O cuesta 0 USD** → hasta ~90% de ahorro en cargas con esperas (inferencia LLM, queries). Esto es enorme para apps de IA, que pasan mucho tiempo esperando al modelo.
- **AI Gateway** (100+ modelos, smart routing, fallback automático entre proveedores, observabilidad), **Vercel Sandbox** (código no confiable/generado por IA en microVMs hasta ~45 min, Node y Python), **v0**, microfrontends, rolling releases, Queue.
- Precios: **Hobby gratis**; **Pro 20 USD/asiento + uso**.

### 11.2 Railway — backend persistente

Mejor para backends con proceso vivo: APIs, workers, cron jobs, servicios Docker, Postgres, volúmenes persistentes. Precio usage-based (puede ser barato). **Advertencia conocida:** históricamente, cuando se agotan los créditos puede apagar apps; monitorea el saldo.

### 11.3 VPS — control total, costo cero de licencias

Conviene cuando necesitas control total, Docker Compose 24/7, n8n permanente, MCP servers privados, workers largos, scraping, bots, webhooks, colas, túneles. Stack típico:

```text
Ubuntu Server 24.04 · Docker + Compose · Caddy o Traefik (HTTPS) ·
n8n · Postgres · Redis · Qdrant · MCP servers · workers ·
backups automáticos · firewall · SSH keys · Fail2ban
```

Tamaños orientativos: 2 vCPU/4 GB para un MCP/bot ligero; **4 vCPU/8–16 GB para un laboratorio serio**; 8 vCPU/32 GB para multiagente + scrapers + DBs cómodas. Proveedores económicos para labs: Hetzner, Contabo (un ejemplo real: migrar de Make Teams ~348 USD/mes a n8n self-hosted en un VPS ~12 USD/mes).

### 11.4 Amazon Bedrock y AgentCore — la opción enterprise

- **Bedrock**: pricing de modelos fundacionales (inferencia). En 2026 cataloga incluso GPT-5.5 además de Claude, etc. Útil si ya estás en AWS y quieres multi-modelo con gobernanza.
- **Bedrock AgentCore**: plataforma modular para agentes con **12 componentes facturables** (Runtime, Browser, Code Interpreter, Gateway, Identity, Memory, Policy, Evaluations…). Runtime ~0.0895 USD/vCPU-hora + ~0.00945 USD/GB-hora, facturación por segundo. Modelo de CPU activa (no pagas el I/O idle). Es potente pero **complejo de costear** (varias líneas corren a la vez); úsalo cuando necesites despliegue enterprise con identidad, memoria y evals gestionados.

### 11.5 Decisión rápida

| Caso | Usa |
|------|-----|
| Landing / SaaS frontend / dashboard Next.js / chat de IA | **Vercel** |
| API persistente + worker + DB | **Railway** (o VPS) |
| n8n + MCP + bots + scraping + Compose 24/7 | **VPS** |
| Laboratorio IA completo self-hosted | VPS o máquina local |
| Producción corporativa con identidad/memoria/evals gestionados | **Bedrock AgentCore** / cloud + IaC + CI/CD |

**Rutas:** cero costo = VPS barato + Docker Compose + Caddy (todo self-hosted). Costo-beneficio = Vercel (frontend) + Railway o VPS (backend). Premium = AWS/GCP con IaC, AgentCore y observabilidad gestionada.

---

## 12. Sistemas operativos: Windows vs Ubuntu vs Linux Mint

### 12.1 Recomendación honesta

- **Ubuntu 24.04 LTS** es la opción más estándar para IA/dev/servidores: la mayoría de docs, drivers NVIDIA/CUDA, Docker y tutoriales apuntan ahí.
- **Windows 11 Pro + WSL2 Ubuntu** es excelente si además usas Office, Hyper-V, apps de escritorio y quieres drivers NVIDIA cómodos. Es, de hecho, **tu mejor opción de PC diario** dado que ya operas en Windows y tienes RTX.
- **Linux Mint** es más amigable como escritorio (arranca más rápido y usa algo menos de RAM que Ubuntu; usa Flatpak en vez de Snap forzado), pero para servidores/IA pesada Ubuntu/Proxmox ganan por ecosistema y soporte.

### 12.2 Para tu caso

| Escenario | Sistema |
|-----------|---------|
| PC principal Windows con muchas apps + RTX | **Windows 11 Pro + WSL2 Ubuntu** |
| Laptop dev simple | Ubuntu 24.04 LTS |
| Usuario no técnico / workstation ligera | Linux Mint |
| Servidor 24/7 | Ubuntu Server o Proxmox |
| Varias VMs serias | Proxmox |
| VMs en PC Windows | Hyper-V |

### 12.3 Windows vs Ubuntu para OpenClaw / Hermes / automatización

Ubuntu gana para estos casos por: Docker nativo (sin overhead de WSL), mejor soporte de drivers NVIDIA, cron nativo, menos overhead de RAM. Windows + WSL2 es aceptable y cómodo si vives en el ecosistema Microsoft. **Para automatizar la GUI de Windows**, Windows nativo. **Para automatizar navegador/servicios**, Linux. **Para agentes de alto riesgo (OpenClaw/Hermes), VM aislada SIEMPRE**, sin importar el host.

---

## 13. Virtualización y hardware para muchas máquinas virtuales

### 13.1 Hypervisor por plataforma

| Aspecto | Hyper-V (Windows) | VirtualBox | KVM/QEMU (Linux) / Proxmox |
|---------|-------------------|------------|----------------------------|
| Tipo | Type-1 (menor overhead) | Type-2 (mayor overhead) | Type-1 (mejor rendimiento) |
| GPU passthrough | ✅ partición/reserva de GPU | ❌ limitado | ✅ VFIO passthrough |
| Uso personal | Más complejo | ✅ simple, cross-platform | Curva mayor, máximo control |
| Mejor para | VMs en Windows con GPU | Labs portátiles simples | Servidor dedicado de VMs/LXC |

**Veredicto:** en Windows, **Hyper-V** para IA (mejor que VirtualBox). En Linux, **KVM/QEMU** (superior a ambos). Para un servidor dedicado solo a VMs/contenedores, **Proxmox** (combina KVM para VMs y LXC para contenedores, con GUI, API, clusters).

### 13.2 Hardware óptimo para correr varias VMs con IA ligera

| Componente | Recomendado |
|------------|-------------|
| CPU | 12–16 núcleos (Ryzen 9 / Intel i9) |
| RAM | 64 GB DDR (mínimo 32 GB) — **la RAM es lo que limita el número de VMs** |
| Disco | 2 TB NVMe Gen4 |
| GPU | Solo si servirás modelos; passthrough en Hyper-V/KVM |

C�lculo orientativo (VMs ligeras con API remota, 2 cores/4 GB c/u): con 64 GB de RAM corres ~12 VMs simultáneas; con 128 GB, ~25. Si las VMs corren modelos locales, la cuenta la manda la VRAM, no el número de cores.

---

## 14. Hardware: mínimo, tu equipo y para correr Gemma 4 E4B

### 14.1 Mínimo para Hermes, OpenClaw y automatizaciones

La clave: **estos agentes consumen poco si el modelo corre por API remota.** El gasto local es del daemon, no del modelo.

| Framework | CPU | RAM | Disco | Idle |
|-----------|-----|-----|-------|------|
| OpenClaw (mínimo) | 1–2 vCPU | 2 GB | 20 GB SSD | ~180 MB |
| OpenClaw (cómodo) | 4 cores | 8–16 GB | 100 GB NVMe | — |
| Hermes (mínimo) | 2 cores | 4 GB | 60 GB SSD | ~2 GB |
| Hermes (recomendado) | 4 cores | 8 GB | 100 GB SSD | — |

Es decir: un **VPS de 4 vCPU / 8 GB** corre Hermes/OpenClaw + n8n + un par de MCP servers sin drama, usando APIs gratis o baratas para la inferencia. Hermes incluso anuncia operar desde un VPS de 5 USD.

### 14.2 Tu equipo actual (Ryzen 7 5800X3D + RTX 3080 Ti 12 GB) — diagnóstico

Tienes un equipo **muy bien balanceado para todo lo de este manual sin comprar nada**:

- **CPU (5800X3D):** excelente single-thread y caché 3D; sobra para Docker Compose pesado, n8n, scrapers (tu Scrap Ultra), DBs, varias VMs ligeras.
- **GPU (RTX 3080 Ti, 12 GB VRAM):** corre cómodamente **Gemma 4 E4B**, **Gemma 4 12B en 4-bit (~8 GB)**, **Qwen2.5-Coder 14B en Q4_K_M (~9–10 GB)** y modelos de visión 4B para análisis de cámaras. No es para servir frontier local, pero para edge/privacidad/offline es ideal.
- **Recomendación de RAM:** si aún no estás en 64 GB, ese es el upgrade con mejor ROI para correr más VMs y contenedores en paralelo.

**Regla práctica de VRAM (Q4_K_M):** modelo 8B ≈ 6 GB · 14B ≈ 10 GB · 32B ≈ 20–22 GB · 70B ≈ 43 GB. Lo crítico es que **el modelo quepa entero en VRAM**: si cabe, corre 5–10× más rápido que si se derrama a RAM.

### 14.3 Mínimo "sin modelos grandes locales" (PC de trabajo)

| Componente | Mínimo funcional | Recomendado serio |
|------------|------------------|-------------------|
| CPU | 6 núcleos / 12 hilos | 12–16 núcleos |
| RAM | 32 GB | 64–128 GB |
| SSD | 1 TB NVMe | 2–4 TB NVMe |
| GPU | Opcional (8–12 GB si local LLM) | 12–24 GB |
| SO | Windows 11 Pro + WSL2 / Ubuntu 24.04 | Proxmox / Ubuntu Server / Win Pro + Hyper-V |

El mínimo te corre VS Code, Claude Code/Codex, Docker, n8n, Supabase ligero, Qdrant, Ollama con modelos pequeños y 1–2 VMs. El recomendado, todo el laboratorio completo.

---

## 15. Modelos locales: alcances y límites **reales** (Gemma 4 y Qwen)

### 15.1 Gemma 4 (la familia que corres)

**Gemma 4** es real, de Google DeepMind, "construida a partir de la investigación de Gemini 3", **Apache 2.0**, lanzada ~junio 2026. Cinco tamaños: **E2B, E4B, 12B, 26B-A4B (MoE), 31B**. Multimodal: texto + imagen (todos), **audio nativo en E2B/E4B/12B**, comprensión de video. **Function calling nativo**. Contexto: **128K (E2B/E4B)**, **256K (12B/26B/31B)**. 140+ idiomas. Modos de *thinking* configurables. Corre en llama.cpp, Ollama, vLLM, LM Studio, MLX, SGLang, Unsloth. Variante **MTP** (multi-token prediction) acelera la inferencia 1.4–2.2× sin pérdida.

| Modelo | Params (efectivos) | RAM/VRAM (4-bit) | Velocidad aprox. | Mejor para |
|--------|--------------------|-------------------|------------------|------------|
| **E2B** | ~2.4B | ~4–5 GB | muy rápida (CPU) | Edge, móviles, extracción simple, sub-200 ms |
| **E4B** | ~4.7B | ~5–7 GB | rápida | **Balance óptimo**: chat, extracción, agentic ligero, visión + tools |
| **12B** (unified) | 12B | ~8 GB (4-bit) / 14 GB (8-bit) | media | Multimodal completo (audio/video nativo), corre en laptop de 16 GB; supera a Gemma 3 27B |
| **26B-A4B / 31B** | MoE / dense | 16+ GB | menor | Workstation; máxima capacidad open |

**Límites reales de E2B/E4B:** velocidad, privacidad y costo-cero por token, **sí**. Razonamiento multi-paso complejo, coding agentic largo y tool-calling de precisión frontier, **no** — no reemplazan a Claude/GPT/Gemini. Úsalos como **complemento**: extracción de fichas, clasificación de leads, resúmenes, descripciones de imágenes (cámaras), fallback offline. Para tu `gemma4:e4b`: configura `num_ctx` moderado (4K–8K) si quieres más velocidad; el contexto largo y la multimodalidad consumen VRAM.

```bash
ollama run gemma4:e4b          # tu caballo de batalla local (visión + tools)
ollama run gemma4:e2b          # edge ultra-ligero
ollama run gemma4:12b          # multimodal completo (te cabe a 4-bit en 12 GB)
```

### 15.2 Qwen (coding y razonamiento local)

La familia Qwen se mueve rápido: **Qwen2.5-Coder → Qwen3 → Qwen3.5 → Qwen3.6**. Lo verificado y útil:

- **qwen2.5-coder:7b-instruct** (~6.6–8 GB en Ollama): sigue siendo **excelente para autocomplete y coding básico de Python/JS** (con Continue.dev/Tabby). Tool-calling **limitado**. El "default local de coding" ya es disputado, pero rinde muy bien para su tamaño.
- **qwen2.5-coder:14b** (~9–10 GB Q4): mejor para refactors; te cabe en tu 12 GB.
- **Qwen3 7B**: el mejor modelo de código <8B por HumanEval (~76), fuerte multilingüe; **Qwen3 tiene el tool-calling más estable entre los locales**.
- **Qwen 3.5 9B**: más fuerte en razonamiento/coding/multilingüe para su tamaño; bueno para conversaciones de "refactor este módulo". Tool-calling/agentic por encima de E4B pero por debajo de 30B+ o frontier en loops multi-turno precisos.
- **Qwen 3.6 (27B / 35B-A3B MoE)**: el nuevo "default" si tienes 16–24 GB+; Apache 2.0, tool-calling out-of-the-box. El 35B-A3B necesita 64 GB+ de RAM para offload híbrido.

**Patrón de coding local en tu 12 GB:** `qwen2.5-coder:7b` para tab-complete + cambias a un modelo de 14B (o Qwen 3.5 9B) para "refactoriza este módulo". No necesitan correr a la vez.

### 15.3 Ollama vs llama.cpp vs vLLM (el matiz importante)

- **Ollama:** la forma más simple de correr modelos locales (lo que ya usas). Suficiente para prototipos, edge y dev. **Caveat:** en algunos benchmarks rinde menos tokens/seg que alternativas nativas.
- **llama.cpp:** máximo control y rendimiento por GPU/CPU; un poco más de fricción de setup.
- **vLLM:** para **producción y multi-usuario / contexto largo de alto throughput**. Si algún día sirves un modelo local a varios usuarios o a un agente con loops intensos, migra a vLLM.

**Estrategia híbrida (la que ahorra de verdad):** local para el ~70% (rutina, código sensible, offline) y frontier por API para el ~30% (problemas difíciles, decisiones de arquitectura, producción crítica). Esto entrega ~80–90% de la productividad de "todo cloud" al 10–30% del costo, manteniendo privacidad.

---

## 16. APIs gratis y baratas 2026 + router multi-proveedor

**Regla:** los tiers gratis **cambian constantemente** y casi siempre **entrenan con tus datos** (su forma de financiarse). Úsalos para laboratorio y prototipos; mantén producción y datos de clientes fuera de ellos. El cuello de botella nunca es el precio, es el **rate limit**.

### 16.1 Panorama verificado (jun 2026, sin tarjeta salvo nota)

| Proveedor | Modelos destacados | Tier gratis aprox. | Notas |
|-----------|--------------------|--------------------|-------|
| **Google AI Studio (Gemini)** | Gemini 2.5/3.x Flash | ~1,500 req/día, 10 RPM, 1M contexto, multimodal | **El mejor acceso gratis a un frontier cerrado**. Cuotas recortadas 50–80% a fines de 2025; verifica en ai.google.dev. Gemini 2.0 retirado jun-2026 |
| **Cerebras** | Llama 3.3 70B, Qwen3 32B | **1M tokens/día** | El más generoso en volumen crudo; hardware ultrarrápido |
| **Groq** | Llama 3.3 70B, Qwen3 | 30 RPM, 1,000 RPD, 12K TPM | El más **rápido** (LPU). Límites recortados en 2026 (antes 14,400 RPD) |
| **Mistral** | Large, Codestral | ~1B tokens/mes (opt-in a training) | Tier Experiment → Production (pago, sin training) |
| **OpenRouter** | DeepSeek R1, Llama, Qwen3, Gemma 3 (~30 free) | ~20 RPM/modelo, ~50 req/día | **Una sola API OpenAI-compatible** para decenas de modelos |
| **NVIDIA NIM** (build.nvidia.com) | DeepSeek R1, Kimi, Nemotron | 40 RPM, ~1K créditos | Inferencia optimizada |
| **SambaNova** | varios | rápido, límites estrictos | Velocidad |
| **GitHub Models** | GPT-4o/4.1, o3, Llama | 10–15 RPM, 50–150 req/día | Mezcla amplia |
| **DeepSeek** | V3, R1 | 5M tokens, sin límite duro | — |
| **Xiaomi MiMo** | MiMo-V2-Pro (OpenAI/Anthropic-compat) | tier generoso `[VERIFICAR]` | Partnerships con OpenClaw/Cline/etc.; fuerte en agentic en reportes recientes |
| **xAI** | Grok 4, Grok 4.1 Fast | ~25 USD en créditos de registro | — |

### 16.2 Tu router multi-proveedor (lo que ya haces, refinado)

Tu patrón actual (Groq, Cerebras, Gemini, Mistral, SambaNova, OpenRouter) es **correcto y vigente**. Para hacerlo robusto:

- **Estandariza con failover:** usa el patrón "base-URL swap" entre un proveedor primario y uno secundario, ambos OpenAI-compatible (ej. OpenRouter primario, Groq secundario). Tu código no cambia; el sistema salta de endpoint cuando golpeas un rate limit.
- **Enruta por capacidad:** contexto muy largo → Gemini (AI Studio); máxima velocidad → Groq/Cerebras; coding → variantes Qwen-coder / Codestral; agentic con tools → el de tool-calling más estable.
- **Capa de gateway (open-source):** **LiteLLM** (proxy unificado), Portkey o el propio AI Gateway de Vercel para load-balancing, fallbacks y caching. Para observar costo/latencia, conéctalo a Langfuse.

**Las tres rutas de modelos:**
- **Cero costo:** Ollama local (Gemma 4 E4B / Qwen-coder) + tiers gratis enrutados con failover. El 90% de tus prototipos corre así a 0 USD/mes.
- **Costo-beneficio:** lo anterior + suscripción a UN frontier para lo crítico (Claude Code Pro o Codex), pagando solo el 10% de llamadas de alto valor.
- **Premium:** múltiples frontier por API + Bedrock/Vertex con gobernanza, para producción corporativa.

---

## 17. Observabilidad: Langfuse y las métricas que importan

En producción seria, **observabilidad no es opcional**. n8n te dice "el nodo corrió" (un check verde con JSON); no te dice qué modelo reintentó tres veces, cuántos tokens costó, si una herramienta devolvió vacío, o por qué el agente eligió el segundo mejor camino. Para eso:

- **Langfuse** (open source, **MIT**, self-hosted vía Docker Compose v3 o Kubernetes): trazas, *observations* tipadas (generations/spans/events), sessions, scores; **prompt management con versionado**; **LLM-as-Judge** con trazado de ejecución completo; datasets; **agent graph view (beta)** para flujos tipo LangGraph; SDK v4 **OpenTelemetry-native**. Integra con OpenAI, LangChain, LlamaIndex, Pydantic AI, Vercel AI SDK y **n8n** (vía OpenTelemetry / shipper comunitario). Cloud Hobby gratis (50K observations), Core ~29 USD/mes, Pro ~199 USD/mes.
- **Alternativas:** **LangSmith** (la integración más profunda con LangChain/LangGraph: state diffs nodo a nodo, replay contra nuevos modelos; cerrado, self-host solo Enterprise), **Arize Phoenix** (OTel-native, open source), **Laminar** (debugging de agentes), W&B Weave, Braintrust.
- **Importante:** **Helicone entró en modo mantenimiento (3 mar 2026)** — no lo elijas para roadmap nuevo.

**Cómo conectar n8n → Langfuse (cero costo, ~30 min):** una imagen de n8n que exporta trazas OpenTelemetry a Langfuse en cada ejecución; cada nodo mapea a su tipo de observation (Generation para llamadas al modelo, Agent para AI Agent nodes, Tool para HTTP/utilidades). Resultado: cada workflow se vuelve una traza con tokens, costo, reintentos, latencia y filtrado por userId/sessionId.

**Métricas que un senior trackea:** tokens por tarea · latencia p50/p95/p99 · accuracy vs costo · **self-correction rate** (cuántas veces el agente se corrige solo) · tasa de error de herramientas · costo por tarea/usuario.

**Rutas:** cero costo = Langfuse self-hosted. Costo-beneficio = Langfuse Cloud Hobby/Core. Premium = LangSmith/Arize + APM de infraestructura (Datadog/Honeycomb) para cobertura whole-stack.

---

## 18. IA auto-mejorándose: la ciencia real (no el hype)

Pediste la ciencia, así que aquí está el estado verificado, con papers reales — no marketing.

### 18.1 Qué es real

- **Darwin Gödel Machine (DGM)** — Sakana AI / UBC / Vector Institute (Zhang, Hu, Lu, Lange, Clune), **conference paper en ICLR 2026**. Un sistema que **modifica su propio código** (mejorando así su capacidad de modificarse) y **valida empíricamente cada cambio con benchmarks de coding**. Mantiene un **archivo abierto** de todos los agentes generados como "stepping stones" (exploración open-ended, no una sola línea evolutiva). Resultados: **SWE-bench 20.0% → 50.0%**, **Polyglot 14.2% → 30.7%**. Descubrió por sí solo mejores herramientas de edición, estrategias de manejo de contexto largo y mecanismos de peer-review de sus salidas. Código: `github.com/jennyzzt/dgm`.
- **El límite clave del DGM:** la auto-mejora funciona bien **solo cuando el dominio de la tarea coincide con el sustrato de modificación** (ambos coding). Para matemáticas, poesía o revisión de papers, mejorar la tarea **no** mejora la capacidad de auto-modificarse.
- **HyperAgents / DGM-H** — Meta (mar 2026): fusiona el *task agent* y el *meta agent* en **un solo código auto-modificable** → "auto-modificación metacognitiva" (mejora su propio proceso de mejora), extendiéndose a dominios no-código (revisión de papers, diseño de funciones de recompensa en robótica, olimpiadas).
- **ShinkaEvolve** (Sakana AI, ICLR 2026, open source): descubrió una **función de pérdida de balanceo para MoE** que superó el estado del arte de DeepSeek en ~30 generaciones; SOTA en circle-packing con ~150 evaluaciones (vs miles).
- **AlphaEvolve** (DeepMind) y su implementación open-source **OpenEvolve** (MAP-Elites + cascade evaluator); **CodeEvolve** superó a AlphaEvolve en 4 problemas. **SICA** (Self-Improving Coding Agent), línea independiente.

### 18.2 Los límites honestos

- **Reward hacking:** los agentes encuentran atajos que **engañan la métrica sin mejorar de verdad**. Es el riesgo central de cualquier loop de auto-mejora.
- **S-curve, no exponencial:** la mejora compone, pero la evidencia favorece una curva en S (rendimientos decrecientes) salvo prueba fuerte de escalado ilimitado.
- **Fragilidad de los sistemas multiagente** (ya citada en §5.3): coordinación, infraestructura y mantenimiento siguen siendo problemas abiertos.

### 18.3 Qué puedes construir tú (lab medible)

El componente que tienes a mano es **Hermes + `hermes-agent-self-evolution` (DSPy + GEPA)**: el agente genera una skill → la ejecuta → evalúa contra un harness → GEPA lee las trazas para entender *por qué* falló (no solo *que* falló) → propone variantes → pasa *constraint gates* (tests, límites de tamaño, benchmarks) → abre PR. **Mide el *improvement rate* y vigila el reward hacking.** Los datos internos de Nous afirman que agentes con 20+ skills auto-creadas completan tareas similares ~40% más rápido (menos tokens y tiempo, **no** "mejor salida"). Trátalo como hipótesis a verificar con tu propio harness, no como verdad.

---

## 19. Análisis de video de cámaras de seguridad (edge, privacy-first)

El stack DIY open-source maduro y de costo casi cero es **Frigate + un VLM local + orquestador**:

- **Frigate** (open source, `blakeblackshear/frigate`): NVR local con detección de objetos en tiempo real (OpenCV + Tensorflow), pensado para Home Assistant; recomienda un detector dedicado (Coral TPU o tu GPU). En 0.15+ trae **Semantic Search** (embeddings CLIP de los thumbnails, todo local) y **GenAI Search**; 0.17 suma **resúmenes GenAI de eventos** y reconocimiento de matrículas (LPR). Frigate+ (pago) ofrece modelos afinados con imágenes de usuarios.
- **VLM local para descripciones contextuales:** Frigate soporta cualquier proveedor OpenAI-compatible. La doc usa de ejemplo **`qwen3-vl:4b`** en Ollama; también LLaVA/Moondream o **Gemma 4 E4B (visión + tools)**. Un modelo de visión 4B (4-bit) cabe en 8 GB de VRAM — **tu RTX 3080 Ti lo corre de sobra**.

**Arquitectura recomendada (todo local en tu equipo):**

```text
C�mara IP (RTSP)
   → Frigate            (detección + tracking + recorte del objeto)
   → Ollama + qwen3-vl:4b / gemma4:e4b   (descripción contextual: "persona con playera azul
                                           en la entrada al anochecer")
   → Home Assistant / n8n  (reglas de alerta por objeto, zona y hora → WhatsApp/Telegram)
```

Tendencias 2026: el procesamiento pasó de "detección de movimiento" a **razonamiento contextual**; las cámaras procesan localmente y envían solo metadatos (privacy-first, menor consumo). Para tu contexto (oficinas/propiedades), esto te da búsqueda en lenguaje natural sobre las grabaciones ("muéstrame autos rojos en la entrada el martes") sin enviar video a la nube.

**Rutas:** cero costo = Frigate + Ollama (Gemma/Qwen-VL) + Home Assistant, todo local. Costo-beneficio = lo anterior + Frigate+ o Gemini API para descripciones más ricas. Premium = cámaras con IA en el edge (Verkada/UniFi Protect AI) si quieres hardware llave en mano.

---

## 20. Big data e inferencia estadística (no uses LLM para números)

El principio que te ahorra errores y dinero: **el LLM es para significado y síntesis, no para cálculos exactos.** Los números van a herramientas deterministas.

**Stack recomendado:**
- **DuckDB / Polars / pandas** para análisis en memoria (rapidísimo, cero infraestructura).
- **Postgres** para datos transaccionales; **ClickHouse** si llegas a millones de eventos (OLAP).
- **statsmodels / scikit-learn** para inferencia y modelado.
- **dbt** para transformaciones versionadas; **MLflow / W&B** para tracking de experimentos.
- LLM **solo** para la síntesis narrativa final, con citas.

**Experimentos inmobiliarios (tu dominio, con tu background actuarial):**
1. Precio m² por colonia · DOM por rango de precio · absorción por zona.
2. **Regresión hedónica** de precio (variables: m², recámaras, amenidades, ubicación).
3. Segmentación/clustering de propiedades y de leads (NSE, DISC, DINKs, empty nesters).
4. Elasticidad precio-demanda · forecast de inventario.
5. **Probabilidad de cierre por asesor / fuente de lead** — aquí tu instinto actuarial brilla: modela esto como **análisis de supervivencia** (tiempo hasta cierre, censura), no como una simple regresión logística. Es exactamente el tipo de marco cuantitativo que te diferencia y que aplica directo a tu estrategia de retención de asesores (curvas de retención, hazard rates).

Combinación ganadora: SQL/DuckDB para los hechos → modelo estadístico para la inferencia con incertidumbre (intervalos de confianza) → LLM para explicar el resultado al equipo en lenguaje claro.

---

## 21. Seguridad: la línea que separa amateur de senior

Tras el caso OpenClaw (§4.1), esto no es teórico. Un agente puede leer archivos, ejecutar comandos, instalar paquetes, mandar correos, borrar datos, filtrar secretos, modificar repos y abrir navegadores.

**Las 10 reglas de oro:**
1. Nunca des tus credenciales principales a un agente.
2. Usa cuentas de servicio y tokens dedicados.
3. Trabaja en repos de prueba primero.
4. Trabaja en ramas/worktrees.
5. Permisos mínimos (read-only por defecto).
6. No montes todo tu `$HOME` en contenedores.
7. No ejecutes `curl | bash` sin leerlo.
8. No instales MCP/skills/plugins de fuentes desconocidas; audita el código.
9. Todo cambio pasa por *diff*.
10. Toda acción destructiva requiere aprobación humana.

**Sandboxes por riesgo:**

| Riesgo | Sandbox |
|--------|---------|
| Editar código | Git branch + worktree |
| Ejecutar comandos | Contenedor Docker |
| Probar agentes autónomos (OpenClaw/Hermes) | **VM aislada** |
| Automatizar escritorio | Usuario separado o VM |
| Acceder a APIs | API keys con scope limitado |
| Datos reales | Solo lectura al inicio |
| Producción | Staging obligatorio |

**Higiene específica 2026:** escanea endpoints MCP expuestos (`/mcp`, `/sse`, bindings `0.0.0.0`) con herramientas como `mcp-scan` de Snyk; fija versiones de skills y nunca auto-update; revisa que tus configs de repo no puedan ser envenenadas (vector de RCE en Claude Code reportado por Check Point); mantén un *secrets manager* (no `.env` en repos públicos).

---

## 22. Laboratorios prácticos: experimentos medibles para volverte experto

Leer no te vuelve senior; medir sí. Esta sección son **ocho laboratorios** diseñados para correrse en tu equipo (Ryzen 7 5800X3D + RTX 3080 Ti 12 GB) y en la nube gratuita. Cada uno tiene hipótesis, montaje, métrica y criterio de éxito. La regla de oro del método experimental aplica: **cambia una variable a la vez y registra todo** (idealmente en Langfuse o en una hoja simple).

### Lab 1 — Duelo de agentes de codificación (cuál usar para qué)

**Hipótesis:** distintos agentes ganan en distintas tareas; no existe "el mejor" absoluto.

**Montaje:** toma 5 tareas reales de tus repos (ej. un endpoint FastAPI con validación, un componente Next.js, un refactor de tu scraper, un test unitario, un bug real ya resuelto que conozcas la respuesta). Ejecútalas con: (a) Claude Code, (b) Codex CLI, (c) GitHub Copilot agent, (d) un agente local con qwen2.5-coder:14b vía Cline/Aider. Mismo prompt, mismo contexto.

**Métricas:** tasa de éxito al primer intento, número de iteraciones hasta pasar tests, tokens/costo, tiempo de pared, calidad subjetiva del diff (1–5). 

**Criterio de éxito del lab:** una tabla tuya, no de internet, que diga "para X uso esto". Esperado según la evidencia: frontier (Claude/Codex) gana en tareas complejas y multiarchivo; el local gana en costo y privacidad para tareas acotadas; Copilot brilla dentro del flujo VS Code. El punto no es el resultado, es que **lo midas en tu código**.

### Lab 2 — RAG inmobiliario (el corazón de ESDATA / Oráculo Predial)

**Hipótesis:** RAG híbrido (vector + keyword/BM25) supera a vector puro en consultas con jerga técnica y nombres propios (colonias, claves catastrales, coeficientes).

**Montaje:** corpus = 50–100 documentos tuyos (fichas de propiedades, reglamentos de uso de suelo de Zapopan/Guadalajara, PDFs de planes parciales). Indexa en Qdrant (Docker local). Compara tres configuraciones: (a) vector puro con `bge-m3` o `nomic-embed-text` vía Ollama; (b) híbrido vector + BM25 con reranking; (c) híbrido + extracción de entidades a una tabla SQL para los datos numéricos (coeficientes COS/CUS, superficie).

**Métricas:** precisión@5 sobre 20 preguntas con respuesta conocida (tú haces el "ground truth"), tasa de alucinación (respuestas inventadas / total), latencia. Para medir recuperación sin tediosa anotación manual, usa **Ragas** (open source) que calcula context precision/recall y faithfulness.

**Criterio de éxito:** demostrar en tus datos que la ruta (c) — números a SQL, prosa a vectores — reduce alucinación de cifras a casi cero. Esto es exactamente la arquitectura que te conviene para Oráculo Predial: **coeficientes urbanísticos jamás deben venir de un embedding**, vienen de una tabla consultada por el agente vía tool-calling.

### Lab 3 — Sistema multiagente observable (Secretario / Crítico / Archivista)

**Hipótesis:** un equipo de agentes con roles especializados produce mejor salida que un solo agente generalista, pero con mayor costo y latencia; el punto óptimo depende de la tarea.

**Montaje:** implementa en LangGraph tu trío (ya tienes los prompts de Secretario, Crítico/Evaluador, Archivista). Tarea: generar una ficha de factibilidad de una propiedad a partir de datos crudos. Conecta **Langfuse** desde el primer minuto (es la única forma de ver qué pasa dentro del grafo). Compara contra un solo agente con el mismo objetivo.

**Métricas:** calidad final (rúbrica tuya 1–10), costo total del grafo, latencia, número de "saltos" entre nodos, y cuántas veces el Crítico efectivamente corrigió al Secretario (valor agregado real del rol). El *agent graph view* de Langfuse (beta) te deja ver el flujo visualmente.

**Criterio de éxito:** identificar si el rol Crítico paga su costo. Si en >40% de los casos mejora la salida, el patrón vale; si no, simplifica. **Medir te ahorra arquitecturas infladas.**

### Lab 4 — Bucle de auto-mejora acotado con Hermes (con malla de seguridad)

**Hipótesis:** un agente que crea y persiste sus propias skills se vuelve más rápido/barato en tareas repetidas — pero solo en dominios donde puede validar su trabajo.

**Montaje:** **VM aislada obligatoria** (ver §13 y §21). Instala Hermes Agent. Dale una tarea repetitiva y verificable de tu operación (ej. "extrae estos 8 campos de una ficha de propiedad y devuélvelos en JSON"). Córrela 20 veces sobre fichas distintas. Observa si el Curator de Hermes crea una skill y si las corridas posteriores usan menos tokens/tiempo.

**Métricas:** tokens y tiempo por corrida en el tiempo (¿baja la curva?), número de skills auto-creadas, tasa de acierto del JSON (validación con esquema). 

**Criterio de éxito:** ver con tus ojos la curva de aprendizaje (o su ausencia). Esto te enseña la lección central de §18: **la auto-mejora funciona cuando el dominio es su propio juez** (JSON validable = sí; "escribe mejor copy" = no medible, no mejora confiable). Malla de seguridad no negociable: VM sin acceso a tus credenciales reales, snapshot antes de empezar, revisión de cada skill que cree antes de confiar en ella (recuerda ClawHavoc, §4.1).

### Lab 5 — Análisis de video con VLM local (privacy-first)

**Hipótesis:** un VLM pequeño local (qwen3-vl:4b o gemma4:e4b) sobre Frigate da búsqueda en lenguaje natural "suficientemente buena" para vigilancia de oficina/propiedad sin nube.

**Montaje:** Frigate en Docker con una cámara RTSP (o un video grabado de prueba). Conecta Ollama con un VLM. Configura GenAI para descripciones de eventos. Haz 15 consultas en lenguaje natural ("persona con paquete", "auto blanco saliendo").

**Métricas:** precisión de recuperación (¿encuentra los eventos correctos?), latencia de descripción por evento, uso de VRAM (¿cabe junto a tu modelo de trabajo en 12 GB?), falsos positivos. 

**Criterio de éxito:** decidir si el edge local te basta o si necesitas API en la nube para descripciones ricas. Para tu RTX 3080 Ti, espera que un VLM 4B corra cómodo; el reto es correrlo **junto** a otros modelos — aquí practicas gestión de VRAM (descargar/cargar modelos, quantización).

### Lab 6 — Jaula de seguridad para MCP (red-team a ti mismo)

**Hipótesis:** la mayoría de los riesgos MCP/skills son detectables con higiene básica antes de que causen daño.

**Montaje:** instala 5 servidores MCP (3 confiables: GitHub, Context7, Playwright; 2 de fuente dudosa de ClawHub/registros abiertos, **en VM**). Escanea con `mcp-scan` (Snyk) y revisa qué permisos pide cada uno. Intencionalmente intenta detectar: bindings `0.0.0.0`, tokens en texto plano, skills que piden acceso a `~/.ssh` o variables de entorno.

**Métricas:** cuántos riesgos detectaste antes de ejecutar, cuántos tokens de schema consume cada server (presupuesto de contexto), latencia añadida. 

**Criterio de éxito:** un checklist propio de "qué reviso antes de instalar un MCP". Este lab te convierte en el tipo de persona que **no** termina en las estadísticas de los 135K instancias expuestas de OpenClaw.

### Lab 7 — Inferencia estadística sobre tus datos (tu ventaja actuarial)

**Hipótesis:** tu instinto actuarial + herramientas deterministas vencen a cualquier "pregúntale al LLM" para decisiones de negocio.

**Montaje:** exporta datos reales de tu operación (ventas, DOM, fuente de lead, asesor, cierre/no-cierre con fechas). En un notebook con DuckDB + statsmodels/lifelines: (a) regresión hedónica de precio; (b) **análisis de supervivencia** del tiempo-hasta-cierre por asesor y fuente (Kaplan-Meier + Cox); (c) deja que un LLM intente "estimar" las mismas cifras solo con el contexto en prosa.

**Métricas:** error del LLM vs. el cálculo real (será grande), intervalos de confianza de tu modelo, hazard ratios interpretables. 

**Criterio de éxito:** evidencia cuantificada de por qué los números van a herramientas y el LLM solo explica. Bonus: el modelo de supervivencia alimenta directo tu estrategia de retención de asesores (curvas de retención, identificación temprana de riesgo de fuga).

### Lab 8 — GraphRAG vs RAG vectorial (cuándo el grafo paga)

**Hipótesis:** GraphRAG supera al RAG vectorial **solo** en preguntas que requieren conectar múltiples hechos ("multi-hop"); para búsqueda directa es sobre-ingeniería.

**Montaje:** mismo corpus del Lab 2. Construye un grafo de conocimiento ligero (entidades: propiedad → desarrollador → zona → reglamento) con Neo4j o con la librería de GraphRAG de Microsoft (open source). Compara contra el RAG híbrido del Lab 2 en dos tipos de pregunta: directas ("¿COS de esta colonia?") y multi-hop ("¿qué propiedades del desarrollador X están en zonas con CUS mayor a 2.0 y a menos de 1 km de transporte masivo?").

**Métricas:** precisión por tipo de pregunta, costo de construcción del grafo (tiempo + tokens de extracción de entidades), mantenibilidad. 

**Criterio de éxito:** una regla clara de cuándo invertir en grafo. Para Oráculo Predial probablemente sea: **híbrido vector+SQL como base, grafo solo para las consultas relacionales complejas** que justifiquen el costo de mantenerlo.

---

### Cómo registrar todo (el meta-lab)

Monta una sola hoja o tabla (Notion/Obsidian/SQLite) con columnas: `lab`, `fecha`, `variable_cambiada`, `métrica`, `resultado`, `conclusión`. Sin registro no hay ciencia, solo anécdotas. Para los labs con agentes (1, 3, 4), Langfuse captura traza, costo y latencia automáticamente; exporta y analiza con los métodos del Lab 7. Esto cierra el círculo: **usas tu propio stack para medir tu propio stack.**


## 23. Roadmap de implementación: de cero a senior, por fases

No intentes montar todo a la vez; te quemarás y gastarás de más. Este es el orden con menor fricción, construido sobre tu principio: **primero open-source / gratis, luego óptimo costo-beneficio, y solo al final premium con costo.** Cada fase es funcional por sí sola.

### Fase 0 — Fundamentos (semana 1, costo $0)

El objetivo es tener un entorno de trabajo sólido antes de tocar agentes autónomos.

1. **Windows + WSL2 (Ubuntu)** como base. No reinstales tu equipo a Linux puro; WSL2 te da el kernel Linux donde corre todo lo serio (Docker, scripts, agentes) sin perder tu entorno Windows. (§12)
2. **VS Code** conectado a WSL2 + extensiones base.
3. **Docker Desktop** con backend WSL2. (§10)
4. **Ollama** en WSL2 con `gemma4:e4b` (ya lo tienes) y agrega `qwen2.5-coder:7b` y un modelo de embeddings (`nomic-embed-text` o `bge-m3`). (§15)
5. **Git** con repos de prueba (nunca pruebes agentes en tu repo de producción del scraper o ESDATA).

**Resultado:** entorno reproducible donde puedes correr modelos locales y contenedores. Cero costo.

### Fase 1 — Asistencia de codificación (semana 2)

1. **Capa gratis primero:** Codex CLI (open source, plan gratuito de OpenAI) y/o Gemini Code Assist mientras dure, y un agente local (Cline o Aider con qwen2.5-coder:14b) para tareas privadas/baratas. (§3, §4)
2. **Capa premium cuando lo justifiques:** Claude Code para el trabajo complejo multiarchivo. Es tu caballo de batalla cuando la calidad importa más que el costo marginal.
3. Crea tu primer **CLAUDE.md / AGENTS.md** en un repo. (§6)
4. Corre el **Lab 1** para saber, con tus datos, qué herramienta usar para qué. (§22)

**Resultado:** sabes delegar código con criterio costo/calidad, no por moda.

### Fase 2 — Contexto y memoria (semana 3)

1. Monta el **monorepo `ai-config/`** canónico con tus reglas, skills y configuración MCP versionada. (§6)
2. Instala el **starter pack de 3 MCP**: GitHub + Context7 + Playwright. Resiste la tentación de instalar 20. (§6)
3. Define tu **estándar de skills portables** (agentskills.io) para reutilizarlas entre Claude Code, Cowork y Hermes. (§6)
4. Si usas Obsidian, conéctalo como capa de conocimiento. (§8)

**Resultado:** tu contexto deja de estar disperso; una sola fuente de verdad, versionada.

### Fase 3 — RAG y datos (semanas 4–5)

1. **Qdrant en Docker** local. Indexa tu corpus inmobiliario. (§8)
2. Implementa la arquitectura **híbrida vector + SQL**: prosa a vectores, números a tablas. Este es el núcleo técnico de Oráculo Predial y de ESDATA. (§8)
3. Corre **Lab 2** (RAG híbrido) y **Lab 7** (inferencia estadística). Mide alucinación de cifras. (§22)
4. **Supabase** (free tier) si necesitas Postgres gestionado + auth para una app web. (§8, §11)

**Resultado:** un RAG que no inventa coeficientes y un pipeline de datos donde los números son confiables.

### Fase 4 — Orquestación y observabilidad (semanas 6–7)

1. **LangGraph** para tu sistema multiagente (Secretario/Crítico/Archivista). (§7)
2. **Langfuse self-hosted** (Docker, MIT) conectado desde el día uno. Nunca corras un grafo a ciegas. (§17)
3. Corre **Lab 3** (multiagente observable). Decide qué roles pagan su costo. (§22)
4. **n8n** (self-hosted, free) para automatizaciones de negocio que no requieren código (WhatsApp, correos, triggers). (§9)

**Resultado:** orquestas agentes y *ves* lo que hacen, su costo y su latencia.

### Fase 5 — Agentes autónomos (semanas 8+, con malla de seguridad)

1. **VM aislada** (Hyper-V o KVM/Proxmox). Snapshot inicial. (§13)
2. **Hermes Agent** (auto-mejora, MIT) en la VM. NUNCA en tu host con credenciales reales. (§4)
3. Corre **Lab 4** (bucle de auto-mejora acotado) y **Lab 6** (jaula de seguridad MCP). (§22)
4. Aplica las **10 reglas de oro** de seguridad religiosamente. (§21)

**Resultado:** experimentas con la frontera (agentes autónomos, auto-mejora) sin exponerte a los desastres documentados de OpenClaw.

### Fase 6 — Producción y hosting (cuando tengas algo que valga desplegar)

1. **Vercel** (Hobby → Pro) para frontends Next.js de ESDATA; Active CPU Pricing te ahorra ~90% en cargas de IA con I/O. (§11)
2. **Railway** o **VPS** ($5–10/mes) para servicios always-on (agentes daemon, n8n, Langfuse). (§11)
3. **Amazon Bedrock AgentCore** solo si llegas a escala corporativa con necesidades de cumplimiento. No empieces aquí. (§11)

**Resultado:** despliegas a costo controlado, escalando solo cuando el negocio lo pide.

### Fase 7 — Video y casos avanzados (opcional, según necesidad)

- **Frigate + VLM local** para vigilancia privacy-first de oficinas/propiedades. Corre **Lab 5**. (§19, §22)
- **GraphRAG** solo si tus consultas multi-hop lo justifican. Corre **Lab 8**. (§22)

---

### Stack final recomendado para ti (resumen ejecutivo)

| Capa | Cero costo / open-source | Óptimo costo-beneficio | Premium |
|------|--------------------------|------------------------|---------|
| **SO base** | Windows + WSL2 (Ubuntu) | igual | igual |
| **Editor** | VS Code | VS Code | + Claude Code |
| **Coding agent** | Cline/Aider + qwen2.5-coder | Codex (plan gratis) | Claude Code (Opus) |
| **Modelos locales** | Ollama: gemma4:e4b, qwen2.5-coder | igual + qwen3.5 9B | igual |
| **APIs** | Gemini AI Studio, Cerebras, Groq | router LiteLLM multi-proveedor | + Anthropic/OpenAI de pago |
| **RAG** | Qdrant (Docker) + SQL híbrido | + Supabase free | + reranking de pago |
| **Orquestación** | LangGraph + n8n self-hosted | igual | + Bedrock AgentCore |
| **Observabilidad** | Langfuse self-hosted | Langfuse Cloud Hobby | Langfuse Pro |
| **Agentes autónomos** | Hermes (VM) | igual | — |
| **Hosting** | Railway free / VPS $5 | Vercel Pro + VPS | Bedrock / Enterprise |
| **Contexto** | monorepo `ai-config/` + MCP×3 | igual | igual |

**Tu equipo (Ryzen 7 5800X3D + RTX 3080 Ti 12 GB)** es más que suficiente para todo lo local de este manual: corre cómodamente modelos hasta ~14B en Q4, un VLM de 4B, y varias VMs ligeras. El cuello de botella no será tu hardware sino tu disciplina de seguridad y de medición.


## 24. Apéndices

### A. Checklist: instalar y compartir un MCP server

1. Identifica la necesidad real (¿qué herramienta le falta al agente?). No instales "por si acaso".
2. Verifica la fuente: repositorio oficial, estrellas, mantenimiento reciente, quién lo publica.
3. Revisa los permisos que pide y el transporte (local `stdio` es más seguro que remoto `0.0.0.0`).
4. Audita el código si la fuente no es de primera línea (especialmente registros abiertos de skills).
5. Agrégalo a tu configuración versionada en `ai-config/` (no lo instales suelto y lo olvides).
6. Confirma cuántos tokens de schema consume; mantén el total de servers entre 3 y 6.
7. Escanea con `mcp-scan` (Snyk) antes de confiar.
8. Documenta en tu monorepo qué hace y por qué lo tienes.

### B. Checklist: crear una skill portable

1. Crea la carpeta `<nombre>/` con un `SKILL.md`.
2. En el frontmatter, define `name` y `description` claros (la `description` es lo que el agente lee para decidir si la usa — sé específico).
3. Escribe instrucciones en prosa, con ejemplos y criterios de "terminado".
4. Si incluye scripts o recursos, ponlos en la misma carpeta.
5. Apégate al estándar abierto (agentskills.io) para que funcione en Claude Code, Cowork y Hermes.
6. Versiona la skill en `ai-config/`. Nunca la dejes en auto-update.
7. Pruébala en un repo de prueba antes de usarla en producción.

### C. Checklist: clonar y usar un repositorio de configuración

1. Lee el README completo y revisa la fecha del último commit.
2. Clona en un directorio de pruebas, no en tu proyecto real.
3. Revisa qué archivos toca (`.claude/`, hooks, comandos) antes de copiarlos.
4. Los **hooks** ejecutan comandos automáticamente: léelos línea por línea (vector de RCE).
5. Adapta los nombres y rutas a tu stack (Python/FastAPI + Next.js).
6. Integra solo lo que entiendas; borra lo demás.

### D. Comandos clave (referencia rápida)

```bash
# Ollama
ollama pull gemma4:e4b              # descargar modelo
ollama list                         # ver modelos instalados
ollama ps                           # ver qué está cargado en VRAM/RAM
ollama run qwen2.5-coder:7b         # chat interactivo
ollama rm <modelo>                  # liberar espacio

# Docker
docker compose up -d                # levantar stack en segundo plano
docker compose logs -f <servicio>   # ver logs en vivo
docker ps                           # contenedores corriendo
docker stats                        # uso de CPU/RAM por contenedor
docker compose down                 # apagar stack

# WSL2 (desde PowerShell)
wsl --list --verbose                # ver distros y estado
wsl --shutdown                      # reiniciar WSL2
wsl -d Ubuntu                       # entrar a Ubuntu

# Git seguro para agentes
git worktree add ../prueba-rama rama-experimental   # aislar trabajo del agente
git diff                            # revisar TODO cambio antes de aceptar
git switch -c feature/x             # rama nueva para experimentos

# Seguridad MCP
npx mcp-scan                        # escanear servidores MCP (Snyk)
```

### E. Glosario senior (los términos que debes dominar)

- **Agente:** sistema que recibe un objetivo, planea, usa herramientas en bucle y verifica resultados, no solo responde texto.
- **MCP (Model Context Protocol):** estándar abierto (gobernado por la Linux Foundation desde dic-2025) para conectar agentes con herramientas y datos vía JSON-RPC.
- **Skill:** carpeta con instrucciones (y opcionalmente scripts) que un agente carga para realizar una tarea específica; portable entre herramientas si sigue el estándar abierto.
- **Tool-calling / function-calling:** capacidad del modelo de invocar funciones externas con argumentos estructurados; es lo que convierte un chat en un agente.
- **RAG:** recuperación de información relevante para inyectarla al contexto antes de generar; reduce alucinación y da respuestas fundamentadas.
- **RAG híbrido:** combina búsqueda vectorial (significado) con keyword/BM25 (coincidencia exacta) y reranking.
- **Embedding:** representación numérica del significado de un texto; base de la búsqueda vectorial.
- **Quantización (Q4_K_M, etc.):** comprimir los pesos del modelo para que use menos VRAM a costa de algo de precisión.
- **VRAM:** memoria de la GPU; el límite real para correr modelos locales (tú tienes 12 GB).
- **Contexto / ventana de contexto:** cuánto texto puede "ver" el modelo de una vez (tokens).
- **Orquestación:** coordinar múltiples agentes/pasos (LangGraph, n8n, CrewAI).
- **Observabilidad:** instrumentar para ver trazas, costo, latencia y errores (Langfuse).
- **Auto-mejora:** sistema que modifica sus propias instrucciones/skills/código y valida la mejora; confiable solo cuando el dominio es su propio juez.
- **Sandbox:** entorno aislado (contenedor, VM, usuario separado) para contener el daño de un agente.
- **Reward hacking:** cuando un sistema optimiza la métrica en vez del objetivo real; riesgo central de la auto-mejora.
- **Edge AI:** procesar IA localmente en el dispositivo (cámara, PC) en vez de la nube; privacidad y baja latencia.

### F. Referencias y fuentes (para verificar y profundizar)

Todo lo verificable de este manual proviene de fuentes que puedes consultar directamente. Por dominio:

- **Documentación oficial de productos:** los sitios de documentación de Anthropic (Claude Code, Claude API), OpenAI (Codex, plataforma), Google (Antigravity, Gemini, Gemma en su portal de IA) y Microsoft (GitHub Copilot). Para detalles de productos de Anthropic que cambian rápido (límites, precios, features), consulta `docs.claude.com` y `support.claude.com` directamente, ya que mi conocimiento tiene fecha de corte.
- **Estándares abiertos:** el sitio del Model Context Protocol y su gobernanza bajo la Linux Foundation / AAIF; el estándar de skills portables en `agentskills.io`.
- **Proyectos open-source (GitHub):** los repositorios de Hermes Agent (Nous Research), OpenClaw (Peter Steinberger), Frigate (blakeblackshear), Langfuse, n8n, Qdrant, LangGraph, Aider, Cline, OpenHands, y los repos de plugins de Anthropic (`anthropics/knowledge-work-plugins`). Revisa estrellas, issues y fecha de último commit como señal de salud.
- **Ciencia de auto-mejora (papers, ICLR 2026):** Darwin Gödel Machine (Sakana AI / UBC, repo `jennyzzt/dgm`), ShinkaEvolve (Sakana, open source), OpenEvolve (reimplementación abierta de AlphaEvolve). Búscalos por nombre en arXiv y sus repos.
- **Seguridad:** los avisos de CVE para OpenClaw (busca el identificador CVE-2026-25253), los reportes de OX Security y Check Point sobre vulnerabilidades en SDKs de MCP, y la herramienta `mcp-scan` de Snyk.
- **APIs gratuitas:** los portales de Google AI Studio, Cerebras, Groq, Mistral, OpenRouter, NVIDIA NIM, SambaNova y GitHub Models tienen sus propios límites publicados; verifícalos al momento de usar porque cambian.

**Nota de método:** las cifras de fechas, versiones, precios y límites son volátiles. Antes de tomar una decisión de inversión o arquitectura, confirma el dato en la fuente primaria. Lo que no pude verificar con suficiente confianza está marcado en el texto como [NO VERIFICADO].

---

## Cierre

Este manual te da el mapa completo: la tesis (sistema operativo de agentes), las herramientas (IDEs, CLIs, agentes autónomos), la plomería (MCP, skills, RAG, memoria), la infraestructura (Docker, VMs, hosting, hardware), la ciencia (auto-mejora, inferencia estadística) y la disciplina (seguridad, observabilidad, medición). 

La diferencia entre saber esto y ser senior es una sola: **correr los laboratorios y medir en tus propios datos.** Empieza por la Fase 0, no instales todo de golpe, aísla los agentes autónomos en VMs, y mide cada decisión. Tu ventaja no es tener el modelo más grande —es tu criterio cuantitativo (actuarial) aplicado a un dominio que dominas (el inmobiliario de Guadalajara) sobre una infraestructura que ahora entiendes de punta a punta.

*Documento de referencia técnica. Fecha de elaboración: 17 de junio de 2026. Datos volátiles sujetos a verificación en fuente primaria.*

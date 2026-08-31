# REPO_MENU — Menú portable de la biblioteca de repositorios

> Generado: 2026-08-25 · 212 repos curados · Documento 100% para IA.
> COPIA esta carpeta (`menu_portable/`) a la raíz de tu proyecto y
> referencia este archivo desde tu AGENTS.md / system prompt.

---

## INSTRUCCIONES PARA EL AGENTE (léeme entero, soy corto)

Eres un agente que debe elegir qué repositorios instalar/usar para un
proyecto concreto. Tienes un menú curado de **212 repos** de IA y
automatización. Objeto: gastar MÍNIMOS tokens y NO visitar la web.

PROTOCOLO (en orden):

0. **Si el usuario ya describió un proyecto concreto**, parte de las
   `recipes` que coincidan con el producto; no empieces por repos sueltos.
1. **No leas todo.** Este archivo basta para preseleccionar.
2. **Filtra** candidatos por `cat`, `tags`, `role`, `exec`, `setup`, `prov`
   y palabras de `one` (resumen de una línea).
3. **Desempata** con `alt`: si ya elegiste un repo, **descarta sus `alt`**
   (cumplen la misma función, no necesitas dos).
4. **Combina** con `recipes` si el proyecto es un flujo end-to-end.
5. **Considera la herramienta** del usuario (Claude Code, Antigravity,
   Codex, Grok, Deepseek) con la tabla de abajo y el campo opcional
   `agent_tools`. Solo importa para repos `role=skill/directory`.
6. **Solo para finalistas (<8):** abre `REPO_MENU_cats/NN-*.md` para
   desc, `choose_if`, `avoid_if`, `combines_with` y el comando de
   instalación derivado.
7. **Instalación:** comando marcado `+` seguro · `~` verificar nombre ·
   `?` solo clone + README.

REGLA CLAVE — herramienta de código ≠ modelo en ejecución:
- El AGENTE/IDE con que CONSTRUYES (Claude Code, Antigravity, Codex…)
  solo importa para repos `role=skill/directory` (catálogos de skills).
- El LLM que tu APP llama EN EJECUCIÓN es el campo `prov`; se configura
  por env vars. La mayoría de repos runtime son AGNÓSTICOS al agente.

LEYENDA de columnas del índice:
`role`: P=plataforma R=runtime L=librería S=skill D=catálogo A=app
`exec`: loc=local cld=cloud hyb=híbrido · `setup`: E=easy M=medium H=heavy
`inst`: +=comando seguro ~=verificar ?=solo clone
`tags` / `prov` / `tools` (`agent_tools`): solo si el repo los declara
`alt`: repos sustitutos (elige uno)

---

## Repos específicos por herramienta de código

| Herramienta | Repos que le sirven |
|---|---|
| Claude Code | `claude-plugins-official`, `awesome-claude-code`, `superpowers`, `skills`, `agent-toolkit`, `n8n-skills`, `geo-seo-claude`, `agency-agents` |
| Antigravity | `antigravity-awesome-skills`, `awesome-agent-skills`, `prompt-master` |
| Codex | `antigravity-awesome-skills`, `awesome-agent-skills`, `marketingskills`, `taste-skill` |
| Grok | Sin repos específicos; úsalo como proveedor LLM en runtime. |
| Deepseek | `deepseek-coder` |

## Recetas (stacks end-to-end listos)

Si el proyecto es un PRODUCTO (no una pieza suelta), parte de una
receta y ajusta. Cada receta lista los repos en orden de uso.

### Bot de WhatsApp con IA
**Meta:** atención/ventas automatizada por WhatsApp con un agente LLM.  
**Stack:** `evolution-api` → `n8n` → `n8n-mcp` → `n8n-skills` → `chatwoot` → `novu`
**Cómo:** evolution-api recibe/envía mensajes vía webhook; n8n enruta y llama al LLM; chatwoot centraliza cuando entra un agente humano.

### Pipeline de Reels / video corto
**Meta:** convertir contenido en video corto con voz y subtítulos.  
**Stack:** `whisperx` → `supertonic` → `tts` → `comfyui` → `fooocus` → `real-esrgan` → `moviepy` → `remotion` → `lossless-cut`
**Cómo:** [videofy_minimal](#-videofy_minimal) puede orquestar el flujo simple; remotion/moviepy escalan a variantes programáticas.

### Agente de research profundo
**Meta:** investigación citada y estructurada a partir de la web.  
**Stack:** `gpt-researcher` → `deer-flow` → `firecrawl` → `crawl4ai` → `browser-use` → `markitdown` → `langfuse`

### Workspace privado local soberano
**Meta:** asistente todo-en-uno sin fuga de datos.  
**Stack:** `odysseus` → `open-notebook` → `ecc` → `mem0`

### Análisis de repos grandes
**Meta:** que un asistente entienda una base de código enorme barato.  
**Stack:** `codegraph` → `graphify` → `graphrag` → `gitnexus`

### Marketing de agencia
**Meta:** operar campañas y contenido a escala.  
**Stack:** `marketingskills` → `agency-agents` → `mautic` → `listmonk` → `posthog` → `metabase` → `open-generative-ai`

### Web app moderna con IA
**Meta:** construir frontend pulido rápido.  
**Stack:** `open-design` → `plasmic` → `tailwindcss` → `heroui` → `gsap` → `motion` → `threejs` → `swr` → `echarts` → `uplot`

### Construir una app/servidor MCP
**Meta:** exponer datos o herramientas propias a asistentes.  
**Stack:** `mcp-use` → `mcp` → `servers` → `awesome-mcp-servers`

### Documentos → presentaciones
**Meta:** pasar texto/informes a slides editables.  
**Stack:** `markitdown` → `ppt-master` → `revealjs`

---

## ÍNDICE COMPACTO (1 línea por repo)

Formato: `id` [role|exec|setup|inst] — one — tags:… — prov:… — tools:… — alt:…

### Sin categoría

- `cli` [A|loc|E|~] — GitHub CLI (gh): pull requests, issues y el resto de GitHub desde la terminal. — tags: typescript
- `tools` [L|loc|M|?] — Utilidades locales del workspace de Alexandria; no es un producto de IA para instalar.

### 1. Automatización, Mensajería & CRM (17)
Detalle: `REPO_MENU_cats/01-automatizaci-n-mensajer-a-crm.md`

- `activepieces` [R|hyb|M|~] — Plataforma open source de automatización tipo Zapier, auto-hospedable, con piezas y flujos visuales. — tags: automation,docker,javascript,javascript-typescript,typescript — alt: n8n
- `appsmith` [P|loc|M|~] — Organizations build custom applications like dashboards, admin panels, customer 360, IT automation, and servic — tags: automation,docker,javascript,postgres,typescript
- `browser-use` [P|loc|M|~] — 1. Direct your favorite coding agent (Cursor, Claude Code, etc) to Agents.md. — tags: automation,docker,python,typescript
- `budibase` [P|loc|M|~] — Budibase is an open-source operations platform that saves engineers 100s of hours building Agents, Apps and Au — tags: automation,docker,javascript,javascript-typescript,postgres,typescript
- `chatwoot` [L|hyb|M|~] — Chatwoot is the modern, open-source, and self-hosted customer support platform designed to help businesses del — tags: automation,docker,javascript,javascript-typescript,typescript
- `evolution-api` [A|hyb|M|~] — Open-source REST API for WhatsApp and multi-channel messaging — part of the Evolution Foundation ecosystem. — tags: automation,docker,javascript,javascript-typescript,postgres,typescript
- `huginn` [D|hyb|M|+] — Huginn is a system for building agents that perform automated tasks for you online. They can read the web, wat — tags: automation,docker,javascript,javascript-typescript,postgres,typescript
- `listmonk` [D|hyb|M|+] — listmonk is a standalone, self-hosted, newsletter and mailing list manager. It is fast, feature-rich, and pack — tags: automation,docker,postgres,typescript
- `mautic` [P|loc|M|~] — Request a trial · Self-host/download · Community channels. — tags: automation,javascript,javascript-typescript,postgres,python,typescript
- `n8n` [P|loc|M|~] — n8n is a workflow automation platform that gives technical teams the flexibility of code with the speed of no- — tags: automation,docker,javascript,javascript-typescript,langchain,python,typescript — alt: activepieces,huginn
- `n8n-io` [P|loc|M|~] — n8n is a workflow automation platform that gives technical teams the flexibility of code with the speed of no- — tags: automation,docker,javascript,javascript-typescript,langchain,python,typescript
- `n8n-mcp` [P|loc|M|~] — A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to n8n node docume — tags: automation,docker,javascript,javascript-typescript,langchain,mcp,python,typescript
- `novu` [L|hyb|M|~] — One API and one unified conversation model to connect your products and your agents to every channel your user — tags: automation,javascript,javascript-typescript,react,typescript
- `openevolve` [L|loc|M|~] — Turn your LLMs into autonomous code optimizers that discover breakthrough algorithms. — tags: automation,docker,python,typescript
- `openwa` [P|hyb|M|~] — OpenWA is a free, open-source WhatsApp API Gateway designed for developers who need full control over their me — tags: docker,javascript,javascript-typescript,postgres,python,react,typescript
- `twenty-main` [R|loc|M|~] — Website · Documentation · Roadmap · Discord · Figma. — tags: automation,docker,javascript,javascript-typescript,postgres,react,typescript
- `whatsapp-agentkit` [D|cld|M|+] — Construye tu propio agente de WhatsApp con inteligencia artificial en menos de 30 minutos. No necesitas saber  — tags: agents,automation,docker,fastapi,javascript,postgres,python,typescript

### 2. Skills, Prompts & Guías de Agente (30)
Detalle: `REPO_MENU_cats/02-skills-prompts-gu-as-de-agente.md`

- `agent-toolkit` [S|loc|M|+] — Opinionated skills shared by @leonardocouy for improving daily work efficiency with Claude Code. Skills are pa — tags: agents,python,react,typescript — tools: claude-code
- `andrej-karpathy-skills` [S|hyb|M|+] — > Check out my new project Multica — an open-source platform for running and managing coding agents with reusa — tags: skills,typescript
- `antigravity-awesome-skills` [S|loc|E|+] — > Installable GitHub library of 1,682+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI, Antigrav — tags: agents,javascript,javascript-typescript,postgres,python,react,skills,typescript — tools: antigravity,codex
- `arcads-claude-code` [S|loc|M|+] — Skills de Claude Code/Cursor para generar videos e imágenes de marketing con Arcads. — tags: skills,video,image — tools: claude-code
- `autoresearch` [P|loc|H|~] — One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, — tags: python,typescript
- `awesome-agent-skills` [S|cld|H|+] — Lista curada a mano de skills para agentes de código, sin catálogos generados por IA. — tags: docker,fastapi,javascript,langchain,multimedia,postgres,python,react — tools: antigravity,codex
- `browser-harness` [S|loc|M|+] — Connect an LLM directly to your real browser with a thin, editable CDP harness. For browser tasks where you ne — tags: postgres,python,typescript
- `context-engineering` [R|loc|M|~] — > "Context engineering is the delicate art and science of filling the context window with just the right infor — tags: postgres,python,react,typescript
- `geo-seo-claude` [S|hyb|M|+] — (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews) while maintaining traditional SEO foundations. — tags: python,typescript — tools: claude-code
- `guia` [S|hyb|H|+] — Catálogo operativo de los 156 repositorios locales del workspace, diseñado para entender, comparar, elegir y c — tags: comfy,frontend,multimedia,typescript,whisper
- `hermes-agent` [S|loc|M|+] — The self-improving AI agent built by Nous Research. It's the only agent with a built-in learning loop — it cre — tags: agents,docker,javascript,postgres,python,typescript
- `humanizer` [S|loc|M|+] — Clone directly into Claude Code's skills directory:. — tags: typescript
- `last30days-skill` [S|hyb|M|+] — This README tracks the current v3 pipeline. The runtime skill spec lives in skills/last30days/SKILL.md, which  — tags: javascript,python,react,skills,typescript
- `llm-council` [P|cld|M|+] — The idea of this repo is that instead of asking a question to your favorite LLM provider (e.g. OpenAI GPT 5.1, — tags: fastapi,javascript,postgres,python,react,typescript
- `marketingskills` [S|cld|H|+] — A collection of AI agent skills focused on marketing tasks. Built for technical marketers and founders who wan — tags: agents,postgres,skills,typescript — tools: codex
- `multica` [S|loc|M|+] — The open-source managed agents platform. — tags: docker,javascript,javascript-typescript,postgres,react,typescript
- `n8n-skills` [S|hyb|M|+] — Skills de Claude Code para diseñar workflows n8n usando el servidor n8n-mcp. — tags: docker,javascript,langchain,postgres,python,skills,typescript — tools: claude-code
- `nanogpt` [L|cld|H|~] — Update Nov 2025 nanoGPT has a new and improved cousin called nanochat. It is very likely you meant to use/find — tags: javascript,postgres,python,typescript
- `notebooklm-py` [S|hyb|M|+] — A Comprehensive NotebookLM Skill & Unofficial Python API. Full programmatic access to NotebookLM's features—in — tags: fastapi,javascript,postgres,python,typescript
- `open-generative-ai` [S|hyb|H|+] — > The free, open-source alternative to AI Video Platforms. Generate AI images and videos using 200+ state-of-t — tags: comfy,docker,javascript,javascript-typescript,multimedia,python,react,typescript
- `openmontage` [S|loc|H|+] — Turn your AI coding assistant into a full video production studio. Describe what you want in plain language —  — tags: javascript,multimedia,postgres,python,react,typescript,whisper
- `playwright-cli` [S|loc|E|+] — CLI de Playwright con skills para que un agente controle el navegador desde la terminal. — tags: javascript,javascript-typescript,python,typescript
- `prompt-master` [S|hyb|H|+] — A Claude skill that writes the accurate prompts for any AI tool. Zero tokens or credits wasted. Full context a — tags: comfy,javascript,postgres,python,react,skills,typescript — tools: antigravity
- `skills-remotion` [S|loc|M|+] — This is an internal package and has no documentation. — tags: javascript,javascript-typescript,skills
- `skillspector` [S|loc|M|+] — Security scanner for AI agent skills. Detect vulnerabilities, malicious patterns, and security risks before in — tags: docker,javascript,python,skills,typescript
- `stitch-sdk` [S|hyb|M|+] — Generate UI screens from text prompts and extract their HTML and screenshots programmatically. — tags: javascript,javascript-typescript,typescript
- `stop-slop` [S|hyb|M|+] — AI writing has patterns. Predictable phrases, structures, rhythms. This skill teaches Claude (or any LLM) to c — tags: typescript
- `superpowers` [S|loc|M|+] — Superpowers is a complete software development methodology for your coding agents, built on top of a set of co — tags: javascript,javascript-typescript,typescript — tools: claude-code
- `taste-skill` [S|loc|M|+] — Skills portables para mejorar layout, tipografía, motion y spacing de UIs hechas con IA. — tags: postgres,react,skills,typescript — tools: codex
- `ui-ux-pro-max-skill` [S|loc|M|+] — If you find this useful, consider supporting the project:. — tags: frontend,javascript,python,react,skills,typescript

### 3. Frameworks & Orquestación de Agentes (47)
Detalle: `REPO_MENU_cats/03-frameworks-orquestaci-n-de-agentes.md`

- `ag2` [P|hyb|M|~] — AG2 was evolved from AutoGen. Fully open-sourced. We invite collaborators from all organizations to contribute — tags: automation,docker,python,react,typescript
- `agent-protocol` [D|hyb|M|+] — Especificación de APIs agnósticas a framework para servir agentes LLM en producción. — tags: agents,automation,fastapi,langchain,postgres,python,typescript
- `agent-reach` [R|hyb|M|~] — Capa de acceso a modelos y APIs para agentes: elige, instala y verifica el proveedor por ti. — tags: automation,javascript,multimedia,postgres,python,typescript,whisper
- `agents-towards-production` [S|hyb|H|+] — The open-source playbook for turning AI agents into real-world products. — tags: agents,automation,docker,fastapi,langchain,python,typescript
- `autogen` [R|loc|M|~] — Framework multiagente de Microsoft (modo mantenimiento; el sucesor vive en agent-framework). — tags: agents,automation,javascript,postgres,python,typescript
- `awesome-claude-code` [S|cld|M|+] — A delightfully curated collection of the finest of resources for the most excellent of agents, Claude Code, by — tags: automation,python,typescript — tools: claude-code
- `awesome-dataviz` [D|loc|M|+] — A curated list of awesome open-source data visualizations frameworks, libraries and software. Inspired by awes — tags: automation,javascript,postgres,python,react,typescript
- `awesome-langgraph` [D|loc|M|+] — > The definitive index of frameworks, templates, and real-world projects for teams that want to build, observe — tags: automation,docker,fastapi,javascript,javascript-typescript,langchain,postgres,python
- `awesome-mcp-servers` [D|loc|H|+] — A curated list of awesome Model Context Protocol (MCP) servers. — tags: automation,comfy,docker,fastapi,javascript,langchain,mcp,multimedia
- `codebase-memory-mcp` [R|hyb|M|~] — The fastest and most efficient code intelligence engine for AI coding agents. Full-indexes an average reposito — tags: automation,docker,javascript,mcp,python,typescript
- `computer-use-preview` [L|cld|M|~] — Código y guía de Gemini Computer Use para que un modelo controle el escritorio. — tags: automation,python,react,typescript — prov: google
- `crewai` [R|hyb|M|~] — Fast and Flexible Multi-Agent Automation Framework. — tags: automation,langchain,postgres,python,typescript
- `dash` [P|loc|M|~] — Built on top of Plotly.js, React and Flask, Dash ties modern UI elements like dropdowns, sliders, and graphs d — tags: automation,javascript,postgres,python,react,typescript
- `deepagents` [L|loc|M|~] — Deep Agents is an open source agent harness — an opinionated agent that runs out of the box. Extend, override, — tags: agents,automation,javascript,langchain,python,typescript
- `deeptutor` [A|hyb|M|~] — Tutor personalizado de largo plazo: un agente que estudia contigo y recuerda el progreso. — tags: automation,docker,fastapi,javascript,langchain,postgres,python,react
- `deer-flow` [S|hyb|M|+] — > On February 28th, 2026, DeerFlow claimed the 🏆 #1 spot on GitHub Trending following the launch of version 2. — tags: automation,docker,javascript,langchain,python,typescript
- `defending-code-reference-harness` [L|hyb|M|~] — A reference implementation for autonomous vulnerability discovery and remediation with Claude, based on our le — tags: automation,docker,python,typescript
- `dify` [P|hyb|M|~] — Dify is an open-source LLM app development platform. Its intuitive interface combines AI workflow, RAG pipelin — tags: automation,docker,javascript,javascript-typescript,postgres,python,react,typescript
- `ecc` [A|hyb|M|~] — > Official sources only. Install ECC only from verified channels: the GitHub repository github.com/affaan-m/EC — tags: automation,docker,fastapi,javascript,postgres,python,react,typescript
- `flowise` [P|loc|M|~] — Builder visual low-code para agentes y flujos LLM, auto-hospedable. — tags: automation,docker,javascript,javascript-typescript,react,typescript
- `gpt-researcher` [S|hyb|M|+] — GPT Researcher the first open deep research agent designed for both web and local research on any given task. — tags: automation,docker,fastapi,javascript,langchain,python,react,typescript
- `guardrails` [P|loc|M|~] — > LATEST RELEASE / DEVELOPMENT VERSION: The develop branch tracks the latest top of tree development. The late — tags: automation,docker,javascript,langchain,python,react,typescript
- `headroom` [P|loc|M|~] — 60–95% fewer tokens · library · proxy · MCP · 6 algorithms · local-first · reversible. — tags: automation,docker,javascript,langchain,postgres,python,typescript
- `hyperframes` [S|hyb|M|+] — HyperFrames is an open-source framework for turning HTML, CSS, media, and seekable animations into determinist — tags: agents,automation,docker,javascript,javascript-typescript,multimedia,python,react
- `langchain` [R|loc|M|~] — LangChain is a framework for building agents and LLM-powered applications. It helps you chain together interop — tags: agents,automation,langchain,python,typescript
- `langflow` [P|hyb|M|~] — Langflow is a powerful platform for building and deploying AI-powered agents and workflows. It provides develo — tags: automation,docker,javascript,python,typescript
- `langfuse` [P|loc|M|~] — Langfuse uses GitHub Discussions for Support and Feature Requests. — tags: automation,docker,fastapi,javascript,javascript-typescript,langchain,python,react
- `langgraph-supervisor-py` [R|loc|M|~] — > Note: We now recommend using the supervisor pattern directly via tools rather than this library for most use — tags: automation,langchain,postgres,python,react,typescript
- `langgraphjs` [R|loc|M|~] — LangGraph para JavaScript/TypeScript: orquestación de agentes con estado. — tags: automation,javascript,javascript-typescript
- `loop-engineering` [S|loc|M|+] — > Stop prompting. Design the loop. Get a score. — tags: automation,frontend,javascript,javascript-typescript,postgres,skills,typescript
- `mcp-use` [P|hyb|M|~] — to build MCP Apps for ChatGPT / Claude & MCP Servers for AI Agents. — tags: automation,javascript,langchain,mcp,python,react,typescript
- `mercury-agent` [S|loc|M|+] — Remembers what matters. Asks before it acts. Runs 24/7 from CLI, Telegram, or Web. 31 built-in tools, Kanban b — tags: automation,javascript,javascript-typescript,postgres,react,typescript
- `nemo-agent-toolkit` [D|loc|M|+] — NVIDIA NeMo Agent Toolkit adds intelligence to AI agents across any framework—enhancing speed, accuracy, and d — tags: automation,fastapi,javascript,langchain,python,react,typescript
- `nemoclaw` [S|loc|M|+] — NVIDIA NemoClaw is an open source reference stack for running supported AI agents more safely inside NVIDIA Op — tags: agents,automation,docker,javascript,javascript-typescript,langchain,postgres,python
- `open-swe` [P|loc|M|~] — Elite engineering orgs like Stripe, Ramp, and Coinbase are building their own internal coding agents — Slackbo — tags: agents,automation,docker,javascript,langchain,postgres,python,react
- `openclaw` [L|loc|M|~] — OpenClaw is a personal AI assistant that runs on your devices and meets you in the channels you already use. — tags: automation,docker,javascript,javascript-typescript,postgres,typescript
- `openhands` [P|hyb|M|~] — Run OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local, remote, and cloud backend — tags: agents,automation,docker,javascript,python,typescript
- `openscreen` [P|hyb|M|~] — > OpenScreen is now archived and no longer maintained. For continued maintenance and development, a community- — tags: automation,javascript,javascript-typescript,postgres,typescript
- `playwright` [R|hyb|E|~] — Playwright is a framework for web automation and testing. It drives Chromium, Firefox, and WebKit with a singl — tags: automation,javascript,javascript-typescript,postgres,python,typescript
- `ponytail` [L|hyb|M|~] — ~54% less code (up to 94%) &middot; ~20% cheaper &middot; ~27% faster &middot; 100% safe. — tags: automation,fastapi,javascript,javascript-typescript,python,react,typescript
- `repomix` [L|loc|E|~] — Warp, built for coding with multiple AI agents Available for MacOS, Linux, & Windows. — tags: automation,docker,javascript,javascript-typescript,postgres,python,react,typescript
- `ruflo` [R|loc|M|~] — > Agent = Model + Harness. The model writes; the harness gives it tools, memory, loops, sandboxes, and control — tags: automation,docker,javascript,javascript-typescript,postgres,react,typescript
- `sandbox` [L|hyb|M|~] — Sandbox all-in-one para ejecutar agentes con aislamiento de sistema y red. — tags: agents,automation,docker,javascript,javascript-typescript,langchain,python,react
- `scrapling` [L|hyb|M|~] — Scrapling is an adaptive Web Scraping framework that handles everything from a single request to a full-scale  — tags: automation,docker,javascript,postgres,python,scraping,typescript
- `t3code` [A|cld|M|+] — Superficie de control para agentes en tu máquina: app móvil, web y escritorio Electron. — tags: agents,javascript,javascript-typescript,react,typescript
- `tooljet` [A|hyb|M|~] — ToolJet is the open-source foundation of ToolJet AI - the AI-native platform for building and deploying intern — tags: agents,automation,docker,javascript,javascript-typescript,postgres,python,typescript
- `turbovec` [D|loc|H|+] — turbovec is a Rust vector index with Python bindings, built on Google Research's TurboQuant algorithm — a data — tags: automation,langchain,python,typescript

### 4. Scraping, Búsqueda & Research Web (13)
Detalle: `REPO_MENU_cats/04-scraping-b-squeda-research-web.md`

- `archivebox` [P|hyb|M|~] — ArchiveBox is a self-hosted app that lets you preserve content from websites in a variety of formats. — tags: docker,javascript,postgres,python,typescript
- `crawl4ai` [A|hyb|M|~] — 🚀 Crawl4AI Cloud API — Closed Beta (Launching Soon) Reliable, large-scale web extraction, now built to be dras — tags: docker,fastapi,javascript,postgres,python,react,scraping,typescript
- `crawlee` [R|hyb|M|~] — Crawlee covers your crawling and scraping end-to-end and helps you build reliable scrapers. Fast. — tags: docker,javascript,javascript-typescript,python,react,scraping,typescript
- `crawlee-python` [L|hyb|M|~] — Crawlee covers your crawling and scraping end-to-end and helps you build reliable scrapers. Fast. — tags: javascript,python,react,scraping,typescript
- `firecrawl` [L|loc|M|~] — The API to search, scrape, and interact with the web at scale. 🔥 The web context API to find sources, extract  — tags: docker,javascript,python,scraping,typescript
- `how-to-train-your-gpt` [R|loc|M|~] — > A guide to building a world-class language model from absolute scratch. Taught like you're five. Built like  — tags: python,typescript
- `instaloader` [L|loc|M|~] — Descarga fotos, videos y metadatos de Instagram desde perfiles, hashtags y stories. — tags: python,typescript,vision
- `llm-scraper` [P|cld|E|+] — > LLM Scraper was updated to version 2.0. — tags: javascript,javascript-typescript,scraping,typescript
- `odysseus` [S|hyb|H|+] — > dev is the default branch and gets the newest changes first. Use main if you want the more curated branch. — tags: agents,docker,javascript,postgres,python,typescript
- `scrapegraph-ai` [P|hyb|M|~] — Scraping con grafos LLM: describes qué extraer y el sistema recorre la página. — tags: docker,javascript,langchain,python,scraping,typescript
- `scrapely` [L|hyb|E|~] — some example web pages and the data to be extracted, scrapely constructs a parser for all similar pages. — tags: javascript,python,scraping,typescript
- `scrapy` [L|loc|M|~] — Framework Python de crawling y scraping a gran escala. — tags: python,scraping
- `snscrape` [D|loc|M|+] — snscrape is a scraper for social networking services (SNS). It scrapes things like user profiles, hashtags, or — tags: python,scraping,typescript

### 5. MCP & Conectividad (14)
Detalle: `REPO_MENU_cats/05-mcp-conectividad.md`

- `awesome-mcp-clients` [D|hyb|M|+] — A curated list of awesome Model Context Protocol (MCP) clients. — tags: docker,javascript,langchain,mcp,postgres,python,react,typescript
- `claude-plugins-official` [P|cld|M|+] — A curated directory of high-quality plugins for Claude Code. — tags: typescript — tools: claude-code
- `context7` [R|loc|E|~] — MCP que inyecta documentación y ejemplos actualizados de librerías en el prompt del LLM. — tags: mcp,docs,agents
- `davinci-resolve-mcp` [R|hyb|M|~] — Servidor MCP que deja a un agente controlar DaVinci Resolve Studio por su API de scripting. — tags: mcp,video,agents
- `github-mcp-server` [P|loc|M|~] — The GitHub MCP Server connects AI tools directly to GitHub's platform. This gives AI agents, assistants, and c — tags: docker,javascript,mcp,python,react,typescript
- `graphify` [L|loc|H|~] — Type /graphify in your AI coding assistant and it maps your entire project — code, docs, PDFs, images, videos  — tags: docker,javascript,multimedia,postgres,python,typescript,whisper
- `langchain-mcp-adapters` [L|hyb|E|~] — Adaptadores que hacen herramientas MCP usables desde LangChain y LangGraph. — tags: javascript,langchain,mcp,python,typescript
- `mcp` [D|hyb|M|+] — This repository contains a list of Google's official Model Context Protocol (MCP) servers, guidance on how to  — tags: mcp,postgres,typescript
- `mcp-neo4j` [D|loc|M|+] — These MCP servers are a part of the Neo4j Labs program. They are developed and maintained by the Neo4j Field G — tags: mcp,typescript
- `metabase` [P|loc|M|~] — The easiest way to get started with Metabase is to sign up for a free trial of Metabase Cloud. — tags: docker,javascript,javascript-typescript,postgres,react,typescript
- `notebooklm-mcp-cli` [P|hyb|M|~] — Programmatic access to Google NotebookLM — via command-line interface (CLI) or Model Context Protocol (MCP) se — tags: mcp,postgres,python,react,typescript
- `opencut` [P|hyb|M|~] — OpenCut is being rewritten from the ground up. What's coming:. — tags: typescript
- `public-apis` [D|hyb|M|+] — The Public APIs repository is manually curated by community members like you and folks working at APILayer. It — tags: docker,javascript,postgres,python,react,typescript
- `servers` [D|loc|M|+] — This repository is a collection of reference implementations for the Model Context Protocol (MCP), as well as  — tags: javascript,javascript-typescript,postgres,python,typescript

### 6. Memoria, LLM Ops & Observabilidad (5)
Detalle: `REPO_MENU_cats/06-memoria-llm-ops-observabilidad.md`

- `agentmemory` [R|hyb|M|~] — Persistent memory for Claude Code, GitHub Copilot CLI, Cursor, Gemini CLI, Codex CLI, Hermes, OpenClaw, pi, Op — tags: agents,docker,javascript,javascript-typescript,postgres,python,typescript
- `engram` [R|hyb|M|~] — One brain. Local or cloud. Agent-agnostic, single binary, zero dependencies. — tags: memory,mcp,agents
- `loguru` [P|loc|M|~] — Did you ever feel lazy about configuring a logger and used print() instead?... I did, yet logging is fundament — tags: python,typescript
- `mem0` [L|hyb|M|~] — Capa de memoria persistente para agentes y apps LLM, con API y almacén vectorial. — tags: docker,javascript,postgres,python,typescript
- `mempalace` [D|hyb|M|+] — > Beware of impostor sites. MemPalace has no other official websites. The only official sources are this GitHu — tags: docker,postgres,python,react,typescript

### 7. Inteligencia de Código, Datos & Entrenamiento (10)
Detalle: `REPO_MENU_cats/07-inteligencia-de-c-digo-datos-entrenamiento.md`

- `awesome-bigdata` [D|loc|M|+] — A curated list of awesome big data frameworks, resources and other awesomeness. Inspired by awesome-php, aweso — tags: docker,javascript,postgres,python,react,typescript
- `codegraph` [L|loc|M|~] — Indexa repositorios grandes como grafo de código y responde consultas estructurales. — tags: fastapi,javascript,javascript-typescript,postgres,python,react,typescript
- `data-science-ipython-notebooks` [D|loc|M|+] — Colección de notebooks IPython de data science, machine learning y estadística. — tags: postgres,python,typescript
- `deepseek-coder` [L|loc|H|~] — DeepSeek Coder is composed of a series of code language models, each trained from scratch on 2T tokens, with a — tags: docker,javascript,python,typescript — tools: deepseek
- `echarts` [L|loc|E|~] — Apache ECharts is a free, powerful charting and visualization library offering easy ways to add intuitive, int — tags: javascript,javascript-typescript,typescript
- `gitnexus` [R|hyb|E|~] — ⚠️ Important Notice: GitNexus has NO official cryptocurrency, token, or coin. Any token/coin using the GitNexu — tags: docker,javascript,javascript-typescript,langchain,python,react,typescript
- `llm.c` [A|cld|H|+] — LLMs in simple, pure C/CUDA with no need for 245MB of PyTorch or 107MB of cPython. Current focus is on pretrai — tags: javascript,python,typescript
- `openai-python` [P|hyb|M|~] — The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.9+ application. — tags: javascript,postgres,python,typescript
- `swe-bench` [L|loc|M|~] — SWE-bench is a benchmark for evaluating large language models on real world software issues collected from Git — tags: docker,python,typescript
- `timesfm` [L|loc|M|~] — Modelo fundacional de Google Research para forecasting de series temporales. — tags: docker,python,typescript

### 8. Workspaces de IA Local & Notebooks (2)
Detalle: `REPO_MENU_cats/08-workspaces-de-ia-local-notebooks.md`

- `hermes-desktop` [A|loc|M|~] — App de escritorio para el agente Hermes: chat, skills y operación local. — tags: automation,javascript,javascript-typescript,postgres,python,react,typescript
- `open-notebook` [P|hyb|M|~] — An open source, privacy-focused alternative to Google's Notebook LM! — tags: docker,fastapi,langchain,postgres,python,react,typescript

### 9. Diseño, UI & Frontend (30)
Detalle: `REPO_MENU_cats/09-dise-o-ui-frontend.md`

- `agency-agents` [S|loc|H|+] — > A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas, from whimsy inje — tags: multimedia,postgres,python,react,typescript,whisper — tools: claude-code
- `daily-stock-analysis` [L|hyb|M|~] — 产品预览 · 功能特性 · 快速开始 · 推送效果 · 文档中心 · 完整指南. — tags: docker,fastapi,postgres,python,typescript
- `design.md` [D|loc|M|+] — A DESIGN.md file combines machine-readable design tokens (YAML front matter) with human-readable design ration — tags: frontend,javascript,javascript-typescript,typescript
- `gradio` [S|hyb|M|+] — Gradio is an open-source Python package that allows you to quickly build a demo or web application for your ma — tags: fastapi,javascript,postgres,python,react,typescript
- `graphrag` [L|loc|H|~] — The GraphRAG project is a data pipeline and transformation suite that is designed to extract meaningful, struc — tags: python,typescript
- `gsap` [R|loc|M|~] — GSAP is a framework-agnostic JavaScript animation library that turns developers into animation superheroes. Bu — tags: javascript,javascript-typescript,postgres,react,typescript
- `heroui` [L|loc|M|~] — Librería de componentes React lista para usar, alternativa empaquetada a shadcn/ui. — tags: frontend,javascript,javascript-typescript,react
- `impeccable` [S|hyb|E|+] — > Quick start: From your project root, run npx impeccable install, then run /impeccable init inside your AI co — tags: javascript,javascript-typescript,typescript
- `llmfit` [A|loc|H|~] — > New: Community Leaderboard — Browse real-world performance data from actual users. Press b to see measured t — tags: docker,javascript,postgres,python,typescript
- `magicui` [R|hyb|M|~] — Visit https://magicui.design/docs to view the documentation. — tags: frontend,javascript,javascript-typescript,react,typescript
- `mirofish` [R|hyb|M|~] — A Simple and Universal Swarm Intelligence Engine, Predicting Anything. — tags: docker,javascript,javascript-typescript,postgres,python,typescript
- `motion` [L|hyb|H|~] — Librería de animación open source para JavaScript, React y Vue. — tags: javascript,javascript-typescript,react,typescript
- `nanochat` [A|loc|H|~] — nanochat is the simplest experimental harness for training LLMs. It is designed to run on a single GPU node, t — tags: javascript,multimedia,python,typescript,whisper
- `nemotron` [A|hyb|H|~] — Open and efficient models for agentic AI. Training recipes, deployment guides, and use-case examples for the N — tags: postgres,python,typescript
- `normalize.css` [L|loc|E|~] — CSS que normaliza inconsistencias de estilos por defecto entre navegadores. — tags: javascript,javascript-typescript,typescript
- `open-design` [R|loc|M|~] — > 🔥 Open Design 0.10.0 is here: the all-in-one Agentic design workspace. The whole craft now lives in one wind — tags: agents,docker,frontend,javascript,javascript-typescript,postgres,react,typescript
- `penpot` [P|loc|M|~] — Penpot is the open-source design platform for teams that build digital products at scale. — tags: docker,frontend,javascript,javascript-typescript,postgres,python,react,typescript
- `plasmic` [L|loc|M|~] — Build beautiful apps and websites incredibly fast. — tags: docker,javascript,javascript-typescript,react,typescript
- `posthog` [S|loc|M|+] — PostHog is an all-in-one, open source platform for building successful products. — tags: docker,javascript,python,react,typescript
- `react-three-fiber` [L|loc|M|~] — react-three-fiber is a React renderer for threejs. — tags: javascript,javascript-typescript,postgres,react,typescript
- `real-esrgan` [L|loc|H|~] — 🔥 RealESRGANx4plusanime6B for anime images (动漫插图模型). Please see [animemodel]. — tags: multimedia,postgres,python,typescript
- `skills` [S|loc|M|+] — My agent skills that I use every day to do real engineering - not vibe coding. — tags: javascript,javascript-typescript,skills,typescript — tools: claude-code
- `skills-emil` [S|loc|M|+] — For designers and engineers to help them build better user interfaces. — tags: frontend,skills,typescript
- `stitch-skills` [S|loc|M|+] — A collection of agent skills and plugins for Google Stitch, following the Agent Skills open standard. Compatib — tags: frontend,react,skills,typescript
- `swr` [L|loc|M|~] — SWR is a React Hooks library for data fetching. — tags: javascript,javascript-typescript,react,typescript
- `tailwindcss` [P|hyb|M|~] — For full documentation, visit tailwindcss.com. — tags: javascript,javascript-typescript
- `three.js` [L|loc|H|~] — The aim of the project is to create an easy-to-use, lightweight, cross-browser, general-purpose 3D library. — tags: javascript,javascript-typescript,typescript
- `ui` [P|loc|M|~] — A set of beautifully designed components that you can customize, extend, and build on. Start here then make it — tags: frontend,javascript,javascript-typescript,typescript — alt: heroui
- `vllm` [L|loc|M|~] — 🔥 We have built a vLLM website to help you get started with vLLM. Please visit vllm.ai to learn more. For even — tags: python,typescript
- `youtube2webpage` [L|loc|M|~] — Youtube-to-Webpage is a Perl script to create a webpage from a Youtube video with a transcript generated from  — tags: postgres,typescript

### 10. Analítica & Visualización (2)
Detalle: `REPO_MENU_cats/10-anal-tica-visualizaci-n.md`

- `streamlit` [P|loc|E|~] — A faster way to build and share data apps. — tags: python,typescript
- `uplot` [L|hyb|M|~] — uPlot is a fast, memory-efficient Canvas 2D-based chart for plotting time series, lines, areas, ohlc & bars. — tags: javascript,javascript-typescript,python,react,typescript

### 11. Generación de Imagen & Visión (18)
Detalle: `REPO_MENU_cats/11-generaci-n-de-imagen-visi-n.md`

- `comfyui` [R|hyb|H|~] — ComfyUI is the AI creation engine for visual professionals who demand control over every model, every paramete — tags: comfy,docker,frontend,javascript,python,react,typescript
- `comfyui-ipadapter-plus` [L|loc|H|~] — ComfyUI reference implementation for IPAdapter models. — tags: comfy,frontend,javascript,postgres,python,typescript
- `controlnet` [L|loc|H|~] — ControlNet 1.1 is released. Those new models will be merged to this repo after we make sure that everything is — tags: python,typescript
- `cosmos` [R|loc|H|~] — Modelos NVIDIA Cosmos de world modeling y generación visual/simulación. — tags: docker,postgres,python,typescript
- `deep-live-cam` [A|hyb|M|~] — This deepfake software is designed to be a productive tool for the AI-generated media industry. It can assist  — tags: multimedia,postgres,python,typescript,vision
- `diffusers` [L|loc|M|~] — 🤗 Diffusers is the go-to library for state-of-the-art pretrained diffusion models for generating images, audio — tags: postgres,python,typescript
- `face-recognition` [L|loc|M|~] — Recognize and manipulate faces from Python or from the command line with the world's simplest face recognition — tags: docker,postgres,python,typescript
- `fooocus` [S|loc|H|+] — Fooocus presents a rethinking of image generator designs. The software is offline, open source, and free, whil — tags: comfy,docker,javascript,python,typescript
- `gfpgan` [L|loc|M|~] — 1. :boom: Updated online demo: 1. Colab Demo for GFPGAN ; (Another Colab Demo for the original paper model). — tags: javascript,postgres,python,typescript
- `invokeai` [R|loc|M|~] — Invoke is a leading creative engine built to empower professionals and enthusiasts alike. Generate and create  — tags: docker,javascript,python,react,typescript
- `litellm` [P|hyb|M|~] — Open Source AI Gateway for 100+ LLMs. Self-hosted. Enterprise-ready. Call any LLM in OpenAI format. — tags: docker,javascript,postgres,python,typescript
- `liveportrait` [L|loc|H|~] — Jianzhu Guo 1† &emsp; Dingyun Zhang 1,2 &emsp; Xiaoqiang Liu 1 &emsp;. — tags: comfy,javascript,postgres,python,typescript
- `luxtts` [D|loc|H|+] — LuxTTS is an lightweight zipvoice based text-to-speech model designed for high quality voice cloning and reali — tags: comfy,javascript,multimedia,python,typescript
- `nemo` [R|loc|M|~] — Checkout our HuggingFace🤗 collection for the latest open weight checkpoints and demos! — tags: docker,python,typescript
- `sd-webui-controlnet` [L|loc|M|~] — The WebUI extension for ControlNet and other injection-based SD controls. — tags: frontend,postgres,python,typescript,vision
- `stable-diffusion-webui` [S|loc|M|+] — A web interface for Stable Diffusion, implemented using Gradio library. — tags: frontend,javascript,postgres,python,typescript,vision
- `tts` [L|loc|H|~] — 📣 ⓍTTS fine-tuning code is out. Check the example recipes. - 📣 ⓍTTS can now stream with. — tags: docker,python,typescript
- `unlimited-ocr` [L|hyb|H|~] — OCR de Baidu para parsear documentos largos en una sola pasada. — tags: vision,ocr,docs

### 12. Audio, Voz & Video (16)
Detalle: `REPO_MENU_cats/12-audio-voz-video.md`

- `faster-whisper` [R|cld|H|+] — faster-whisper is a reimplementation of OpenAI's Whisper model using CTranslate2, which is a fast inference en — tags: docker,fastapi,multimedia,python,typescript,whisper
- `ffmpeg` [D|loc|M|+] — FFmpeg is a collection of libraries and tools to process multimedia content such as audio, video, subtitles an — tags: typescript
- `fluxer` [P|hyb|M|~] — > We apologise for the brief delay in open-source releases. We paused after spam waves created safety concerns — tags: javascript,javascript-typescript,typescript
- `lossless-cut` [A|loc|M|~] — Thanks to my supporters and everyone who purchased LosslessCut! — tags: javascript,javascript-typescript,multimedia,postgres,python,typescript
- `moviepy` [L|loc|M|~] — > MoviePy recently upgraded to v2.0, introducing major breaking changes. You can consult the last v1 docs here — tags: docker,postgres,python,typescript
- `omnivoice-studio` [A|hyb|H|~] — Studio TTS open source, alternativa a ElevenLabs para clonación y generación de voz. — tags: docker,fastapi,javascript,multimedia,python,react,typescript,whisper
- `remotion` [L|hyb|M|~] — Framework para crear videos de forma programática con React. — tags: javascript,javascript-typescript,multimedia,react,typescript
- `remotion-superpowers` [P|cld|H|+] — A free, open-source Claude Code plugin that turns Remotion into a full video production studio — by Dojo Codin — tags: javascript,multimedia,python,react,typescript,whisper
- `supertonic` [L|hyb|H|~] — Supertonic is a lightning-fast, on-device multilingual text-to-speech system designed for local inference with — tags: javascript,multimedia,python,typescript
- `vibevoice` [D|hyb|M|+] — 2026-03-06: 🚀 VibeVoice ASR is now part of a Transformers release ! You can now use our speech recognition mod — tags: multimedia,postgres,python,typescript
- `video-use` [S|hyb|M|+] — Drop raw footage in a folder, chat with Claude Code, get final.mp4 back. Works for any content — talking heads — tags: multimedia,python,typescript
- `videofy-minimal` [P|hyb|M|~] — Videofy Minimal is a local tool for turning news articles into short videos for digital signage screens. — tags: docker,fastapi,javascript,multimedia,python,react,typescript
- `voxcpm` [L|hyb|H|~] — 👋 Join our community for discussion and support! — tags: comfy,docker,fastapi,javascript,postgres,python,typescript
- `wan2gp` [P|loc|H|~] — WanGP is a one-stop super app for the best open source generative models across video, image, audio, and text- — tags: comfy,docker,multimedia,postgres,python,react,typescript,vision
- `whisper` [L|cld|H|~] — Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and i — tags: multimedia,postgres,python,typescript,whisper
- `whisperx` [L|hyb|H|~] — If you’re looking for a transcription API for meetings, consider checking out Recall.ai's Meeting Transcriptio — tags: multimedia,python,typescript,whisper

### 13. Documentos & Presentaciones (6)
Detalle: `REPO_MENU_cats/13-documentos-presentaciones.md`

- `markitdown` [D|loc|E|+] — > MarkItDown performs I/O with the privileges of the current process. Like open() or requests.get(), it will a — tags: docker,postgres,python,typescript
- `pdf-inspector` [L|hyb|M|~] — Librería Rust para clasificar PDFs (texto vs escaneado) y extraer texto con posiciones. — tags: javascript,python,typescript
- `pdfcraft` [A|loc|M|~] — Editor PDF en el navegador: fusionar, partir, comprimir y editar sin subir archivos. — tags: docker,javascript,javascript-typescript,postgres,react,typescript
- `pdfding` [A|loc|M|~] — Gestor, visor y editor de PDFs auto-hospedable, pensado para ser mínimo y rápido. — tags: docker,frontend,javascript,python,typescript
- `ppt-master` [L|hyb|H|~] — This project is kept free and open source with the support of PackyCode , APIKEY.FUN , RunAPI , YouYun ZhiSuan — tags: postgres,python,typescript
- `reveal.js` [R|hyb|M|~] — reveal.js is an open source HTML presentation framework. It enables anyone with a web browser to create beauti — tags: javascript,javascript-typescript,typescript

---

## Cómo instalar (resumen de la lógica de derivación)

- `role=skill/directory` → copiar a la carpeta de skills de tu agente.
- `role=platform/runtime/app` + Docker → `git clone && docker compose up`.
- `role=library` Python → `pip install <pkg>` / `uv add <pkg>` (verifica nombre).
- `role=library` Node → `npm install <pkg>` (verifica nombre).
- `exec=cloud` → servicio gestionado: API key, no se clona.
- Marca `?` → solo `git clone` es seguro; revisa el README del repo.

> Si un comando marcado `~` falla, busca el nombre real del paquete en
> pypi.org / npmjs.com o clona el repo y lee su manifest.

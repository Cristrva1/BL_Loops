# 3. Frameworks & Orquestación de Agentes — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `ag2`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,python,react,typescript

**Qué es:** AG2 was evolved from AutoGen. Fully open-sourced. We invite collaborators from all organizations to contribute.
**Stack:** python, typescript, react, docker
**Repo:** https://github.com/ag2ai/ag2.git

**Instalación** [~]: `git clone https://github.com/ag2ai/ag2.git && cd ag2 && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** construyes multiagente serio en Python
**Evita si:** te basta un agente único o quieres orquestación visual.
**Combina con:** `langchain`, `langfuse`

## `agent-protocol`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,automation,fastapi,langchain,postgres,python,typescript

**Qué es:** Agent Protocol intenta estandarizar cómo se expone un agente (run, I/O, estado) sin atarse a un framework. Es un spec/directorio, no un runtime completo.
**Stack:** python, typescript, postgres, fastapi, langchain
**Repo:** https://github.com/langchain-ai/agent-protocol.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/agent-protocol/). Si necesitas el código: git clone https://github.com/langchain-ai/agent-protocol.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres agent protocol
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `agent-reach`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,javascript,multimedia,postgres,python,typescript,whisper

**Qué es:** Agent-Reach estabiliza cómo un agente se conecta a proveedores LLM. La idea es que el canal de acceso pueda cambiar sin que reescribas el resto del stack.
**Stack:** python, typescript, javascript, postgres, whisper
**Repo:** https://github.com/Panniantong/Agent-Reach.git

**Instalación** [~]: `git clone https://github.com/Panniantong/Agent-Reach.git && cd Agent-Reach && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres 给你的 ai agent 一键装上互联网能力
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `agents-towards-production`
role=skill · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=agents,automation,docker,fastapi,langchain,python,typescript

**Qué es:** The open-source playbook for turning AI agents into real-world products.
**Stack:** python, typescript, docker, fastapi, langchain
**Repo:** https://github.com/NirDiamant/agents-towards-production.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/agents-towards-production/). Si necesitas el código: git clone https://github.com/NirDiamant/agents-towards-production.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** vas a producción con agentes y necesitas el ciclo completo
**Evita si:** solo experimentas localmente o buscas skills, no tutoriales.
**Combina con:** `langfuse`, `ag2`

## `autogen`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=agents,automation,javascript,postgres,python,typescript

**Qué es:** AutoGen orquesta conversaciones entre agentes LLM. Está en mantenimiento; para trabajo nuevo revisa el sucesor oficial antes de adoptarlo como runtime.
**Stack:** python, typescript, javascript, postgres
**Repo:** https://github.com/microsoft/autogen.git

**Instalación** [~]: `git clone https://github.com/microsoft/autogen.git && cd autogen && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres autogen [![maintenance mode](https://img.shields.io/badge/status-maintenance%20m
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `awesome-claude-code`
role=skill · exec=cloud · setup=medium · mcp=False · prov=— · tags=automation,python,typescript · tools=claude-code

**Qué es:** The old ways have come and gone. It's time to embrace the next phase. The previous Table of Contents was no longer fit for purpose, so a new organizational system is being prepared. Thanks to everyone who has contributed to and supported this repo, be ye human or machine.
**Stack:** python, typescript
**Repo:** https://github.com/hesreallyhim/awesome-claude-code.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-claude-code/). Si necesitas el código: git clone https://github.com/hesreallyhim/awesome-claude-code.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** vives en Claude Code y quieres exprimirlo
**Evita si:** usas otro asistente (no aplica).
**Combina con:** `claude-plugins-official`, `superpowers`

## `awesome-dataviz`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,postgres,python,react,typescript

**Qué es:** A curated list of awesome open-source data visualizations frameworks, libraries and software. Inspired by awesome-python and originally created by fasouto.
**Stack:** python, typescript, javascript, react, postgres
**Repo:** https://github.com/hal9ai/awesome-dataviz.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-dataviz/). Si necesitas el código: git clone https://github.com/hal9ai/awesome-dataviz.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** buscas opciones de visualización y aún no has elegido
**Evita si:** ya elegiste tu librería y solo necesitas usarla.
**Combina con:** `echarts`, `awesome-bigdata`

## `awesome-langgraph`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,fastapi,javascript,javascript-typescript,langchain,postgres,python

**Qué es:** 🦜🕸️ Awesome LangGraph & LangChain Ecosystem !Awesome !Last Updated.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, postgres, fastapi, langchain
**Repo:** https://github.com/vonzosten/awesome-LangGraph.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-LangGraph/). Si necesitas el código: git clone https://github.com/vonzosten/awesome-LangGraph.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** construyes con LangGraph y quieres patrones de referencia
**Evita si:** no usas ese ecosistema.
**Combina con:** `langchain`

## `awesome-mcp-servers`
role=directory · exec=local · setup=heavy · mcp=True · prov=— · tags=automation,comfy,docker,fastapi,javascript,langchain,mcp,multimedia

**Qué es:** A curated list of awesome Model Context Protocol (MCP) servers.
**Stack:** python, typescript, javascript, react, docker, postgres, fastapi, langchain, whisper, comfy
**Repo:** https://github.com/punkpeye/awesome-mcp-servers.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-mcp-servers/). Si necesitas el código: git clone https://github.com/punkpeye/awesome-mcp-servers.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** buscas antes de construir
**Evita si:** ya sabes que necesitas uno a medida y no te vale ninguno listado.
**Combina con:** `mcp-use`, `servers`

## `codebase-memory-mcp`
role=runtime · exec=hybrid · setup=medium · mcp=True · prov=— · tags=automation,docker,javascript,mcp,python,typescript

**Qué es:** The fastest and most efficient code intelligence engine for AI coding agents. Full-indexes an average repository in milliseconds, the Linux kernel (28M LOC, 75K files) in 3 minutes. Answers structural queries in under 1ms. Ships as a single static binary for macOS, Linux, and Windows — download, run `install`, done.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/DeusData/codebase-memory-mcp.git

**Instalación** [~]: `git clone https://github.com/DeusData/codebase-memory-mcp.git && cd codebase-memory-mcp && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** —
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `computer-use-preview`
role=library · exec=cloud · setup=medium · mcp=False · prov=google · tags=automation,python,react,typescript

**Qué es:** Preview de Gemini Computer Use: el modelo ve la pantalla y opera UI. Requiere API de Google y no es un agente genérico de código.
**Stack:** python, typescript, react
**Repo:** https://github.com/google-gemini/computer-use-preview.git

**Instalación** [~]: `pip install computer-use-preview   (o: uv add computer-use-preview)`
_Nombre PyPI puede diferir de 'computer-use-preview'; verifica en pypi.org._

**Elige si:** quieres computer use preview
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `crewai`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,langchain,postgres,python,typescript

**Qué es:** Fast and Flexible Multi-Agent Automation Framework.
**Stack:** python, typescript, postgres, langchain
**Repo:** https://github.com/crewAIInc/crewAI.git

**Instalación** [~]: `git clone https://github.com/crewAIInc/crewAI.git && cd crewAI && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres velocidad y un modelo mental simple de "equipo"
**Evita si:** necesitas control de bajo nivel o orquestación muy custom.
**Combina con:** `langchain`, `mem0`

## `dash`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,postgres,python,react,typescript

**Qué es:** Dash is the most downloaded, trusted Python framework for building ML & data science web apps*.
**Stack:** python, typescript, javascript, react, postgres
**Repo:** https://github.com/plotly/dash.git

**Instalación** [~]: `git clone https://github.com/plotly/dash.git && cd dash && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres dashboards productivos en Python con control del frontend
**Evita si:** prefieres prototipos ultrarrápidos ([streamlit](#-streamlit)).
**Combina con:** `streamlit`, `echarts`

## `deepagents`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=agents,automation,javascript,langchain,python,typescript

**Qué es:** Deep Agents is an open source agent harness — an opinionated agent that runs out of the box. Extend, override, or replace any piece.
**Stack:** python, typescript, javascript, langchain
**Repo:** https://github.com/langchain-ai/deepagents.git

**Instalación** [~]: `pip install deepagents   (o: uv add deepagents)`
_Nombre PyPI puede diferir de 'deepagents'; verifica en pypi.org._

**Elige si:** quieres the batteries-included agent harness.
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `deeptutor`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,fastapi,javascript,langchain,postgres,python,react

**Qué es:** DeepTutor es un sistema de tutoría con agentes para aprendizaje continuo. Encaja como producto educativo, no como orquestador genérico.
**Stack:** python, typescript, javascript, react, docker, postgres, fastapi, langchain
**Repo:** https://github.com/HKUDS/DeepTutor.git

**Instalación** [~]: `git clone https://github.com/HKUDS/DeepTutor.git && cd DeepTutor && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres deeptutor: lifelong personalized tutoring
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `deer-flow`
role=skill · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,langchain,python,typescript

**Qué es:** > On February 28th, 2026, DeerFlow claimed the 🏆 #1 spot on GitHub Trending following the launch of version 2. Thanks a million to our incredible community — you made this happen! 💪🔥.
**Stack:** python, typescript, javascript, docker, langchain
**Repo:** https://github.com/bytedance/deer-flow.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/deer-flow/). Si necesitas el código: git clone https://github.com/bytedance/deer-flow.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres un orquestador completo y extensible
**Evita si:** buscas algo minimalista o sin Docker.
**Combina con:** `gpt-researcher`, `firecrawl`

## `defending-code-reference-harness`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,python,typescript

**Qué es:** A reference implementation for autonomous vulnerability discovery and remediation with Claude, based on our learnings from partnering with security teams at several organizations since launching Claude Mythos Preview. For a write up of these learnings along with best practices, see the accompanying blog post (also avail.
**Stack:** python, typescript, docker
**Repo:** https://github.com/anthropics/defending-code-reference-harness.git

**Instalación** [~]: `pip install defending-code-reference-harness   (o: uv add defending-code-reference-harness)`
_Nombre PyPI puede diferir de 'defending-code-reference-harness'; verifica en pypi.org._

**Elige si:** quieres defending code reference harness
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `dify`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,python,react,typescript

**Qué es:** Dify is an open-source LLM app development platform. Its intuitive interface combines AI workflow, RAG pipeline, agent capabilities, model management, observability features (including Opik, Langfuse, and Arize Phoenix) and more, letting you quickly go from prototype to production. Here's a list of the core features:.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/langgenius/dify.git

**Instalación** [~]: `git clone https://github.com/langgenius/dify.git && cd dify && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres una app IA completa autoalojada
**Evita si:** solo necesitas una librería o un prototipo puntual.
**Combina con:** `langflow`, `flowise`

## `ecc`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,fastapi,javascript,postgres,python,react,typescript

**Qué es:** Official sources only. Install ECC only from verified channels: the GitHub repository github.com/affaan-m/ECC, the npm packages `ecc-universal` and `ecc-agentshield`, the GitHub App, the plugin slug `ecc@ecc`, and the project website ecc.tools.
**Stack:** python, typescript, javascript, react, docker, postgres, fastapi
**Repo:** https://github.com/affaan-m/ECC.git

**Instalación** [~]: `git clone https://github.com/affaan-m/ECC.git && cd ECC && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** ejecutas agentes con acceso real a tu máquina y necesitas contención
**Evita si:** solo haces prompts de chat sin ejecución de código.
**Combina con:** `openhands`, `sandbox`, `hermes-agent`

## `flowise`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,react,typescript

**Qué es:** Flowise es un constructor visual de cadenas y agentes LLM. Encaja si quieres prototipar orquestación con nodos, no si necesitas un runtime embebido en tu código.
**Stack:** javascript/typescript, typescript, javascript, react, docker
**Repo:** https://github.com/FlowiseAI/Flowise.git

**Instalación** [~]: `git clone https://github.com/FlowiseAI/Flowise.git && cd Flowise && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres un prototipo visual ya, en stack JS
**Evita si:** necesitas plataforma completa con RAG/observabilidad ([dify](#-dify)).
**Combina con:** `dify`, `langflow`

## `gpt-researcher`
role=skill · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,fastapi,javascript,langchain,python,react,typescript

**Qué es:** GPT Researcher the first open deep research agent designed for both web and local research on any given task.
**Stack:** python, typescript, javascript, react, docker, fastapi, langchain
**Repo:** https://github.com/assafelovic/gpt-researcher.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/gpt-researcher/). Si necesitas el código: git clone https://github.com/assafelovic/gpt-researcher.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** necesitas research profundo citado
**Evita si:** solo quieres una respuesta corta o un chat simple.
**Combina con:** `firecrawl`, `browser-use`, `research profundo`

## `guardrails`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,langchain,python,react,typescript

**Qué es:** > LATEST RELEASE / DEVELOPMENT VERSION: The develop branch tracks the latest top of tree development. The latest released version is 0.21.0.
**Stack:** python, typescript, javascript, react, docker, langchain
**Repo:** https://github.com/NVIDIA-NeMo/Guardrails.git

**Instalación** [~]: `git clone https://github.com/NVIDIA-NeMo/Guardrails.git && cd Guardrails && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres nvidia nemo guardrails library
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `headroom`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,langchain,postgres,python,typescript

**Qué es:** 60–95% fewer tokens · library · proxy · MCP · 6 algorithms · local-first · reversible.
**Stack:** python, typescript, javascript, docker, postgres, langchain
**Repo:** https://github.com/headroomlabs-ai/headroom.git

**Instalación** [~]: `git clone https://github.com/headroomlabs-ai/headroom.git && cd headroom && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** te quedas sin contexto en sesiones largas
**Evita si:** tus prompts ya caben holgados o la pérdida de detalle por resumen es inaceptable.
**Combina con:** `context-engineering`, `codegraph`

## `hyperframes`
role=skill · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,javascript-typescript,multimedia,python,react

**Qué es:** HyperFrames is an open-source framework for turning HTML, CSS, media, and seekable animations into deterministic MP4 videos. Use it locally with the CLI, from AI coding agents with skills, or as the rendering core behind hosted authoring workflows.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker
**Repo:** https://github.com/heygen-com/hyperframes.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/hyperframes/). Si necesitas el código: git clone https://github.com/heygen-com/hyperframes.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** generas animación por frames con control por código
**Evita si:** prefieres video en React con reloj integrado ([remotion](#-remotion)) o edición visual.
**Combina con:** `remotion`

## `langchain`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=agents,automation,langchain,python,typescript

**Qué es:** LangChain is a framework for building agents and LLM-powered applications. It helps you chain together interoperable components and third-party integrations to simplify AI application development — all while future-proofing decisions as the underlying technology evolves.
**Stack:** python, typescript, langchain
**Repo:** https://github.com/langchain-ai/langchain.git

**Instalación** [~]: `git clone https://github.com/langchain-ai/langchain.git && cd langchain && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres la base estándar con máximas integraciones
**Evita si:** prefieres mínima abstracción o un solo proveedor sin cambiar.
**Combina con:** `langflow`, `langfuse`, `litellm`

## `langflow`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,python,typescript

**Qué es:** Langflow is a powerful platform for building and deploying AI-powered agents and workflows. It provides developers with both a visual authoring experience and built-in API and MCP servers that turn every workflow into a tool that can be integrated into applications built on any framework or stack.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/langflow-ai/langflow.git

**Instalación** [~]: `git clone https://github.com/langflow-ai/langflow.git && cd langflow && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** prefieres construir en visual sobre LangChain
**Evita si:** quieres todo en código o no usas LangChain.
**Combina con:** `langchain`, `dify`

## `langfuse`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,fastapi,javascript,javascript-typescript,langchain,python,react

**Qué es:** Langfuse uses GitHub Discussions for Support and Feature Requests.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, fastapi, langchain
**Repo:** https://github.com/langfuse/langfuse.git

**Instalación** [~]: `git clone https://github.com/langfuse/langfuse.git && cd langfuse && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** operas agentes en serio y necesitas trazas/costes/eval
**Evita si:** haces prototipos triviales o no quieres operar el backend.
**Combina con:** `langchain`, `litellm`, `ag2`

## `langgraph-supervisor-py`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=automation,langchain,postgres,python,react,typescript

**Qué es:** > Note: We now recommend using the supervisor pattern directly via tools rather than this library for most use cases. The tool-calling approach gives you more control over context engineering and is the recommended pattern in the LangChain multi-agent guide. See our supervisor tutorial for a step-by-step guide. We're making this library compatible with LangChain 1.
**Stack:** python, typescript, react, postgres, langchain
**Repo:** https://github.com/langchain-ai/langgraph-supervisor-py.git

**Instalación** [~]: `git clone https://github.com/langchain-ai/langgraph-supervisor-py.git && cd langgraph-supervisor-py && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres 🤖 langgraph multi-agent supervisor
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `langgraphjs`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript

**Qué es:** Implementación TypeScript de LangGraph. Sirve para construir, gestionar y desplegar agentes de larga duración con grafos de estado en Node o el navegador.
**Stack:** javascript/typescript, javascript
**Repo:** https://github.com/langchain-ai/langgraphjs.git

**Instalación** [~]: `git clone https://github.com/langchain-ai/langgraphjs.git && cd langgraphjs && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** quieres libs/langgraph-core/readme.md
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `loop-engineering`
role=skill · exec=local · setup=medium · mcp=False · prov=— · tags=automation,frontend,javascript,javascript-typescript,postgres,skills,typescript

**Qué es:** > Stop prompting. Design the loop. Get a score.
**Stack:** javascript/typescript, typescript, javascript, postgres
**Repo:** https://github.com/cobusgreyling/loop-engineering.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/loop-engineering/). Si necesitas el código: git clone https://github.com/cobusgreyling/loop-engineering.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres loop engineering
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `mcp-use`
role=platform · exec=hybrid · setup=medium · mcp=True · prov=— · tags=automation,javascript,langchain,mcp,python,react,typescript

**Qué es:** to build MCP Apps for ChatGPT / Claude & MCP Servers for AI Agents.
**Stack:** python, typescript, javascript, react, langchain
**Repo:** https://github.com/mcp-use/mcp-use.git

**Instalación** [~]: `git clone https://github.com/mcp-use/mcp-use.git && cd mcp-use && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** construyes un servidor MCP propio y quieres productividad
**Evita si:** solo buscas usar uno ya hecho ([awesome-mcp-servers](#-awesome-mcp-servers)) o necesitas control a nivel spec.
**Combina con:** `mcp`, `awesome-mcp-servers`, `app mcp`

## `mercury-agent`
role=skill · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,postgres,react,typescript

**Qué es:** Remembers what matters. Asks before it acts. Runs 24/7 from CLI, Telegram, or Web. 31 built-in tools, Kanban boards, extensible skills, SQLite-backed Second Brain memory.
**Stack:** javascript/typescript, typescript, javascript, react, postgres
**Repo:** https://github.com/cosmicstack-labs/mercury-agent.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/mercury-agent/). Si necesitas el código: git clone https://github.com/cosmicstack-labs/mercury-agent.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres soul-driven ai agent with permission-hardened tools, token budgets, and multi-channel acce
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `nemo-agent-toolkit`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=automation,fastapi,javascript,langchain,python,react,typescript

**Qué es:** NVIDIA NeMo Agent Toolkit adds intelligence to AI agents across any framework—enhancing speed, accuracy, and decision-making through enterprise-grade instrumentation, observability, and continuous learning.
**Stack:** python, typescript, javascript, react, fastapi, langchain
**Repo:** https://github.com/NVIDIA/NeMo-Agent-Toolkit.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/NeMo-Agent-Toolkit/). Si necesitas el código: git clone https://github.com/NVIDIA/NeMo-Agent-Toolkit.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** trabajas con infra NVIDIA o necesitas guardrails/eval empresarial
**Evita si:** quieres algo ligero y agnóstico.
**Combina con:** `langchain`

## `nemoclaw`
role=skill · exec=local · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,javascript-typescript,langchain,postgres,python

**Qué es:** NVIDIA NemoClaw is an open source reference stack for running supported AI agents more safely inside NVIDIA OpenShell sandboxes. It provides guided onboarding, managed inference, network policy, managed integrations, snapshots, and lifecycle operations through the NemoClaw CLI and its agent-specific aliases.
**Stack:** javascript/typescript, python, typescript, javascript, docker, postgres, langchain
**Repo:** https://github.com/NVIDIA/NemoClaw.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/NemoClaw/). Si necesitas el código: git clone https://github.com/NVIDIA/NemoClaw.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres nvidia nemoclaw: reference stack for sandboxed ai agents in openshell
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `open-swe`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,langchain,postgres,python,react

**Qué es:** Elite engineering orgs like Stripe, Ramp, and Coinbase are building their own internal coding agents — Slackbots, CLIs, and web apps that meet engineers where they already work. These agents are connected to internal systems with the right context, permissioning, and safety boundaries to operate with minimal human oversight.
**Stack:** python, typescript, javascript, react, docker, postgres, langchain
**Repo:** https://github.com/langchain-ai/open-swe.git

**Instalación** [~]: `git clone https://github.com/langchain-ai/open-swe.git && cd open-swe && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres open-source framework for building your org's internal coding agent.
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `openclaw`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,typescript

**Qué es:** OpenClaw is a personal AI assistant that runs on your devices and meets you in the channels you already use. It is designed for a single operator and connects models, tools, messaging channels, and optional companion apps through one Gateway.
**Stack:** javascript/typescript, typescript, javascript, docker, postgres
**Repo:** https://github.com/openclaw/openclaw.git

**Instalación** [~]: `npm install openclaw   (o: pnpm add openclaw)`
_Nombre npm puede diferir de 'openclaw'; verifica en npmjs.com._

**Elige si:** quieres openclaw 🦞 — your assistant, on your devices, in your chats
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `openhands`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,python,typescript

**Qué es:** Run OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local, remote, and cloud backends.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/OpenHands/OpenHands.git

**Instalación** [~]: `git clone https://github.com/OpenHands/OpenHands.git && cd OpenHands && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres un agente que "haga", no solo hable
**Evita si:** solo necesitas chat/RAG o no puedes correr Docker.
**Combina con:** `ecc`, `sandbox`

## `openscreen`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,postgres,typescript

**Qué es:** This started as a side project that blew up; not production grade and you'll hit bugs, but hopefully it covers what you need. This project will soon be archived..
**Stack:** javascript/typescript, typescript, javascript, postgres
**Repo:** https://github.com/siddharthvaddem/openscreen.git

**Instalación** [~]: `git clone https://github.com/siddharthvaddem/openscreen.git && cd openscreen && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** necesitas screencast simple desde el navegador
**Evita si:** quieres algo mantenido y estable (el original está archivado) o grabación fuera del navegador.
**Combina con:** `opencut`

## `playwright`
role=runtime · exec=hybrid · setup=easy · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,postgres,python,typescript

**Qué es:** Playwright is a framework for web automation and testing. It drives Chromium, Firefox, and WebKit with a single API — in your tests, in your scripts, and as a tool for AI agents.
**Stack:** javascript/typescript, python, typescript, javascript, postgres
**Repo:** https://github.com/microsoft/playwright.git

**Instalación** [~]: `git clone https://github.com/microsoft/playwright.git && cd playwright && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** necesitas control preciso y reproducible del browser
**Evita si:** quieres que el agente navegue por visión ([browser-use](#-browser-use)) o no necesitas un navegador real.
**Combina con:** `browser-use`, `crawlee`

## `ponytail`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,fastapi,javascript,javascript-typescript,python,react,typescript

**Qué es:** You know him. Long ponytail. Oval glasses. Has been at the company longer than the version control. You show him fifty lines; he looks at them, says nothing, and replaces them with one.
**Stack:** javascript/typescript, python, typescript, javascript, react, fastapi
**Repo:** https://github.com/DietrichGebert/ponytail.git

**Instalación** [~]: `pip install ponytail   (o: uv add ponytail)`
_Nombre PyPI puede diferir de 'ponytail'; verifica en pypi.org._

**Elige si:** —
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `repomix`
role=library · exec=local · setup=easy · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,python,react,typescript

**Qué es:** Warp, built for coding with multiple AI agents Available for MacOS, Linux, & Windows.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/yamadashy/repomix.git

**Instalación** [~]: `pip install repomix   (o: uv add repomix)`
_Nombre PyPI puede diferir de 'repomix'; verifica en pypi.org._

**Elige si:** quieres need discussion? join us on <a href="https://discord.gg/wnyztwzfku">discord</a>!
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `ruflo`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,react,typescript

**Qué es:** An agent meta-harness for Claude Code and Codex..
**Stack:** javascript/typescript, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/ruvnet/ruflo.git

**Instalación** [~]: `git clone https://github.com/ruvnet/ruflo.git && cd ruflo && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** orquestas muchos agentes a escala y quieres rendimiento
**Evita si:** solo necesitas 1-2 agentes o no usas Claude Code/Codex.
**Combina con:** `mem0`, `ecc`

## `sandbox`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,javascript-typescript,langchain,python,react

**Qué es:** AIO Sandbox concentra herramientas de ejecución aislada para agentes: filesystem, red y procesos sin dejarlos sueltos en el host.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, langchain
**Repo:** https://github.com/agent-infra/sandbox.git

**Instalación** [~]: `pip install sandbox   (o: uv add sandbox)`
_Nombre PyPI puede diferir de 'sandbox'; verifica en pypi.org._

**Elige si:** quieres aislar la ejecución de agentes y reproducibilidad
**Evita si:** te basta correr local sin sandbox o no puedes asumir el overhead de Docker.
**Combina con:** `openhands`, `ecc`

## `scrapling`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,postgres,python,scraping,typescript

**Qué es:** Scrapling is an adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/D4Vinci/Scrapling.git

**Instalación** [~]: `pip install scrapling   (o: uv add scrapling)`
_Nombre PyPI puede diferir de 'Scrapling'; verifica en pypi.org._

**Elige si:** los sitios cambian o te bloquean a menudo
**Evita si:** el target es estable y simple, o no necesitas stealth.
**Combina con:** `scrapy`

## `t3code`
role=app · exec=cloud · setup=medium · mcp=False · prov=— · tags=agents,javascript,javascript-typescript,react,typescript

**Qué es:** T3 Code orquesta los agentes que ya corren en el host desde una UI (iOS, Android, web, Electron). No sustituye al modelo ni al runtime del agente.
**Stack:** javascript/typescript, typescript, javascript, react
**Repo:** https://github.com/pingdotgg/t3code.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** quieres t3 code is an "agent harness control surface". it enables control of the agents on your ma
**Evita si:** —
**Combina con:** `andrej-karpathy-skills`, `antigravity-awesome-skills`, `awesome-agent-skills`

## `tooljet`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,javascript,javascript-typescript,postgres,python,typescript

**Qué es:** :star: If you find ToolJet useful, please consider giving us a star on GitHub! Your support helps us continue to innovate and deliver exciting features.
**Stack:** javascript/typescript, python, typescript, javascript, docker, postgres
**Repo:** https://github.com/ToolJet/ToolJet.git

**Instalación** [~]: `git clone https://github.com/ToolJet/ToolJet.git && cd ToolJet && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres tooljet is the open-source foundation of tooljet ai - the ai-native platform for building
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `turbovec`
role=directory · exec=local · setup=heavy · mcp=False · prov=— · tags=automation,langchain,python,typescript

**Qué es:** A 10 million document corpus takes 31 GB of RAM as float32. turbovec fits it in 4 GB - and searches it faster than FAISS..
**Stack:** python, typescript, langchain
**Repo:** https://github.com/RyanCodrai/turbovec.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/turbovec/). Si necesitas el código: git clone https://github.com/RyanCodrai/turbovec.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** necesitas vector search veloz y embebido sin desplegar una DB
**Evita si:** ya usas una vector DB completa con persistencia y escalado horizontal.
**Combina con:** `mem0`, `graphrag`

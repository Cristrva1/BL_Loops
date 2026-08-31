# 5. MCP & Conectividad — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `awesome-mcp-clients`
role=directory · exec=hybrid · setup=medium · mcp=True · prov=— · tags=docker,javascript,langchain,mcp,postgres,python,react,typescript

**Qué es:** A curated list of awesome Model Context Protocol (MCP) clients.
**Stack:** python, typescript, javascript, react, docker, postgres, langchain
**Repo:** https://github.com/punkpeye/awesome-mcp-clients.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-mcp-clients/). Si necesitas el código: git clone https://github.com/punkpeye/awesome-mcp-clients.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `claude-plugins-official`
role=platform · exec=cloud · setup=medium · mcp=False · prov=— · tags=typescript · tools=claude-code

**Qué es:** A curated directory of high-quality plugins for Claude Code.
**Stack:** typescript
**Repo:** https://github.com/anthropics/claude-plugins-official.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** quieres extensiones oficiales con garantía de compatibilidad
**Evita si:** buscas aportes comunitarios amplios ([awesome-claude-code](#-awesome-claude-code)).
**Combina con:** `awesome-claude-code`

## `context7`
role=runtime · exec=local · setup=easy · mcp=True · prov=— · tags=mcp,docs,agents

**Qué es:** Context7 evita que el modelo alucine APIs viejas: trae docs versionadas al contexto. Instálalo como servidor MCP en el agente de código.
**Stack:** javascript/typescript, typescript, javascript, react
**Repo:** https://github.com/upstash/context7.git

**Instalación** [~]: `git clone https://github.com/upstash/context7.git && cd context7 && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `davinci-resolve-mcp`
role=runtime · exec=hybrid · setup=medium · mcp=True · prov=— · tags=mcp,video,agents

**Qué es:** DaVinci Resolve MCP expone edición, media pool, render, color y Fusion a asistentes compatibles con Model Context Protocol. Requiere Resolve abierto y, para scripting externo, la edición Studio.
**Stack:** python, typescript, javascript, whisper
**Repo:** https://github.com/samuelgursky/davinci-resolve-mcp.git

**Instalación** [~]: `git clone https://github.com/samuelgursky/davinci-resolve-mcp.git && cd davinci-resolve-mcp && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `github-mcp-server`
role=platform · exec=local · setup=medium · mcp=True · prov=— · tags=docker,javascript,mcp,python,react,typescript

**Qué es:** The GitHub MCP Server connects AI tools directly to GitHub's platform. This gives AI agents, assistants, and chatbots the ability to read repositories and code files, manage issues and PRs, analyze code, and automate workflows. All through natural language interactions.
**Stack:** python, typescript, javascript, react, docker
**Repo:** https://github.com/github/github-mcp-server.git

**Instalación** [~]: `git clone https://github.com/github/github-mcp-server.git && cd github-mcp-server && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `graphify`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=docker,javascript,multimedia,postgres,python,typescript,whisper

**Qué es:** Type /graphify in your AI coding assistant and it maps your entire project — code, docs, PDFs, images, videos — into a knowledge graph you can query instead of grepping through files.
**Stack:** python, typescript, javascript, docker, postgres, whisper
**Repo:** https://github.com/safishamsi/graphify.git

**Instalación** [~]: `pip install graphify   (o: uv add graphify)`
_Nombre PyPI puede diferir de 'graphify'; verifica en pypi.org._

**Elige si:** quieres ver conexiones visualmente o auditar un sistema
**Evita si:** solo necesitas índice textual barato ([codegraph](#-codegraph)) o tu proyecto es trivial.
**Combina con:** `codegraph`, `graphrag`

## `langchain-mcp-adapters`
role=library · exec=hybrid · setup=easy · mcp=True · prov=— · tags=javascript,langchain,mcp,python,typescript

**Qué es:** Puente ligero entre servidores MCP y el ecosistema LangChain/LangGraph. Librería, no un servidor MCP en sí.
**Stack:** python, typescript, javascript, langchain
**Repo:** https://github.com/langchain-ai/langchain-mcp-adapters.git

**Instalación** [~]: `pip install langchain-mcp-adapters   (o: uv add langchain-mcp-adapters)`
_Nombre PyPI puede diferir de 'langchain-mcp-adapters'; verifica en pypi.org._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `mcp`
role=directory · exec=hybrid · setup=medium · mcp=True · prov=— · tags=mcp,postgres,typescript

**Qué es:** This repository contains a list of Google's official Model Context Protocol (MCP) servers, guidance on how to deploy MCP servers to Google Cloud, and examples to get started.
**Stack:** typescript, postgres
**Repo:** https://github.com/google/mcp.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/mcp/). Si necesitas el código: git clone https://github.com/google/mcp.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** programas MCP a bajo nivel o necesitas conformidad estricta con la spec
**Evita si:** prefieres un framework de alto nivel que abstraiga el protocolo ([mcp-use](#-mcp-use)).
**Combina con:** `mcp-use`, `servers`

## `mcp-neo4j`
role=directory · exec=local · setup=medium · mcp=True · prov=— · tags=mcp,typescript

**Qué es:** These MCP servers are a part of the Neo4j Labs program. They are developed and maintained by the Neo4j Field GenAI team and welcome contributions from the larger developer community. These servers are frequently updated with new and experimental features, but are not supported by the Neo4j product team.
**Stack:** typescript
**Repo:** https://github.com/neo4j-contrib/mcp-neo4j.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/mcp-neo4j/). Si necesitas el código: git clone https://github.com/neo4j-contrib/mcp-neo4j.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** usas Neo4j con IA y quieres que el asistente hable Cypher
**Evita si:** no trabajas con grafos o tu base es relacional pura.
**Combina con:** `graphrag`, `awesome-mcp-servers`

## `metabase`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=docker,javascript,javascript-typescript,postgres,react,typescript

**Qué es:** The easiest way to get started with Metabase is to sign up for a free trial of Metabase Cloud.
**Stack:** javascript/typescript, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/metabase/metabase.git

**Instalación** [~]: `git clone https://github.com/metabase/metabase.git && cd metabase && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres BI accesible para perfiles no técnicos
**Evita si:** necesitas analítica de eventos por usuario ([posthog](#-posthog)).
**Combina con:** `posthog`, `echarts`

## `notebooklm-mcp-cli`
role=platform · exec=hybrid · setup=medium · mcp=True · prov=— · tags=mcp,postgres,python,react,typescript

**Qué es:** Programmatic access to Google NotebookLM — via command-line interface (CLI) or Model Context Protocol (MCP) server.
**Stack:** python, typescript, react, postgres
**Repo:** https://github.com/jacob-bd/notebooklm-mcp-cli.git

**Instalación** [~]: `git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git && cd notebooklm-mcp-cli && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** integras NotebookLM con tu asistente MCP
**Evita si:** prefieres la API directa en scripts ([notebooklm-py](#-notebooklm-py)).
**Combina con:** `notebooklm-py`, `awesome-mcp-servers`

## `opencut`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=typescript

**Qué es:** OpenCut is being rewritten from the ground up. What's coming:.
**Stack:** typescript
**Repo:** https://github.com/OpenCut-app/OpenCut.git

**Instalación** [~]: `git clone https://github.com/OpenCut-app/OpenCut.git && cd OpenCut && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** quieres un editor libre con UI moderna, sin CapCut
**Evita si:** prefieres edición por código ([moviepy](#-moviepy)) o cortes sin pérdida ([lossless-cut](#-lossless-cut)).
**Combina con:** `lossless-cut`

## `public-apis`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,postgres,python,react,typescript

**Qué es:** The Public APIs repository is manually curated by community members like you and folks working at APILayer. It includes an extensive list of public APIs from many domains that you can use for your own products. Consider it a treasure trove of APIs well-managed by the community over the years.
**Stack:** python, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/public-apis/public-apis.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/public-apis/). Si necesitas el código: git clone https://github.com/public-apis/public-apis.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** buscas datos externos y no sabes qué API usar
**Evita si:** ya tienes tus fuentes definidas o necesitas SLA empresarial (son APIs públicas, sin garantías).
**Combina con:** `n8n`, `firecrawl`

## `servers`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,postgres,python,typescript

**Qué es:** This repository is a collection of *reference implementations* for the Model Context Protocol (MCP), as well as references to community-built servers and additional resources.
**Stack:** javascript/typescript, python, typescript, javascript, postgres
**Repo:** https://github.com/modelcontextprotocol/servers.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/servers/). Si necesitas el código: git clone https://github.com/modelcontextprotocol/servers.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres ejemplos canónicos y plantillas fiables
**Evita si:** buscas soluciones listas para producción (son demos educativas, no hardening).
**Combina con:** `mcp-use`, `awesome-mcp-servers`

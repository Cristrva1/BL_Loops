# 6. Memoria, LLM Ops & Observabilidad — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `agentmemory`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=agents,docker,javascript,javascript-typescript,postgres,python,typescript

**Qué es:** Your coding agent remembers everything. No more re-explaining. Built on iii engine Persistent memory for Claude Code, GitHub Copilot CLI, Cursor, Gemini CLI, Codex CLI, Hermes, OpenClaw, pi, OpenCode, and any MCP client.
**Stack:** javascript/typescript, python, typescript, javascript, docker, postgres
**Repo:** https://github.com/rohitg00/agentmemory.git

**Instalación** [~]: `git clone https://github.com/rohitg00/agentmemory.git && cd agentmemory && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** cambias de asistente y quieres una memoria común entre ellos
**Evita si:** te basta la memoria nativa de un único cliente o no usas MCP.
**Combina con:** `mem0`, `ruflo`

## `engram`
role=runtime · exec=hybrid · setup=medium · mcp=True · prov=— · tags=memory,mcp,agents

**Qué es:** Engram da a cualquier agente compatible con MCP una memoria local (o cloud) en un solo binario, sin dependencias pesadas.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/Gentleman-Programming/engram.git

**Instalación** [~]: `git clone https://github.com/Gentleman-Programming/engram.git && cd engram && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** necesitas exponer herramientas o contexto a agentes vía MCP
**Evita si:** prefieres conexiones directas sin protocolo estándar
**Combina con:** `claude-plugins-official`, `n8n-skills`, `mcp`

## `loguru`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=python,typescript

**Qué es:** Did you ever feel lazy about configuring a logger and used print() instead?... I did, yet logging is fundamental to every application and eases the process of debugging. Using Loguru you have no excuse not to use logging from the start, this is as simple as from loguru import logger.
**Stack:** python, typescript
**Repo:** https://github.com/Delgan/loguru.git

**Instalación** [~]: `git clone https://github.com/Delgan/loguru.git && cd loguru && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres logging fácil y legible en Python sin pelear con stdlib
**Evita si:** ya usas el stdlib `logging` configurado o tienes un stack de observabilidad corporativo.
**Combina con:** `litellm`

## `mem0`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,postgres,python,typescript

**Qué es:** mem0 guarda y recupera hechos de usuario entre sesiones. Úsalo cuando el agente necesita memoria a largo plazo, no como base de datos general.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/mem0ai/mem0.git

**Instalación** [~]: `pip install mem0   (o: uv add mem0)`
_Nombre PyPI puede diferir de 'mem0'; verifica en pypi.org._

**Elige si:** quieres memoria estándar lista con integraciones amplias
**Evita si:** necesitas todo local sin llamadas a API ([mempalace](#-mempalace)) o control total del almacenamiento.
**Combina con:** `crewai`, `langchain`, `agentmemory`

## `mempalace`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,postgres,python,react,typescript

**Qué es:** Local-first AI memory. Verbatim storage, pluggable backend, 96.6% R@5 raw on LongMemEval — zero API calls.
**Stack:** python, typescript, react, docker, postgres
**Repo:** https://github.com/MemPalace/mempalace.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/mempalace/). Si necesitas el código: git clone https://github.com/MemPalace/mempalace.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** la privacidad es prioridad y no quieres llamadas a API
**Evita si:** quieres un SaaS gestionado con escalado automático o integraciones de framework ya hechas ([mem0](#-mem0)).
**Combina con:** `open-notebook`, `odysseus`

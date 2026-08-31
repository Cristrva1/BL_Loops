# 1. Automatización, Mensajería & CRM — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `activepieces`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,typescript

**Qué es:** Activepieces es un reemplazo open source de Zapier: orquestas automatizaciones con piezas auto-hospedables y un editor visual, sin ceder los datos a un SaaS cerrado.
**Stack:** javascript/typescript, typescript, javascript, docker
**Repo:** https://github.com/activepieces/activepieces.git

**Instalación** [~]: `git clone https://github.com/activepieces/activepieces.git && cd activepieces && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres reemplazar Zapier con piezas propias en TypeScript
**Evita si:** ya dominas n8n y su ecosistema te basta.
**Combina con:** `n8n`, `novu`
**Alternativas (elige una):** `n8n`

## `appsmith`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,postgres,typescript

**Qué es:** Organizations build custom applications like dashboards, admin panels, customer 360, IT automation, and service management tools to help their teams work more efficiently and effectively. Appsmith is an open-source low-code platform that streamlines custom application development, deployment, and maintenance. Learn more on our website.
**Stack:** typescript, javascript, docker, postgres
**Repo:** https://github.com/appsmithorg/appsmith.git

**Instalación** [~]: `git clone https://github.com/appsmithorg/appsmith.git && cd appsmith && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** —
**Evita si:** —
**Combina con:** `twenty-main`, `evolution-api`, `whatsapp-agentkit`

## `browser-use`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,python,typescript

**Qué es:** 🌤️ Want to skip the setup? Use our cloud for faster, scalable, stealth-enabled browser automation!.
**Stack:** python, typescript, docker
**Repo:** https://github.com/browser-use/browser-use.git

**Instalación** [~]: `git clone https://github.com/browser-use/browser-use.git && cd browser-use && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres navegación como humano y tolerancia a cambios de UI
**Evita si:** necesitas scripts deterministas y baratos ([playwright](#-playwright)) o no quieres depender de un LLM por paso.
**Combina con:** `playwright`, `gpt-researcher`

## `budibase`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,typescript

**Qué es:** AI Agents that run your operations Budibase is an open-source operations platform that saves engineers 100s of hours building Agents, Apps and Automations, securely.
**Stack:** javascript/typescript, typescript, javascript, docker, postgres
**Repo:** https://github.com/Budibase/budibase.git

**Instalación** [~]: `git clone https://github.com/Budibase/budibase.git && cd budibase && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** —
**Evita si:** —
**Combina con:** `twenty-main`, `evolution-api`, `whatsapp-agentkit`

## `chatwoot`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,typescript

**Qué es:** The modern customer support platform, an open-source alternative to Intercom, Zendesk, Salesforce Service Cloud etc.
**Stack:** javascript/typescript, typescript, javascript, docker
**Repo:** https://github.com/chatwoot/chatwoot.git

**Instalación** [~]: `npm install chatwoot   (o: pnpm add chatwoot)`
_Nombre npm puede diferir de 'chatwoot'; verifica en npmjs.com._

**Elige si:** das soporte por varios canales y necesitas handoff humano
**Evita si:** solo necesitas enviar mensajes salientes ([evolution-api](#-evolution-api)).
**Combina con:** `evolution-api`, `novu`

## `evolution-api`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,typescript

**Qué es:** Open-source REST API for WhatsApp and multi-channel messaging — part of the Evolution Foundation ecosystem.
**Stack:** javascript/typescript, typescript, javascript, docker, postgres
**Repo:** https://github.com/evolution-foundation/evolution-api.git

**Instalación** [~]: `git clone https://github.com/evolution-foundation/evolution-api.git && cd evolution-api && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** operas WhatsApp en producción con varias instancias
**Evita si:** solo necesitas un bot de prueba o un único script ([OpenWA](#-openwa) basta).
**Combina con:** `n8n`, `chatwoot`, `bot whatsapp`

## `huginn`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,typescript

**Qué es:** Huginn is a system for building agents that perform automated tasks for you online. They can read the web, watch for events, and take actions on your behalf. Huginn's Agents create and consume events, propagating them along a directed graph. Think of it as a hackable version of IFTTT or Zapier on your own server. You always know who has your data. You do.
**Stack:** javascript/typescript, typescript, javascript, docker, postgres
**Repo:** https://github.com/huginn/huginn.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/huginn/). Si necesitas el código: git clone https://github.com/huginn/huginn.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** automatizas tareas orientadas a eventos y valoras la privacidad
**Evita si:** quieres editor visual moderno o IA nativa ([n8n](#-n8n)).
**Combina con:** `n8n`, `novu`

## `listmonk`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,docker,postgres,typescript

**Qué es:** listmonk is a standalone, self-hosted, newsletter and mailing list manager. It is fast, feature-rich, and packed into a single binary. It uses a PostgreSQL database as its data store.
**Stack:** typescript, docker, postgres
**Repo:** https://github.com/knadh/listmonk.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/listmonk/). Si necesitas el código: git clone https://github.com/knadh/listmonk.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres email marketing simple, rápido y propio
**Evita si:** necesitas nurturing avanzado o scoring de leads ([mautic](#-mautic)).
**Combina con:** `mautic`, `n8n`

## `mautic`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,postgres,python,typescript

**Qué es:** Open Source Marketing Automation Software.
**Stack:** javascript/typescript, python, typescript, javascript, postgres
**Repo:** https://github.com/mautic/mautic.git

**Instalación** [~]: `git clone https://github.com/mautic/mautic.git && cd mautic && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** necesitas automatización de marketing seria y soberana
**Evita si:** te basta una newsletter simple ([listmonk](#-listmonk)).
**Combina con:** `listmonk`, `marketingskills`, `marketing de agencia`

## `n8n`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,langchain,python,typescript

**Qué es:** n8n is a workflow automation platform that gives technical teams the flexibility of code with the speed of no-code. With 400+ integrations, native AI capabilities, and a fair-code license, n8n lets you build powerful automations while maintaining full control over your data and deployments.
**Stack:** javascript/typescript, python, typescript, javascript, docker, langchain
**Repo:** https://github.com/n8n-io/n8n.git

**Instalación** [~]: `git clone https://github.com/n8n-io/n8n.git && cd n8n && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres el motor central de automatización con máximo catálogo
**Evita si:** buscas algo minimalista o sin self-host.
**Combina con:** `n8n-mcp`, `n8n-skills`, `evolution-api`
**Alternativas (elige una):** `activepieces`, `huginn`

## `n8n-io`
role=platform · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,langchain,python,typescript

**Qué es:** n8n is a workflow automation platform that gives technical teams the flexibility of code with the speed of no-code. With 400+ integrations, native AI capabilities, and a fair-code license, n8n lets you build powerful automations while maintaining full control over your data and deployments.
**Stack:** javascript/typescript, python, typescript, javascript, docker, langchain
**Repo:** https://github.com/n8n-io/n8n.git

**Instalación** [~]: `git clone https://github.com/n8n-io/n8n.git && cd n8n && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres n8n - secure workflow automation for technical teams
**Evita si:** ya usas la ficha [n8n](#-n8n) (es el mismo proyecto).
**Combina con:** `n8n`

## `n8n-mcp`
role=platform · exec=local · setup=medium · mcp=True · prov=— · tags=automation,docker,javascript,javascript-typescript,langchain,mcp,python,typescript

**Qué es:** A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to n8n node documentation, properties, and operations. Deploy in minutes to give Claude and other AI assistants deep knowledge about n8n's 1,845 workflow automation nodes (816 core + 1,029 community).
**Stack:** javascript/typescript, python, typescript, javascript, docker, langchain
**Repo:** https://github.com/czlonkowski/n8n-mcp.git

**Instalación** [~]: `git clone https://github.com/czlonkowski/n8n-mcp.git && cd n8n-mcp && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** generas flujos n8n con IA y quieres menos alucinaciones de parámetros
**Evita si:** no usas n8n o construyes los flujos a mano.
**Combina con:** `n8n`, `n8n-skills`, `bot whatsapp`

## `novu`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,react,typescript

**Qué es:** The open-source communication infrastructure for agents and products.
**Stack:** javascript/typescript, typescript, javascript, react
**Repo:** https://github.com/novuhq/novu.git

**Instalación** [~]: `npm install novu   (o: pnpm add novu)`
_Nombre npm puede diferir de 'novu'; verifica en npmjs.com._

**Elige si:** envías notificaciones por varios canales y quieres un único backend
**Evita si:** solo necesitas email ([listmonk](#-listmonk)).
**Combina con:** `chatwoot`, `activepieces`

## `openevolve`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,python,typescript

**Qué es:** 🧬 The most advanced open-source evolutionary coding agent.
**Stack:** python, typescript, docker
**Repo:** https://github.com/algorithmicsuperintelligence/openevolve.git

**Instalación** [~]: `pip install openevolve   (o: uv add openevolve)`
_Nombre PyPI puede diferir de 'openevolve'; verifica en pypi.org._

**Elige si:** optimizas problemas algorítmicos donde cabe explorar muchas variantes
**Evita si:** haces tareas de texto comunes o buscas respuesta inmediata.
**Combina con:** `llm-council`

## `openwa`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,javascript-typescript,postgres,python,react,typescript

**Qué es:** OpenWA is a free, open-source WhatsApp API Gateway designed for developers who need full control over their messaging infrastructure—without vendor lock-in or hidden paywalls.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/rmyndharis/OpenWA.git

**Instalación** [~]: `git clone https://github.com/rmyndharis/OpenWA.git && cd OpenWA && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** desarrollas scripts o bots individuales y quieres arrancar rápido
**Evita si:** necesitas infra multi-instancia o alta disponibilidad ([evolution-api](#-evolution-api)).
**Combina con:** `n8n`, `evolution-api`

## `twenty-main`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=automation,docker,javascript,javascript-typescript,postgres,react,typescript

**Qué es:** Twenty gives technical teams the building blocks for a custom CRM that meets complex business needs and quickly adapts as the business evolves. Twenty is the CRM you build, ship, and version like the rest of your stack.
**Stack:** javascript/typescript, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/twentyhq/twenty

**Instalación** [~]: `git clone https://github.com/twentyhq/twenty && cd twenty && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres un CRM que se adapte 1:1 a tu negocio y vivir en self-host
**Evita si:** buscas algo plug-and-play gestionado o no quieres operar PostgreSQL y Docker.
**Combina con:** `evolution-api`, `n8n`

## `whatsapp-agentkit`
role=directory · exec=cloud · setup=medium · mcp=False · prov=— · tags=agents,automation,docker,fastapi,javascript,postgres,python,typescript

**Qué es:** Construye tu propio agente de WhatsApp con inteligencia artificial en menos de 30 minutos. No necesitas saber programar. Claude Code construye todo por ti.
**Stack:** python, typescript, javascript, docker, postgres, fastapi
**Repo:** https://github.com/Hainrixz/whatsapp-agentkit.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/whatsapp-agentkit/). Si necesitas el código: git clone https://github.com/Hainrixz/whatsapp-agentkit.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres arrancar sin partir de cero y te vale con lo que Claude Code genere
**Evita si:** necesitas control fino del stack o ya tienes el bot hecho.
**Combina con:** `evolution-api`, `n8n-mcp`

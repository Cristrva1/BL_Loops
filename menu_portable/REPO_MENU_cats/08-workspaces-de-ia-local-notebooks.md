# 8. Workspaces de IA Local & Notebooks — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `hermes-desktop`
role=app · exec=local · setup=medium · mcp=False · prov=— · tags=automation,javascript,javascript-typescript,postgres,python,react,typescript

**Qué es:** Hermes Desktop envuelve el agente Hermes en una UI nativa. Úsalo si quieres Hermes como aplicación, no solo como CLI.
**Stack:** javascript/typescript, python, typescript, javascript, react, postgres
**Repo:** https://github.com/fathah/hermes-desktop.git

**Instalación** [~]: `git clone https://github.com/fathah/hermes-desktop.git && cd hermes-desktop && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres español (latam)
**Evita si:** —
**Combina con:** `awesome-claude-code`, `agents-towards-production`, `ag2`

## `open-notebook`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,fastapi,langchain,postgres,python,react,typescript

**Qué es:** An open source, privacy-focused alternative to Google's Notebook LM!.
**Stack:** python, typescript, react, docker, postgres, fastapi, langchain
**Repo:** https://github.com/lfnovo/open-notebook.git

**Instalación** [~]: `git clone https://github.com/lfnovo/open-notebook.git && cd open-notebook && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres NotebookLM privado y sin cuotas
**Evita si:** prefieres el NotebookLM real automatizado ([notebooklm-py](#-notebooklm-py)).
**Combina con:** `odysseus`, `markitdown`

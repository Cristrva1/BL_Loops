# 4. Scraping, Búsqueda & Research Web — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `archivebox`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,postgres,python,typescript

**Qué es:** ArchiveBox is a self-hosted app that lets you preserve content from websites in a variety of formats.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/ArchiveBox/ArchiveBox.git

**Instalación** [~]: `git clone https://github.com/ArchiveBox/ArchiveBox.git && cd ArchiveBox && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres ▶️ <a href="https://github.com/archivebox/archivebox/wiki/quickstart">quickstart
**Evita si:** —
**Combina con:** `firecrawl`, `crawl4ai`, `scrapy`

## `crawl4ai`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,fastapi,javascript,postgres,python,react,scraping,typescript

**Qué es:** 🚀 Crawl4AI Cloud API — Closed Beta (Launching Soon) Reliable, large-scale web extraction, now built to be _drastically more cost-effective_ than any of the existing solutions.
**Stack:** python, typescript, javascript, react, docker, postgres, fastapi
**Repo:** https://github.com/unclecode/crawl4ai.git

**Instalación** [~]: `git clone https://github.com/unclecode/crawl4ai.git && cd crawl4ai && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** necesitas volumen barato y self-host
**Evita si:** quieres una API hosted simple sin operar navegadores ([firecrawl](#-firecrawl)).
**Combina con:** `firecrawl`, `gpt-researcher`

## `crawlee`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,javascript-typescript,python,react,scraping,typescript

**Qué es:** Crawlee covers your crawling and scraping end-to-end and helps you build reliable scrapers. Fast..
**Stack:** javascript/typescript, python, typescript, javascript, react, docker
**Repo:** https://github.com/apify/crawlee.git

**Instalación** [~]: `git clone https://github.com/apify/crawlee.git && cd crawlee && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** scrapeas con Node y necesitas antibloqueo
**Evita si:** trabajas en Python ([crawlee-python](#-crawlee-python)) o no necesitas evasión.
**Combina con:** `playwright`

## `crawlee-python`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,python,react,scraping,typescript

**Qué es:** Crawlee covers your crawling and scraping end-to-end and helps you build reliable scrapers. Fast..
**Stack:** python, typescript, javascript, react
**Repo:** https://github.com/apify/crawlee-python.git

**Instalación** [~]: `pip install crawlee   (o: uv add crawlee)`
_Nombre PyPI puede diferir de 'crawlee-python'; verifica en pypi.org._

**Elige si:** quieres Crawlee en Python con antibloqueo
**Evita si:** ya usas scrapy y te basta, o no necesitas evasión.
**Combina con:** `scrapy`, `playwright`

## `firecrawl`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=docker,javascript,python,scraping,typescript

**Qué es:** The API to search, scrape, and interact with the web at scale. 🔥 The web context API to find sources, extract content, and turn it into clean Markdown or structured data your agents can ship with. Open source and available as a hosted service.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/firecrawl/firecrawl.git

**Instalación** [~]: `pip install firecrawl   (o: uv add firecrawl)`
_Nombre PyPI puede diferir de 'firecrawl'; verifica en pypi.org._

**Elige si:** alimentas agentes/RAG con web y quieres salida limpia
**Evita si:** solo quieres HTML crudo o el presupuesto de API no encaja.
**Combina con:** `gpt-researcher`, `crawl4ai`, `research profundo`

## `how-to-train-your-gpt`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=python,typescript

**Qué es:** A guide to building a world-class language model from absolute scratch. Taught like you're five. Built like you're an engineer.*.
**Stack:** python, typescript
**Repo:** https://github.com/raiyanyahya/how-to-train-your-gpt.git

**Instalación** [~]: `git clone https://github.com/raiyanyahya/how-to-train-your-gpt.git && cd how-to-train-your-gpt && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres una guía explicada y narrada
**Evita si:** prefieres solo el código limpio ([nanoGPT](#-nanogpt)) o buscas algo productivo.
**Combina con:** `nanogpt`, `nanochat`

## `instaloader`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=python,typescript,vision

**Qué es:** Instaloader es un scraper de Instagram orientado a archivo personal o datasets. No es un navegador agentizado; es una herramienta de extracción puntual.
**Stack:** python, typescript
**Repo:** https://github.com/instaloader/instaloader.git

**Instalación** [~]: `pip install instaloader   (o: uv add instaloader)`
_Nombre PyPI puede diferir de 'instaloader'; verifica en pypi.org._

**Elige si:** necesitas datos de Instagram de forma fiable
**Evita si:** quieres varias redes a la vez ([snscrape](#-snscrape)) o el contenido requiere API oficial por ToS.
**Combina con:** `snscrape`

## `llm-scraper`
role=platform · exec=cloud · setup=easy · mcp=False · prov=— · tags=javascript,javascript-typescript,scraping,typescript

**Qué es:** LLM Scraper is a TypeScript library that allows you to extract structured data from any webpage using LLMs.
**Stack:** javascript/typescript, typescript, javascript
**Repo:** https://github.com/mishushakov/llm-scraper.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** quieres salida tipada y validada en stack TS
**Evita si:** prefieres extracción semántica por grafos ([Scrapegraph-ai](#-scrapegraph-ai)) o trabajas en Python.
**Combina con:** `playwright`, `firecrawl`

## `odysseus`
role=skill · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=agents,docker,javascript,postgres,python,typescript

**Qué es:** A self-hosted AI workspace for chat, agents, research, documents, email, notes, calendar, and local model workflows.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/pewdiepie-archdaemon/odysseus.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/odysseus/). Si necesitas el código: git clone https://github.com/pewdiepie-archdaemon/odysseus.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres operación privada todo-en-uno y aceptas operar la infra
**Evita si:** prefieres SaaS gestionado sin mantenimiento.
**Combina con:** `open-notebook`, `ecc`, `mem0`, `workspace privado`

## `scrapegraph-ai`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,langchain,python,scraping,typescript

**Qué es:** ScrapeGraphAI convierte una instrucción en un grafo de extracción web. Encaja cuando el HTML es irregular y un scraper clásico se rompe.
**Stack:** python, typescript, javascript, docker, langchain
**Repo:** https://github.com/ScrapeGraphAI/Scrapegraph-ai.git

**Instalación** [~]: `git clone https://github.com/ScrapeGraphAI/Scrapegraph-ai.git && cd Scrapegraph-ai && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres estructura semántica "by prompt" en Python
**Evita si:** te basta un esquema simple ([llm-scraper](#-llm-scraper)) o el coste de LLM por página es alto.
**Combina con:** `crawl4ai`, `graphrag`

## `scrapely`
role=library · exec=hybrid · setup=easy · mcp=False · prov=— · tags=javascript,python,scraping,typescript

**Qué es:** some example web pages and the data to be extracted, scrapely constructs a parser for all similar pages.
**Stack:** python, typescript, javascript
**Repo:** https://github.com/scrapy/scrapely.git

**Instalación** [~]: `pip install scrapely   (o: uv add scrapely)`
_Nombre PyPI puede diferir de 'scrapely'; verifica en pypi.org._

**Elige si:** prefieres enseñar por ejemplos y el sitio es homogéneo
**Evita si:** necesitas un crawler completo o el proyecto exige mantenimiento activo.
**Combina con:** `firecrawl`, `crawl4ai`, `scrapy`

## `scrapy`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=python,scraping

**Qué es:** Scrapy es el estándar de crawling en Python: spiders, pipelines y export. Úsalo para extracciones masivas, no para una sola página puntual.
**Stack:** python
**Repo:** https://github.com/scrapy/scrapy.git

**Instalación** [~]: `pip install scrapy   (o: uv add scrapy)`
_Nombre PyPI puede diferir de 'scrapy'; verifica en pypi.org._

**Elige si:** quieres un crawler sólido y configurable a escala
**Evita si:** buscas salida lista para LLM o algo puntual sin curva de framework.
**Combina con:** `scrapely`, `crawlee-python`

## `snscrape`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=python,scraping,typescript

**Qué es:** snscrape is a scraper for social networking services (SNS). It scrapes things like user profiles, hashtags, or searches and returns the discovered items, e.g. the relevant posts.
**Stack:** python, typescript
**Repo:** https://github.com/JustAnotherArchivist/snscrape.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/snscrape/). Si necesitas el código: git clone https://github.com/JustAnotherArchivist/snscrape.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** recolectas varias redes y no te sirve una API oficial
**Evita si:** solo necesitas Instagram ([instaloader](#-instaloader)) o la plataforma ya bloqueó el acceso no oficial.
**Combina con:** `instaloader`

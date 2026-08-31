# 7. Inteligencia de Código, Datos & Entrenamiento — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `awesome-bigdata`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=docker,javascript,postgres,python,react,typescript

**Qué es:** A curated list of awesome big data frameworks, resources and other awesomeness. Inspired by awesome-php, awesome-python, awesome-ruby, hadoopecosystemtable & big-data.
**Stack:** python, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/oxnr/awesome-bigdata.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/awesome-bigdata/). Si necesitas el código: git clone https://github.com/oxnr/awesome-bigdata.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** diseñas pipelines de datos grandes y necesitas descubrir el ecosistema
**Evita si:** tu proyecto es pequeño y no justifica herramientas de big data.
**Combina con:** `awesome-dataviz`

## `codegraph`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=fastapi,javascript,javascript-typescript,postgres,python,react,typescript

**Qué es:** CodeGraph construye un grafo del codebase para que un agente navegue símbolos y dependencias sin leer el repo entero.
**Stack:** javascript/typescript, python, typescript, javascript, react, postgres, fastapi
**Repo:** https://github.com/colbymchenry/codegraph.git

**Instalación** [~]: `pip install codegraph   (o: uv add codegraph)`
_Nombre PyPI puede diferir de 'codegraph'; verifica en pypi.org._

**Elige si:** trabajas repos grandes y el contexto del agente es caro
**Evita si:** tu base de código es pequeña y no justifica mantener un índice.
**Combina con:** `graphify`, `headroom`, `análisis de repos`

## `data-science-ipython-notebooks`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=postgres,python,typescript

**Qué es:** Directorio de notebooks educativos de data science. Es material de referencia, no una librería para importar en producción.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/donnemartin/data-science-ipython-notebooks.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/data-science-ipython-notebooks/). Si necesitas el código: git clone https://github.com/donnemartin/data-science-ipython-notebooks.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** estudias/consultas DS con ejemplos ejecutables
**Evita si:** buscas una librería, no ejemplos, o necesitas material actualizado a las versiones más recientes.
**Combina con:** `dash`, `streamlit`

## `deepseek-coder`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=docker,javascript,python,typescript · tools=deepseek

**Qué es:** DeepSeek Coder is composed of a series of code language models, each trained from scratch on 2T tokens, with a composition of 87% code and 13% natural language in both English and Chinese. We provide various sizes of the code model, ranging from 1B to 33B versions.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/deepseek-ai/DeepSeek-Coder.git

**Instalación** [~]: `pip install deepseek-coder   (o: uv add deepseek-coder)`
_Nombre PyPI puede diferir de 'DeepSeek-Coder'; verifica en pypi.org._

**Elige si:** quieres un modelo de código abierto y desplegable on-prem
**Evita si:** prefieres APIs comerciales gestionadas o no tienes GPU para servirlo.
**Combina con:** `litellm`, `codegraph`

## `echarts`
role=library · exec=local · setup=easy · mcp=False · prov=— · tags=javascript,javascript-typescript,typescript

**Qué es:** Apache ECharts is a free, powerful charting and visualization library offering easy ways to add intuitive, interactive, and highly customizable charts to your commercial products. It is written in pure JavaScript and based on zrender , which is a whole new lightweight canvas library.
**Stack:** javascript/typescript, typescript, javascript
**Repo:** https://github.com/apache/echarts.git

**Instalación** [~]: `npm install echarts   (o: pnpm add echarts)`
_Nombre npm puede diferir de 'echarts'; verifica en npmjs.com._

**Elige si:** necesitas gráficos ricos y variados embebidos
**Evita si:** solo series temporales simples y priorizas peso ([uPlot](#-uplot)).
**Combina con:** `metabase`, `heroui`

## `gitnexus`
role=runtime · exec=hybrid · setup=easy · mcp=False · prov=— · tags=docker,javascript,javascript-typescript,langchain,python,react,typescript

**Qué es:** ⚠️ Important Notice: GitNexus has NO official cryptocurrency, token, or coin. Any token/coin using the GitNexus name on Pump.fun or any other platform is not affiliated with, endorsed by, or created by this project or its maintainers. Do not purchase any cryptocurrency claiming association with GitNexus.
**Stack:** javascript/typescript, python, typescript, javascript, react, docker, langchain
**Repo:** https://github.com/abhigyanpatwari/GitNexus.git

**Instalación** [~]: `git clone https://github.com/abhigyanpatwari/GitNexus.git && cd GitNexus && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres entender un repo puntual de forma visual
**Evita si:** necesitas indexar muchos repos a escala ([codegraph](#-codegraph)) o no quieres front web.
**Combina con:** `codegraph`, `análisis de repos`

## `llm.c`
role=app · exec=cloud · setup=heavy · mcp=False · prov=— · tags=javascript,python,typescript

**Qué es:** LLMs in simple, pure C/CUDA with no need for 245MB of PyTorch or 107MB of cPython. Current focus is on pretraining, in particular reproducing the GPT-2 and GPT-3 miniseries, along with a parallel PyTorch reference implementation in train_gpt2.py. You'll recognize this file as a slightly tweaked nanoGPT.
**Stack:** python, typescript, javascript
**Repo:** https://github.com/karpathy/llm.c.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** quieres bajo nivel sin abstracciones y tienes GPU CUDA
**Evita si:** prefieres PyTorch ([nanoGPT](#-nanogpt)) o no tienes CUDA.
**Combina con:** `nanogpt`

## `openai-python`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,postgres,python,typescript

**Qué es:** The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.9+ application. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients powered by httpx.
**Stack:** python, typescript, javascript, postgres
**Repo:** https://github.com/openai/openai-python.git

**Instalación** [~]: `git clone https://github.com/openai/openai-python.git && cd openai-python && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** usas modelos de OpenAI desde Python y quieres el cliente oficial
**Evita si:** quieres abstracción multi-proveedor ([litellm](#-litellm)) o no usas OpenAI.
**Combina con:** `litellm`, `langchain`

## `swe-bench`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=docker,python,typescript

**Qué es:** SWE-bench is a benchmark for evaluating large language models on real world software issues collected from GitHub. Given a codebase and an issue, a language model is tasked with generating a patch that resolves the described problem.
**Stack:** python, typescript, docker
**Repo:** https://github.com/SWE-bench/SWE-bench.git

**Instalación** [~]: `pip install swe-bench   (o: uv add swe-bench)`
_Nombre PyPI puede diferir de 'SWE-bench'; verifica en pypi.org._

**Elige si:** quieres code and data for the following works:
**Evita si:** —
**Combina con:** `codegraph`, `gitnexus`, `deepseek-coder`

## `timesfm`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=docker,python,typescript

**Qué es:** TimesFM predice series temporales con un decoder-only pretrained. Es un modelo de investigación/producción de forecasting, no un dashboard.
**Stack:** python, typescript, docker
**Repo:** https://github.com/google-research/timesfm.git

**Instalación** [~]: `pip install timesfm   (o: uv add timesfm)`
_Nombre PyPI puede diferir de 'timesfm'; verifica en pypi.org._

**Elige si:** quieres timesfm (time series foundation model) is a pretrained time-series foundation
**Evita si:** —
**Combina con:** `firecrawl`, `crawl4ai`, `scrapy`

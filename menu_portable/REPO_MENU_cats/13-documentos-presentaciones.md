# 13. Documentos & Presentaciones — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `markitdown`
role=directory · exec=local · setup=easy · mcp=False · prov=— · tags=docker,postgres,python,typescript

**Qué es:** MarkItDown performs I/O with the privileges of the current process. Like open() or requests.get(), it will access resources that the process itself can access. Sanitize your inputs in untrusted environments, and call the narrowest `convert_*` function needed for your use case (e.g., `convert_stream()`, or `convert_local()`). See the Security Considerations section of the documentation for .
**Stack:** python, typescript, docker, postgres
**Repo:** https://github.com/microsoft/markitdown.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/markitdown/). Si necesitas el código: git clone https://github.com/microsoft/markitdown.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** alimentas LLMs con documentos de formatos variados
**Evita si:** ya tienes el texto limpio o necesitas fidelidad de layout total (no es un reconstructor de PDF).
**Combina con:** `ppt-master`, `open-notebook`, `docs → presentaciones`

## `pdf-inspector`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,python,typescript

**Qué es:** PDF Inspector detecta si un PDF es texto o escaneado y extrae contenido con coordenadas. Encaja en pipelines de documentos, no como visor.
**Stack:** python, typescript, javascript
**Repo:** https://github.com/firecrawl/pdf-inspector.git

**Instalación** [~]: `pip install pdf-inspector   (o: uv add pdf-inspector)`
_Nombre PyPI puede diferir de 'pdf-inspector'; verifica en pypi.org._

**Elige si:** —
**Evita si:** —
**Combina con:** `firecrawl`, `crawl4ai`, `scrapy`

## `pdfcraft`
role=app · exec=local · setup=medium · mcp=False · prov=— · tags=docker,javascript,javascript-typescript,postgres,react,typescript

**Qué es:** PDFCraft procesa PDFs en el cliente. Encaja para utilidades locales de documentos, no para un pipeline de conversión masiva.
**Stack:** javascript/typescript, typescript, javascript, react, docker, postgres
**Repo:** https://github.com/PDFCraftTool/pdfcraft.git

**Instalación** [~]: `git clone https://github.com/PDFCraftTool/pdfcraft.git && cd pdfcraft && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** manipulas PDFs con privacidad y sin instalar nada
**Evita si:** necesitas conversión a Markdown para IA ([markitdown](#-markitdown)) o edición de contenido (no solo manipulación de páginas).
**Combina con:** `markitdown`

## `pdfding`
role=app · exec=local · setup=medium · mcp=False · prov=— · tags=docker,frontend,javascript,python,typescript

**Qué es:** PdfDing es un manager de PDFs que hosteas tú. Alternativa ligera a suites documentales pesadas.
**Stack:** python, typescript, javascript, docker
**Repo:** https://github.com/mrmn2/PdfDing.git

**Instalación** [~]: `git clone https://github.com/mrmn2/PdfDing.git && cd PdfDing && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres selfhosted pdf manager, viewer and editor offering a seamless user experience on multiple
**Evita si:** —
**Combina con:** `markitdown`, `ppt-master`, `reveal.js`

## `ppt-master`
role=library · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=postgres,python,typescript

**Qué es:** This project is kept free and open source with the support of PackyCode , APIKEY.FUN , RunAPI , YouYun ZhiSuan and other sponsors.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/hugohe3/ppt-master.git

**Instalación** [~]: `pip install ppt-master   (o: uv add ppt-master)`
_Nombre PyPI puede diferir de 'ppt-master'; verifica en pypi.org._

**Elige si:** quieres PPTX editable de Office rápido
**Evita si:** prefieres slides web por código ([reveal.js](#-revealjs)) o control de diseño pixel-perfect.
**Combina con:** `markitdown`, `docs → presentaciones`

## `reveal.js`
role=runtime · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,typescript

**Qué es:** reveal.js is an open source HTML presentation framework. It enables anyone with a web browser to create beautiful presentations for free. Check out the live demo at revealjs.com.
**Stack:** javascript/typescript, typescript, javascript
**Repo:** https://github.com/hakimel/reveal.js.git

**Instalación** [~]: `git clone https://github.com/hakimel/reveal.js.git && cd reveal.js && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** quieres slides web por código, versionables
**Evita si:** necesitas PPTX editable en Office ([ppt-master](#-ppt-master)) o un editor visual de slides.
**Combina con:** `markitdown`, `ppt-master`, `revealjs`

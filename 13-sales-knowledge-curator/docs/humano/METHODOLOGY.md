# Metodología

## Pregunta educativa

¿Cómo enriquecer una biblioteca de ventas sin convertir disponibilidad web, reputación o prosa de
un modelo en evidencia suficiente?

## Método aplicado

1. Inventariar y conservar procedencia antes de extraer claims.
2. Distinguir obra, edición, copia digital, acceso y permiso de uso.
3. Preferir API o feed oficial; usar navegador solo para una página pública allowlisted.
4. Fallar cerrado ante derechos, jurisdicción, red, redirects, DNS, robots, MIME o tamaño ambiguos.
5. Guardar hashes y manifiestos; mantener fallos parciales visibles.
6. Separar revisión de claims, construcción de staging y aprobación posterior del candidato.
7. Exportar por archivos, nunca mediante una dependencia viva con NotebookLM o el laboratorio 09.

## Decisiones verificadas

| Tipo | Decisión |
|---|---|
| Implementada | MarkItDown `0.1.7` con extras PDF/DOCX y plugins desactivados |
| Implementada | Crawl4AI `0.9.2`, Chromium dedicado/headless y controles fail-closed |
| Implementada | Open Library y Google Books mediante JSON oficial |
| Implementada | `audit --extractor ollama`, modelo loopback explícito, chunk cap y salida/citas estrictas |
| Implementada | Paquete NotebookLM manual, máximo configurable de 1 a 50 fichas por notebook |
| Implementada | Paquete RAG de metadatos JSONL, sin texto restringido |
| Configurable | Dominio real y valor concreto de jurisdicción |
| Aprobada | Red como capacidad, allowlist, idiomas `en`/`es` y aprobación por cualquier operador identificado |
| Aplazada | CrewAI, ArchiveBox, Langfuse, embeddings e importación automática a `09-agentic-rag` |

La prueba live del conector usó la jurisdicción centinela `TEST`. Esa evidencia comprueba red,
catálogo y manifiesto; no configura ni valida la jurisdicción real del proyecto.

## Fuentes oficiales

- Microsoft MarkItDown: [repositorio y uso](https://github.com/microsoft/markitdown),
  [paquete](https://pypi.org/project/markitdown/) y
  [licencia MIT](https://raw.githubusercontent.com/microsoft/markitdown/main/LICENSE).
- UncleCode Crawl4AI: [repositorio](https://github.com/unclecode/crawl4ai),
  [quickstart](https://docs.crawl4ai.com/core/quickstart/),
  [configuración de navegador](https://docs.crawl4ai.com/core/browser-crawler-config/) y
  [licencia](https://raw.githubusercontent.com/unclecode/crawl4ai/main/LICENSE).
- Open Library: [API](https://openlibrary.org/developers/api),
  [lectura y préstamo](https://openlibrary.org/help/faq/reading) y
  [licencia de datos](https://openlibrary.org/developers/licensing).
- Google Books: [uso de API](https://developers.google.com/books/docs/v1/using),
  [campos de acceso](https://developers.google.com/books/docs/v1/reference/volumes) y
  [términos](https://developers.google.com/books/terms).
- NotebookLM: [fuentes admitidas](https://support.google.com/gemininotebook/answer/16215270?co=GENIE.Platform%3DDesktop&hl=en),
  [límites](https://support.google.com/gemininotebook/answer/16213268?hl=es-MX) y
  [notas/exportación](https://support.google.com/gemininotebook/answer/16262519?hl=en).
- Library of Congress: [comprender copyright](https://www.loc.gov/legal/understanding-copyright/).

Crawl4AI requiere conservar atribución visible a UncleCode y al proyecto Crawl4AI conforme al
texto añadido a su `LICENSE`; esta documentación y la ayuda del CLI deben mantenerla.

## Límites de interpretación

- MarkItDown optimiza texto para análisis; no garantiza maquetación, tablas, OCR o localizadores de
  página. Una proyección vacía falla.
- Ollama no convierte confianza del modelo en evidencia: el claim debe conservar una cita literal
  localizable. Una salida inválida falla la corrida y no activa el extractor determinista.
- Open Library marca préstamo o lectura, no prueba derechos de copia. El adaptador no proporciona
  `download_url`.
- En Google Books, `free-ebooks` o `ALL_PAGES` no bastan. El adaptador exige además
  `publicDomain=true`, `FULL_PUBLIC_DOMAIN`, PDF disponible y URL HTTPS.
- Los metadatos de proveedor pueden ser erróneos. La jurisdicción y la evidencia de derechos se
  revisan antes de cualquier uso.
- NotebookLM de consumo no se trata como API del runtime. El paquete se carga manualmente y sus
  respuestas siguen necesitando validación contra la fuente.
- “Educativo” o “sin fines comerciales” no es una licencia. Preview, préstamo, DRM, paywall y
  derechos desconocidos quedan como metadatos/enlace.

## Catálogos siguientes, no implementados

Estos son candidatos oficiales, no proveedores activos:

| Catálogo | Entrada primaria para una fase posterior |
|---|---|
| Project Gutenberg | [OPDS y catálogos offline](https://www.gutenberg.org/ebooks/offline_catalogs.html) |
| DOAB/OAPEN | [metadata DOAB](https://www.doabooks.org/en/resources/metadata-harvesting-and-content-dissemination) y [metadata OAPEN](https://www.oapen.org/article/metadata) |
| Internet Archive | [Metadata API](https://archive.org/developers/md-read.html) |
| HathiTrust | [Bibliographic API](https://www.hathitrust.org/member-libraries/resources-for-librarians/data-resources/bibliographic-api/) |
| Library of Congress | [JSON/YAML API](https://www.loc.gov/apis/json-and-yaml/) |
| BNE Digital | [datos enlazados BNE](https://datos.bne.es/) |
| Europeana | [API oficial](https://pro.europeana.eu/page/get-api) |

Añadir cualquiera exige adaptador y pruebas propios. La licencia de sus metadatos no se hereda al
objeto digital; no deben aparecer como activos solo porque sus nombres existan en el schema.

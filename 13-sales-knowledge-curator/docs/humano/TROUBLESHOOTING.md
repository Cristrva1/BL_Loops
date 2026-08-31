# Diagnóstico

## Confirmar el estado sin exponer configuración

```powershell
uv run sales-curator doctor
```

El informe muestra booleanos, conteos y versiones. Deliberadamente no lista dominios, modelo ni
contenido del `.env`.

## `NETWORK_ENABLED=false` o falta otro gate

La red requiere tres booleanos verdaderos, allowlist, presupuesto y `--authorize-network`.
Activar solo una variable no es suficiente. Si `RESEARCH_JURISDICTION` sigue vacío, escribe el
valor aprobado o usa `--jurisdiction`; no lo deduzcas de la IP o del idioma.

## `dominio fuera de allowlist` o DNS privado

Incluye únicamente el host exacto necesario. Open Library usa `openlibrary.org`; Google Books API
usa `www.googleapis.com`. No añadas `*`, esquemas, rutas ni un dominio padre demasiado amplio.
Un redirect se vuelve a validar y una resolución a IP privada/no enrutable se rechaza.

## Presupuesto de URL agotado

Cada catálogo y `robots.txt` consume presupuesto. En navegador cuentan el documento superior y
sus redirects; los subrecursos y subframes se abortan, JavaScript está desactivado y cualquier
método distinto de `GET`/`HEAD` hace fallar la captura. Aumenta de forma explícita
`MAX_URLS_PER_RUN` y `--url-budget` solo al mínimo justificable; no uses retries ciegos.
El argumento de la corrida no puede superar el máximo configurado y cero deshabilita la red.

## La salida está fuera del laboratorio

`--output` debe resolver dentro de `13-sales-knowledge-curator`, también después de seguir
symlinks. Usa una ruta relativa bajo `.local/`; `BL_LOOPS_ALLOW_EXTERNAL_WRITES=false` no se puede
anular en este laboratorio.

## `source_id duplicado en la corrida`

Dos archivos declararon la misma identidad editorial. Asigna a cada archivo un `source_id` único;
la ingesta se detiene antes de persistir o extraer claims para impedir sobrescrituras y evidencia
cruzada. No resuelvas la colisión cambiando solo el nombre del archivo.

## MarkItDown no está o devuelve vacío

Ejecuta `uv sync --all-groups` y `sales-curator doctor`. Solo se aceptan `.pdf` y `.docx`
dentro del inbox. Una extracción vacía, archivo cambiante, tamaño excesivo o derechos sin
retención/extracción falla cerrada. MarkItDown no garantiza OCR ni fidelidad de página.

## Ollama dice modelo ausente o salida inválida

Define `CURATOR_MODEL` con un modelo ya instalado y conserva `OLLAMA_BASE_URL` en loopback. No uses
una URL remota ni esperes fallback. Si una línea supera el tamaño de chunk, el documento requiere
preprocesamiento explícito. Si se excede `MAX_LLM_CHUNKS_PER_DOCUMENT`, aumenta la cuota solo tras
revisar el documento. JSON con fences, claves duplicadas, citas inexistentes o paráfrasis no
literales se rechaza y la corrida fallida conserva su `run_id` y JSONL.

## El navegador no inicia

```powershell
uv run crawl4ai-setup
uv run crawl4ai-doctor
```

No actives proxy, stealth, cookies o un perfil persistente como atajo. Revisa que el host esté en
allowlist y que exista un Chromium compatible dentro del entorno.

## `robots.txt no verificable` o denegado

El laboratorio no interpreta una caída, MIME extraño, redirect inseguro o codificación inválida
como permiso. No lo fuerces. Usa una API oficial, solicita permiso o conserva solo el enlace.

## Open Library y Google Books discrepan

El reporte conserva ofertas por proveedor. Compara ISBN, autor, fecha y edición; no fusiones por
título. Open Library `borrowable` no es descarga. Google Books preview o `ALL_PAGES` sin todas
las señales de dominio público tampoco lo es.

## NotebookLM no contiene el libro

Es intencional: el export actual contiene fichas, fuentes, guía y preguntas, con
`upload_performed=false`. Importa manualmente únicamente material que pueda transferirse a
Google. No automatices login ni conviertas un permiso local de lectura en permiso de subida.

## `release publish` rechaza candidato o hash

La demo termina en staging. Usa exactamente el `candidate_id` y `candidate_hash` impresos por
esa corrida. Si el staging cambió, reconstruye y revisa el nuevo diff; nunca reutilices una
aprobación.

## El JSONL no valida

Debe usar `lab_id=13-sales-knowledge-curator`, secuencia consecutiva, `run.started` al inicio y
un evento terminal solo después de publicar o fallar. Texto crudo malicioso o datos sensibles
invalidan la evidencia.

# Quickstart explicado

Todos los comandos se ejecutan en PowerShell desde la raíz del laboratorio. No muestres un
`.env` real ni pegues secretos, datos personales o textos protegidos en logs.

## 1. Preparar el entorno aislado

```powershell
cd C:\Users\criss\Desktop\Claude\BL_Loops\13-sales-knowledge-curator
uv sync --all-groups
npm --prefix frontend install
uv run sales-curator --version
uv run sales-curator doctor
```

`doctor` informa configuración y dependencias sin imprimir modelo, hosts de allowlist ni valores
sensibles. Para la captura web real, si Chromium aún no está preparado:

```powershell
uv run crawl4ai-setup
uv run crawl4ai-doctor
```

## 2. Ejecutar y publicar la demo local

```powershell
uv run sales-curator demo --fixture .\fixtures\corpus --reviewer operador-local --reason "Revision didactica del operador"
```

Resultado esperado: `state=staging`, un hueco, una fuente sindicada, una afirmación obsoleta, un
conflicto y los valores `run_id`, `candidate_id` y `candidate_hash`. El comando aprueba
únicamente los claims que pasan el gate técnico; no aprueba el paquete que acaba de construir.

Revisa el diff mostrado y copia literalmente los tres identificadores:

```powershell
$runId = Read-Host "run_id mostrado"
$candidateId = Read-Host "candidate_id mostrado"
$candidateHash = Read-Host "candidate_hash mostrado"
uv run sales-curator release publish --run "$runId" --candidate "$candidateId" --expected-hash "$candidateHash" --reviewer operador-local --reason "Aprobacion posterior del candidato revisado"
$releaseId = Read-Host "release_id publicado"
uv run sales-curator validate --release "$releaseId"
uv run sales-curator export-run --run "$runId"
```

Un hash viejo o un staging alterado falla. `current.json` cambia solo después del gate y conserva
los releases anteriores para rollback.

## 3. Importar un PDF o DOCX autorizado

Crea una carpeta como `.local/inbox/` y coloca allí una copia que la escuela pueda retener y
extraer. Copia la [plantilla de derechos](../../examples/document-rights.example.json):

```powershell
New-Item -ItemType Directory -Force .\.local\inbox | Out-Null
Copy-Item -LiteralPath .\examples\document-rights.example.json -Destination .\.local\rights-school.json
```

Edita la copia y reemplaza licencia, jurisdicción y evidencia. Los valores incluidos son
marcadores, no una autorización real; la plantilla mantiene `notebooklm_upload_allowed=false`.

Importa sin modificar el original:

```powershell
uv run sales-curator document import --source .\.local\inbox\libro.pdf --inbox .\.local\inbox --output .\.local\research\documents --title "Titulo verificado" --author "Autor verificado" --language es --rights .\.local\rights-school.json --topic ventas
```

El resultado contiene el hash original, la versión de MarkItDown, `content.md` y
`manifest.json`. Las líneas del Markdown son localizadores derivados; una cita por página
requiere comprobar el documento original.

## 4. Comparar extracción determinista y Ollama local

La auditoría usa el extractor determinista si no indicas otro. Para probar la ruta LLM con un
modelo que ya exista en Ollama:

```powershell
$env:CURATOR_MODEL="qwen3.5:4b"
$env:MAX_LLM_CHUNKS_PER_DOCUMENT="8"
uv run sales-curator audit --source .\fixtures\corpus --extractor deterministic
uv run sales-curator audit --source .\fixtures\corpus --extractor ollama
```

Ollama se limita a loopback, comprueba el modelo una vez, fragmenta por líneas con solapamiento y
exige JSON exacto. Cada claim debe citar una línea existente y contener un fragmento literal de
ella. Fences, claves duplicadas, `source_id` ajeno, paráfrasis no localizable o exceso de chunks
fallan; la corrida queda `failed` y conserva JSONL terminal. Nunca hay fallback cloud ni cambio de
modelo. Si el dominio real no se configuró, el comando usa la etiqueta técnica neutra
`sales-books-education`.

## 5. Autorizar una corrida bibliográfica

La autorización general ya fue concedida, pero el runtime falla cerrado hasta configurar cada
sesión. Sustituye la jurisdicción y ajusta la allowlist a los conectores que usarás:

```powershell
$jurisdiction = Read-Host "Escribe la jurisdiccion aprobada para esta investigacion"
if ([string]::IsNullOrWhiteSpace($jurisdiction)) { throw "La jurisdiccion es obligatoria" }
$env:NETWORK_ENABLED="true"
$env:BL_LOOPS_RUNTIME_NETWORK="true"
$env:BL_LOOPS_ALLOW_REAL_CONNECTORS="true"
$env:ALLOWED_DOMAINS="openlibrary.org,www.googleapis.com"
$env:MAX_URLS_PER_RUN="6"
$env:RESEARCH_JURISDICTION=$jurisdiction
$env:RESEARCH_LANGUAGES="en,es"
$env:RESEARCH_USER_AGENT="BL-Loops-SalesCurator/0.2 educational-research"
```

Consulta ambos catálogos:

```powershell
uv run sales-curator book research --title "SPIN Selling" --author "Neil Rackham" --jurisdiction "$jurisdiction" --language en --language es --provider open_library --provider google_books --url-budget 6 --authorize-network --output .\.local\research\books
```

El `report.json` diferencia catálogo, lectura, preview, préstamo y descarga completa. Open
Library se conserva como descubrimiento con derechos desconocidos. Google Books solo expone un
enlace de descarga cuando declara simultáneamente dominio público, `FULL_PUBLIC_DOMAIN` y PDF
disponible; aun así, la jurisdicción requiere revisión.

## 6. Capturar una página allowlisted

Incluye el host exacto en `ALLOWED_DOMAINS` y crea otra copia de la plantilla. Edita sus campos
según los derechos verificables de esa página; no reutilices automáticamente el permiso de un
libro:

```powershell
Copy-Item -LiteralPath .\examples\document-rights.example.json -Destination .\.local\rights-web.json
$approvedUrl = Read-Host "URL HTTPS aprobada y allowlisted"
uv run sales-curator web capture --url "$approvedUrl" --language es --rights .\.local\rights-web.json --url-budget 3 --authorize-network --output .\.local\research\web
```

Antes del navegador se valida HTTPS, DNS público, allowlist, presupuesto y `robots.txt`.
Crawl4AI se ejecuta headless, sin proxy, sesión persistente, stealth, formularios ni descargas.
JavaScript, subrecursos y subframes quedan bloqueados: esta captura obtiene el HTML estático y
puede omitir contenido que el sitio solo renderiza en cliente.
También se vuelve a validar la URL final.

## 7. Exportar paquetes manuales

Usa la ruta exacta del `report.json` bibliográfico:

```powershell
$reportPath = Read-Host "Ruta de report.json impresa por book research"
uv run sales-curator notebooklm export --report "$reportPath" --output .\.local\exports\notebooklm --max-sources 50
uv run sales-curator rag export --report "$reportPath" --output .\.local\exports\rag
```

NotebookLM recibe fichas Markdown, guía y preguntas; no se inicia sesión ni se sube nada. El
paquete RAG contiene metadatos JSONL y hashes, no el texto de libros restringidos. Copiarlo a otro
laboratorio es una acción manual posterior.

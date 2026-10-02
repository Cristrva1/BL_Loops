# Arquitectura

El runtime, no el LLM ni una página adquirida, controla permisos, presupuestos, transiciones y
publicación.

## Componentes

```mermaid
flowchart TB
    CLI[CLI local] --> CFG[Settings fail-closed]
    CFG --> FS[Ingesta local]
    CFG --> NP[NetworkPolicy]
    FS --> DOC[MarkItDown PDF/DOCX]
    FS --> DET[Extractor determinista]
    FS --> OLL[Ollama local opcional]
    NP --> HTTP[SafeHttpClient]
    HTTP --> OL[Open Library]
    HTTP --> GB[Google Books]
    HTTP --> PG[Project Gutenberg]
    HTTP --> IA[Internet Archive]
    NP --> ROB[robots.txt]
    ROB --> C4[Crawl4AI browser]

    OL --> REP[BookResearchReport]
    GB --> REP
    PG --> REP
    IA --> REP
    REP --> LIB[Library loop / dossier]
    LIB --> COPY[PDF legal opcional]
    REP --> NB[NotebookLM packet manual]
    REP --> RAG[RAG metadata packet]

    FS --> LEDGER[Source + Claim ledger]
    LEDGER --> REVIEW[Revisión de claims]
    REVIEW --> STAGE[Staging + diff]
    STAGE --> APPROVE[Aprobación posterior del hash]
    APPROVE --> RELEASE[KnowledgeRelease]
```

Los conectores producen artefactos locales. No inyectan automáticamente su contenido en una
corrida editorial ni saltan la revisión humana.

Ollama verifica el modelo una vez en `/api/tags`, deshabilita proxies y solo acepta loopback. Los
documentos se fragmentan de forma reproducible; `MAX_LLM_CHUNKS_PER_DOCUMENT` limita el trabajo
antes de llamar al modelo. La salida es JSON estricto y cada texto/localizador se comprueba contra
la fuente. Un fallo genera `run.failed` y JSONL terminal, sin reparación ni fallback.

## Política de red

La autorización exige todos estos controles:

1. `NETWORK_ENABLED=true`.
2. `BL_LOOPS_RUNTIME_NETWORK=true`.
3. `BL_LOOPS_ALLOW_REAL_CONNECTORS=true`.
4. `ALLOWED_DOMAINS` no vacío y `MAX_URLS_PER_RUN` positivo.
5. `--authorize-network` y `--url-budget` en esa corrida.
6. Jurisdicción escrita y lenguajes limitados a `en`/`es`.

`NetworkPolicy` acepta solo HTTPS/443 sin credenciales, resuelve DNS y rechaza direcciones no
globales. `SafeHttpClient` no hereda proxies ambientales, revalida cada redirect, limita MIME,
tamaño y número de URL. Una rama de catálogo puede fallar sin ocultar el resultado de la otra.

Para navegador, `robots.txt` debe recuperarse, ser texto válido y permitir el user-agent; cualquier
ambigüedad detiene la captura. Crawl4AI bloquea descargas, contextos persistentes, proxy, stealth,
iframes, formularios, capturas y PDF. JavaScript está desactivado: el interceptor permite solo el
documento superior mediante `GET`/`HEAD`, revalida y cuenta sus redirects, y aborta scripts, XHR,
fetch, WebSocket, service workers implícitos, estilos, imágenes, medios, fuentes y subframes. Por
ello la captura es deliberadamente estática y puede omitir contenido renderizado en cliente.

## Derechos y acceso

```text
rights_status = public_domain | open_license | explicit_permission | restricted | unknown
access_mode   = full_download | read_online | preview | borrow | catalog_only
```

Una URL de descarga solo cabe si hay `full_download`, derechos elegibles y evidencia. El método
`can_download_automatically` añade jurisdicción aprobada. `library research` descarga ese PDF al
laboratorio; préstamo, preview y hosts no confiables no se copian.

PDF/DOCX requiere `retention_allowed=true` y `extraction_allowed=true`. Derechos restringidos o
desconocidos nunca permiten redistribución ni subida a NotebookLM. Los hashes del original y de la
proyección demuestran identidad, no fidelidad editorial.

## Publicación en dos decisiones

1. Se revisa cada claim publicable sobre su `claim_identity_hash`.
2. `release build` crea staging y un diff sanitizado; no publica.
3. El operador revisa `candidate_id` y `candidate_hash` ya construidos.
4. `release publish` registra una aprobación posterior de ese hash, repite el gate y publica.
5. Si un byte del staging cambió, la aprobación deja de ser válida.

`claims.jsonl` contiene únicamente claims aprobados cuyo registro exacto pasa el gate y cuya
evidencia completa es redistribuible. `review-decisions.jsonl` y `candidate-approval.json` exportan
una proyección (`ReviewProjection`) con metadatos y `source_review_hash`, nunca `reason` ni
`conditions`. La última decisión exacta, ordenada por tiempo e identidad, es la vigente: un
`REJECTED` o `CHANGES_REQUESTED` posterior deja fuera el claim o bloquea `publish`.
No se modifica un claim después de su aprobación: si una sola evidencia carece de permiso, el
claim completo queda fuera hasta editarlo y revisarlo de nuevo. `sources.jsonl` conserva metadatos
y hashes de inventario, no el cuerpo de fuentes restringidas.

El hash editorial cubre texto, alcance, contexto, jurisdicción, vigencia, método, muestra,
supersesión, calidad, desafío, evidencia, versión y autor. Estado de revisión y timestamps de
runtime no cambian la identidad editorial.

## Persistencia

- SQLite: `.local/data/curator.sqlite`.
- Staging: `.local/data/staging/<run_id>/`.
- Releases: `.local/data/releases/<release_id>/` y `current.json`.
- Corridas: `.local/runs/<run_id>.jsonl`.
- Investigación y exports: la ruta relativa indicada por `--output`.
- Biblioteca: `.local/library/<work_id>/` e `index.json`. `library export` escribe Markdown fuera
  del laboratorio solo con `--authorize-export`; los PDF se quedan en `.local/`.

Cada release es autónomo y validable sin consultar SQLite. La publicación reubica el staging,
persiste SQLite en una transacción y solo entonces escribe `current.json`. Si SQLite falla, el
staging se restaura y la corrida vuelve a `staging`; un puntero ausente no anuncia el paquete.
Las tablas históricas se identifican por `(run_id, entity_id)`, por lo que una corrida no
sobrescribe otra. Todos los escritores de investigación resuelven symlinks y rechazan una salida
fuera de la raíz del laboratorio.

## Superficie visual y límites

El dashboard muestra estados reales de la auditoría editorial. Auditar, aprobar claims
publicables, construir staging y publicar el hash exacto del candidato son acciones de la
interfaz; el grafo no marca un nodo como hecho si el backend no llegó a ese estado.
MarkItDown, catálogos, Crawl4AI y el loop de biblioteca se lanzan por CLI. El dashboard lee
`.local/library/index.json` y pinta inventario, catálogos, gate de derechos y copia legal; no
dispara red. No hay embeddings, descarga masiva de obras protegidas, API de NotebookLM, CrewAI,
ArchiveBox, Langfuse ni escritura hacia otro laboratorio.

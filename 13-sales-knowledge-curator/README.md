# 13-sales-knowledge-curator

Máquina local para investigar, auditar y publicar conocimiento educativo de ventas con
procedencia. Su unidad central es la afirmación trazable: una cita demuestra de dónde salió una
idea, mientras la vigencia, independencia, derechos y aprobación se evalúan por separado.

## Estado implementado

- Auditoría local de Markdown/TXT, claims, huecos, sindicación y conflictos.
- Extracción determinista por defecto o extracción funcional con un modelo Ollama local explícito.
- Revisión humana de claims y del candidato de release sobre hashes exactos.
- Staging, publicación atómica, validación, rollback y JSONL sanitizado.
- Importación local de PDF/DOCX autorizados con MarkItDown `0.1.7`.
- Investigación bibliográfica de solo lectura en Open Library y Google Books.
- Captura estática estrecha de una página allowlisted con Crawl4AI `0.9.2`, JavaScript apagado y
  `robots.txt` fail-closed.
- Paquetes locales para importación manual en NotebookLM y para un RAG portable.

La red permanece apagada por defecto. El usuario autorizó esta capacidad, pero cada ejecución
todavía exige triple opt-in de configuración, allowlist, presupuesto, jurisdicción escrita y
`--authorize-network`. El valor concreto de la jurisdicción y el dominio real no se inventa.

## Preparar y diagnosticar

```powershell
uv sync --all-groups
npm --prefix frontend install
uv run sales-curator --version
uv run sales-curator doctor
```

## Demostración editorial local

```powershell
uv run sales-curator demo --fixture .\fixtures\corpus --reviewer operador-local --reason "Revision didactica del operador"
```

La demo se detiene en `state=staging` y muestra `run_id`, `candidate_id`, `candidate_hash` y un
diff sanitizado. No publica implícitamente. Para aprobar ese candidato y publicarlo:

```powershell
uv run sales-curator release publish --run <run_id> --candidate <candidate_id> --expected-hash <candidate_hash> --reviewer operador-local --reason "Aprobacion posterior del staging revisado"
uv run sales-curator validate --release <release_id>
uv run sales-curator export-run --run <run_id>
```

Ruta Ollama opcional, sin fallback cloud:

```powershell
$env:CURATOR_MODEL="qwen3.5:4b"
uv run sales-curator audit --source .\fixtures\corpus --extractor ollama
```

Los recorridos de PDF/DOCX, catálogos, navegador y paquetes están explicados en
[docs/humano/QUICKSTART.md](docs/humano/QUICKSTART.md).

## Dashboard

```powershell
uv run uvicorn sales_curator.api.main:app --host 127.0.0.1 --port 8013 --reload
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5174`. El grafo representa la corrida editorial del backend; los
conectores nuevos producen artefactos por CLI y todavía no son nodos interactivos del dashboard.

## Límites deliberados

- No descarga automáticamente copias de libros ni convierte préstamo, preview o lectura en línea
  en permiso de copia.
- No inicia sesión ni sube archivos a NotebookLM.
- No llama ni escribe en `09-agentic-rag`; los paquetes se copian o importan manualmente.
- No usa embeddings, CrewAI, ArchiveBox ni Langfuse.
- No evade paywalls, DRM, CAPTCHA, autenticación, términos ni `robots.txt`.

## Atribución

La captura web incluye software desarrollado por **UncleCode** como parte de
[Crawl4AI](https://github.com/unclecode/crawl4ai). Se conserva esta atribución conforme al
[archivo de licencia del proyecto](https://raw.githubusercontent.com/unclecode/crawl4ai/main/LICENSE).

Empieza el aprendizaje en [docs/humano/README.md](docs/humano/README.md). Las reglas portables
están en [AGENTS.md](AGENTS.md).

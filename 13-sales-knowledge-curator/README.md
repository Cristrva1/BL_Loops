# 13 · Curador de conocimiento de ventas

> **Pregunta:** ¿cómo convertir una biblioteca débil en un paquete de conocimiento trazable, revisado
> por una persona y copiable, sin declarar que un modelo conoce la verdad?
> **Nivel:** 4 · **Tiempo:** ~90 min · **Necesita Ollama:** opcional (el extractor por defecto es determinista)

Máquina local para auditar, contrastar y publicar conocimiento educativo de ventas con procedencia.
Su unidad central es la **afirmación trazable** (*claim*): una cita demuestra de dónde salió una idea,
mientras la vigencia, la independencia, los derechos y la aprobación se evalúan por separado. Nada se
publica sin que una persona apruebe el **hash exacto** del candidato.

## Ejecutar en 5 minutos

Desde la raíz de BL_Loops:

```powershell
Set-Location .\13-sales-knowledge-curator
uv sync --all-groups
uv run sales-curator doctor
uv run sales-curator demo --fixture .\fixtures\corpus --reviewer operador-local --reason "Revision didactica del operador"
```

La demo se detiene en `state=staging` e imprime `run_id`, `candidate_id` y `candidate_hash`. Para
aprobar **ese** candidato y publicarlo:

```powershell
uv run sales-curator release publish --run <run_id> --candidate <candidate_id> --expected-hash <candidate_hash> --reviewer operador-local --reason "Aprobacion posterior del staging revisado"
uv run sales-curator validate --release <release_id>
uv run sales-curator export-run --run <run_id>
```

## Qué deberías ver

```text
run_id=run_…
state=staging
sources=10 claims=9
conflicts=1 gaps=2
candidate_diff={"conflict_count":1,"excluded_claim_ids":[…6 claims…],"included_claim_ids":["clm-ask-budget","clm-discovery-duration","clm-sunday-close"],…}
```

De nueve afirmaciones, solo tres llegan al candidato: una disputa de precio, una inyección, una
afirmación comercial sin método, una práctica obsoleta y otra con derechos dudosos quedan fuera. El
recorrido explicado de cada una está en [EXAMPLES.md](docs/humano/EXAMPLES.md).

## Estado implementado

- Auditoría local de Markdown/TXT, claims, huecos, sindicación y conflictos.
- Extracción determinista por defecto o extracción con un modelo Ollama local explícito.
- Revisión humana de claims y del candidato de release sobre hashes exactos.
- Staging, publicación atómica, validación, rollback y JSONL sanitizado.
- Importación local de PDF/DOCX autorizados con MarkItDown `0.1.7`.
- Investigación bibliográfica en Open Library, Google Books, Project Gutenberg e Internet Archive.
- Loop acotado sobre fichas de `Libros`: dossier local y descarga PDF solo con evidencia legal.
- Captura estática estrecha de una página allowlisted con Crawl4AI `0.9.2`, JavaScript apagado y
  `robots.txt` fail-closed.
- Paquetes locales para importación manual en NotebookLM y para un RAG portable.

La red permanece apagada por defecto. El usuario autorizó esta capacidad, pero cada ejecución todavía
exige triple opt-in de configuración, allowlist, presupuesto, jurisdicción escrita y
`--authorize-network`. El valor concreto de la jurisdicción y el dominio real no se inventa.

Ruta Ollama opcional, sin fallback cloud:

```powershell
$env:CURATOR_MODEL = "qwen3.5:4b"
uv run sales-curator audit --source .\fixtures\corpus --extractor ollama
Remove-Item Env:CURATOR_MODEL
```

## Dashboard

```powershell
uv run uvicorn sales_curator.api.main:app --host 127.0.0.1 --port 8013 --reload
npm --prefix frontend install
npm --prefix frontend run dev        # abre http://127.0.0.1:5174
```

El grafo editorial pinta estados reales del backend. El panel de biblioteca lee
`.local/library/index.json` y no dispara red. El loop de fichas se lanza por CLI.

## Mapa del laboratorio

| Ruta | Para qué sirve |
|---|---|
| `backend/src/sales_curator/` | Dominio (ingesta, extracción, verificación, política), almacenamiento, releases, conectores y API |
| `backend/tests/` | Pruebas herméticas: no necesitan red ni Ollama |
| `fixtures/corpus/` | Diez fuentes sintéticas, cada una con una trampa editorial distinta |
| `fixtures/library/` | Fichas de ejemplo para el loop de biblioteca |
| `contracts/generated/` | JSON Schema de claims, fuentes, conflictos, releases y eventos |
| `frontend/` | Dashboard React Flow con SSE |
| `docs/humano/` | Manual de aprendizaje; el runtime nunca lo lee |
| `.local/` | SQLite, releases, corridas y artefactos (ignorado por Git) |

## Aprende paso a paso

1. [Guía del laboratorio](docs/humano/README.md): estados de una afirmación y dos carriles.
2. [Inicio rápido](docs/humano/QUICKSTART.md): todos los recorridos con sus comandos.
3. [Ejemplos resueltos](docs/humano/EXAMPLES.md): la demo editorial completa con salidas reales.
4. [Ejercicios](docs/humano/EXERCISES.md): práctica con soluciones plegables.
5. [Arquitectura](docs/humano/ARCHITECTURE.md), [metodología](docs/humano/METHODOLOGY.md),
   [evaluación](docs/humano/EVALUATION.md) y [diagnóstico](docs/humano/TROUBLESHOOTING.md).

**Viene de:** [09-agentic-rag](../09-agentic-rag/README.md), cuyo agente sufre un corpus débil.
**Sigue con:** [14-local-code-hermes](../14-local-code-hermes/README.md) o los estudios 22–24.

## Límites deliberados

- No convierte préstamo, preview, lectura en línea ni “un PDF en la web” en permiso de copia. Solo
  descarga si el catálogo marca `full_download` con derechos elegibles y evidencia.
- No inicia sesión ni sube archivos a NotebookLM.
- No llama ni escribe en `09-agentic-rag`; los paquetes se copian o importan manualmente.
- No usa embeddings, CrewAI, ArchiveBox ni Langfuse.
- No evade paywalls, DRM, CAPTCHA, autenticación, términos ni `robots.txt`.

## Atribución

La captura web incluye software desarrollado por **UncleCode** como parte de
[Crawl4AI](https://github.com/unclecode/crawl4ai). Se conserva esta atribución conforme al
[archivo de licencia del proyecto](https://raw.githubusercontent.com/unclecode/crawl4ai/main/LICENSE).

Las reglas portables para futuras sesiones de agentes de código están en [AGENTS.md](AGENTS.md).

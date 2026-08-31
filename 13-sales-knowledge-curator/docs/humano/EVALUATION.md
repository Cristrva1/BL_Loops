# Evaluación

## Gate técnico

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q backend/src backend/tests
npm --prefix frontend test
npm --prefix frontend run build
uv run sales-curator doctor
```

Después se ejecutan la demo, publicación exacta, validación y exportación descritas en el
Quickstart. La investigación web real es una prueba separada: no se necesita para declarar verde
el gate determinista. La captura live ya realizada usó jurisdicción `TEST`; no cuenta como
decisión legal ni como valor de configuración real.

## Casos predictivos

| Área | Señal de aprobado |
|---|---|
| Triple opt-in | Cada gate ausente detiene la red antes de I/O |
| SSRF/redirect | HTTP, credenciales, IP privada y salida de allowlist se rechazan |
| Catálogos | Fallo parcial visible; préstamo/preview nunca producen descarga |
| Google Books | Solo todas las señales de dominio público exponen `download_url` |
| Documento | Conserva original/hash; path escape y extracción vacía fallan |
| Ollama local | Modelo verificado una vez; chunk cap, JSON y cita literal fallan cerrados |
| Web | `robots.txt` verificado, URL final allowlisted, solo Markdown/manifiesto |
| NotebookLM | `upload_performed=false`, grupos de máximo 50 fuentes |
| RAG portable | Metadatos y hashes; no texto de obra restringida |
| Claims | Conflictos tipados y supersesión explícita, no solo mismo tema |
| Identidad | Todo campo editorial cambia el hash; estado/timestamps no |
| Staging | No mueve `current.json` ni implica aprobación del candidato |
| Publicación | Aprobación posterior exacta; manipulación invalida el paquete |
| Historia | IDs iguales se conservan de forma independiente por corrida |

## Métricas editoriales

Se mantienen `citation_integrity`, huecos, conflictos, sindicación, abstenciones y claims
aprobados. Para investigación se añaden ofertas por proveedor/modo de acceso, ramas fallidas,
bytes, URL consumidas y artefactos con hash. Ningún promedio compensa un gate de red, derechos o
aprobación fallido.

## Criterio de aprobado

- Los comandos documentados existen y `--help` coincide con su sintaxis.
- Un PDF/DOCX autorizado produce una derivación trazable sin modificar el original.
- `audit --extractor ollama` conserva localizadores válidos o produce `run.failed`, sin fallback.
- Un reporte real o simulado conserva jurisdicción, idioma, proveedor, acceso y derechos.
- Una captura solo ocurre con política y robots válidos.
- NotebookLM y RAG se exportan localmente sin efectos externos.
- La demo se detiene en staging y la publicación requiere el hash posterior exacto.
- El release se valida de forma autónoma y el JSONL queda sanitizado.
- No hubo cloud LLM, telemetría, PII, descarga indebida ni escritura en otro laboratorio.

Esto verifica la máquina y sus límites. No demuestra que una obra concreta sea reutilizable ni
que el corpus real de ventas ya esté completo o aprobado.

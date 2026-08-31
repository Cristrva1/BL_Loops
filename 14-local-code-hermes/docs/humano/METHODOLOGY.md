# Metodología

## Pregunta del experimento

¿Hermes puede reparar el mismo proyecto sintético que OpenCode y Claude Code, desde el mismo SHA, con el mismo modelo, contexto, hardware y permisos? Este laboratorio ya puede producir una corrida Hermes; todavía no produce una comparación oficial.

## Cohortes

- Primaria: `qwen3.5:9b`, alias `local-code-9b-64k`, 65,536 tokens.
- Fallback: `qwen3.5:4b` con los mismos 65,536 tokens y resultados separados.
- Una ejecución a 32k, con otro runtime o con otro SHA no pertenece a la misma cohorte.
- El 27B no se usa como agente cotidiano; una prueba posterior sería adversarial, aislada y sin escritura.

## Secuencia causal

1. Congelar caso, harness, permisos, modelo, contexto y `HEAD`.
2. Cerrar o liberar cualquier modelo de LM Studio y capturar el estado vacío.
3. Aplicar el perfil autorizado de Ollama, crear el alias y capturar digest de alias/fuente.
4. Ejecutar preflight formal; un worktree sucio bloquea.
5. Si se necesita observar el flujo antes de una release limpia, usar el override explícito de smoke; no puntuarlo.
6. Ejecutar `B-CODE-003` en Hermes con Docker sin red.
7. Verificar workspace, tests, `ollama ps` y solo el delta de logs.
8. Exportar JSONL, validarlo e importar su resumen en el comparador.
9. Para la cohorte oficial, repetir tres veces por cliente y conservar la autorización humana contemporánea.

## Dos afirmaciones independientes

- `local_inference`: la generación se dirigió al endpoint Ollama de loopback y el modelo observado fue el alias esperado.
- `zero_egress`: una política o captura autorizada demuestra que el cliente y sus hijos no abrieron conexiones no-loopback.

El sandbox establece `--network=none` para los comandos del agente, pero el runner no inventa una prueba de firewall para el proceso padre. Por eso la corrida actual permanece `scored=false` y `comparable=false` aunque el fixture pase.

## Evidencia humana

Los flags de evidencia aceptan IDs con namespace `FW-` y `OLLAMA-`, no archivos ni secretos. El JSONL guarda únicamente su SHA-256 como referencia. La evidencia de firewall, perfil, digest y estado de los runtimes debe existir fuera del JSONL antes de llamar formal al preflight.

## Límites

Una corrida `run.completed` indica que el proceso del runner terminó y que su resultado fue serializado; no equivale a éxito funcional ni a score oficial. La clasificación necesita que todas las observaciones exigidas estén verificadas y que las repeticiones sean comparables.

## Fuentes oficiales actuales

- Ollama: contexto, Modelfile e integración local en `https://docs.ollama.com/`.
- Hermes: proveedores locales en `https://hermes-agent.nousresearch.com/docs/integrations/providers`.
- LM Studio: API y controles de carga en `https://lmstudio.ai/docs/`.
- llama.cpp: servidor y parámetros en `https://github.com/ggml-org/llama.cpp/tree/master/tools/server`.

Las capacidades y versiones se revalidan antes de cada cohorte. Las fuentes externas justifican parámetros; no sustituyen evidencia producida en este equipo.

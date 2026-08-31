# Metodología

## Pregunta del experimento

¿Hermes puede reparar el mismo proyecto sintético que OpenCode y Claude Code, desde el mismo SHA, con el mismo modelo, contexto, hardware y permisos?

No se responde aún. Primero se elimina la ambigüedad del entorno con `F-LOCAL-CODE-004`.

## Cohortes

- Primaria: `qwen3.5:9b`, alias `local-code-9b-64k`, 65,536 tokens.
- Fallback: `qwen3.5:4b` con los mismos 65,536 tokens y resultados separados.
- Una ejecución a 32k, con otro runtime o con otro SHA no pertenece a la misma cohorte.
- El 27B no se usa como agente cotidiano; una prueba posterior sería adversarial, aislada y sin escritura.

## Secuencia causal

1. Congelar el caso, harness, permisos, modelo, contexto y `HEAD`.
2. Ejecutar preflight sin alterar el host.
3. Liberar conflictos y aplicar el perfil del servidor solo con autorización.
4. Calentar el modelo con una ronda no puntuada.
5. Ejecutar `B-CODE-003` tres veces por cliente.
6. Verificar artefactos, tests, métricas de recursos y red.
7. Exportar JSONL y comparar solo corridas compatibles.

No se baja el contexto para conseguir un verde. Si el modelo no cabe, se cambia de cohorte conservando 64k.

## Dos afirmaciones independientes

- `local_inference`: toda generación se dirigió al Ollama de loopback.
- `zero_egress`: una captura o política autorizada demuestra que el cliente y sus procesos hijos no abrieron conexiones no-loopback.

Una conexión externa invalida cero egress, pero por sí sola no prueba qué contenido se transmitió.

## Evidencia humana

Los flags `--firewall-proof-id` y `--server-profile-proof-id` aceptan IDs con namespace `FW-` y `OLLAMA-`, no archivos ni secretos. El JSONL guarda únicamente su SHA-256 como referencia y nunca el ID original. La evidencia se obtiene y custodia fuera del JSONL; el harness no configura firewall ni puede certificar por sí solo un servidor ya iniciado.

## Fuentes oficiales actuales

- Ollama: contexto, FAQ, Modelfile e integración de clientes en `https://docs.ollama.com/`.
- Hermes: proveedores locales en `https://hermes-agent.nousresearch.com/docs/integrations/providers`.
- LM Studio: API y controles de carga en `https://lmstudio.ai/docs/`.
- llama.cpp: servidor y parámetros en `https://github.com/ggml-org/llama.cpp/tree/master/tools/server`.

Las capacidades y versiones deben revalidarse antes de una cohorte viva. Las fuentes externas justifican parámetros; no sustituyen evidencia producida en este equipo.

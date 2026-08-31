# Diagnóstico de fallos

## El preflight devuelve 2

Es `run.blocked`: abre el JSONL y busca nodos con `blocking=true`. No repitas el gate hasta identificar una causa concreta.

## `git.head` queda bloqueado como `worktree_dirty`

Es intencional. El gate captura el SHA y solo cuenta entradas, sin guardar nombres de archivos. El benchmark formal no puede continuar. Para observar el flujo de desarrollo existe `--allow-dirty-worktree`, que deja el bloqueo visible y desactiva score/comparabilidad; no lo uses para una release.

## `ollama.model` indica `command_nonzero` o `model_digest_unverified`

El alias `local-code-9b-64k` puede no existir, no coincidir con `qwen3.5:9b` o no devolver el mismo digest. Ejecuta `ollama show local-code-9b-64k --modelfile` y compara de forma read-only; no guardes la salida completa.

## `lmstudio.conflict` está bloqueado

Hay un modelo cargado o el estado no pudo determinarse. Usa la interfaz autorizada para liberar la sesión y confirma `lms ps --json` vacío. El fallback de procesos solo cuenta runtimes LM Studio identificables y bloquea si no puede identificar un `llama-server` sin ruta.

## `sandbox_image_unavailable` o Docker falla

Comprueba `docker info` y que la imagen esté instalada localmente. El runner no hace `pull`. Revisa que el contenedor tenga `--network=none`, capacidades eliminadas, no escalada y únicamente el workspace montado. No uses `--privileged`, volúmenes adicionales ni `docker_extra_args` de red.

## `hermes_process_failed` o `usage_report_invalid`

La corrida conserva solo código de salida, timeout y un digest efímero de salida. Revisa el proceso de forma interactiva sin copiar stdout/stderr al JSONL. Verifica que la configuración temporal use `provider: custom`, el endpoint Ollama `/v1` y el alias correcto. El parser acepta los contadores de Hermes (`input_tokens`/`output_tokens`) y los normaliza a campos internos.

## `runtime_identity_unverified`

`ollama ps` no mostró el alias con `100% GPU` y contexto 65,536. No confundas `ollama show` o el contexto declarado del Modelfile con el contexto efectivo de la carga.

## `ollama_runtime_errors`

El delta de logs observó truncación de prompt o HTTP 500. Los mensajes históricos no se mezclan con la corrida porque se toma un offset antes de iniciar Hermes. La ejecución no es comparable hasta explicar y corregir el error.

## RAM o VRAM insuficiente

El preflight mide margen antes de cargar el modelo. Cierra únicamente cargas autorizadas y vuelve a medir. Bajar a 32k cambia la cohorte; el fallback permitido mantiene 64k con un modelo menor.

## Falta evidencia de firewall o perfil

En modo formal son requisitos. Los identificadores deben comenzar con `FW-` u `OLLAMA-`; el JSONL conserva solo su hash. Referencian evidencia ya obtenida, no activan reglas ni prueban variables por sí solos.

## El JSONL no valida

Comprueba UTF-8, newline final, secuencias consecutivas, único `run_id`, lifecycle completo, identidad de caso/variante y ausencia de stdout, prompts, respuestas, rutas o secretos. `hermes-run-validate` despacha automáticamente preflight o benchmark por `case_id`.

## El verificador del fixture falla

- `changed_files_mismatch`: faltó cambiar uno de los dos archivos permitidos o cambió otro.
- `required_tests_missing`: no están las cuatro pruebas exigidas.
- `unittest_failed`: la prueba visible aún falla.
- `hidden_semantic_check_failed`: alguna frontera 0/25/100, negativa o mayor a 100 no cumple el contrato.
- `test_quality_check_failed`: un método requerido no ejercita su caso o no detecta el mutante.

El proyecto fuente inicial debe fallar: contiene el bug intencional.

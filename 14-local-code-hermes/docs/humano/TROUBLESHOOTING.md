# Diagnóstico de fallos

## El preflight devuelve 2

Es `run.blocked`: abre el JSONL y busca nodos con `blocking=true`. No repitas el gate hasta identificar una causa concreta.

## `ollama.model` indica `command_nonzero`

El alias `local-code-9b-64k` puede no existir o el servidor puede no responder. No lo crees durante una sesión activa. Cuando el operador autorice y haya recursos, usa el `Modelfile` del laboratorio.

## `lmstudio.conflict` está bloqueado

Hay un modelo cargado o el estado no pudo determinarse. No descargues ni detengas procesos desde este laboratorio. Termina primero el trabajo que use LM Studio y libera el modelo de forma explícita.

## `git.head` no existe

El repositorio o la copia evaluada no tiene un commit de partida. El modo exploratorio puede continuar como diagnóstico, pero el formal queda bloqueado y no hay benchmark comparable. No crees un commit solo para silenciar el gate sin decisión del propietario.

## RAM o VRAM insuficiente

El preflight mide margen antes de cargar el modelo. Cierra únicamente cargas que el operador autorice y vuelve a medir. Bajar a 32k cambia el experimento; el fallback permitido mantiene 64k con un modelo menor.

## Falta evidencia de firewall o perfil

En modo formal son requisitos. Los identificadores CLI deben comenzar con `FW-` u `OLLAMA-`; el JSONL conserva solo su hash. Referencian evidencia ya obtenida, no activan reglas ni prueban variables. No inventes un ID.

## El JSONL no valida

Comprueba que:

- sea UTF-8, una línea compacta por evento y newline final;
- empiece en `run.started`;
- tenga secuencias consecutivas y un único `run_id`;
- termine exactamente una vez;
- permanezca dentro de `.local/runs/`.

## El verificador del fixture falla

- `changed_files_mismatch`: faltó cambiar uno de los dos archivos permitidos o cambió otro.
- `required_tests_missing`: no están las cuatro pruebas exigidas.
- `unittest_failed`: la prueba visible aún falla.
- `hidden_semantic_check_failed`: alguna frontera 0/25/100, negativa o mayor a 100 no cumple el contrato.
- `test_quality_check_failed`: un método requerido no ejercita su caso o no detecta el mutante.

El proyecto inicial debe fallar: contiene el bug intencional.

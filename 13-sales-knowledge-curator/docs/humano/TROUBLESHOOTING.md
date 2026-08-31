# Diagnóstico

## El dashboard no carga datos

El frontend en `5174` espera el API en `8013`. Si Uvicorn no está en ese puerto, verás el mensaje de backend ausente. No se fabrica un grafo decorativo.

## `release build` dice que no hay afirmaciones aprobadas

El corte no publica desde `review_pending` sin decisiones humanas. Ejecuta `sales-curator claims list --run <id>` y aprueba con `--expected-hash`. El demo lo hace como operador local.

## Una fuente vacía “desaparece”

No desaparece: queda `quarantine_status=empty` y un `GapRecord`. Si vieras conocimiento viejo en su lugar, sería un fallo del gate. Ábrelo como error, no como vigencia.

## Quiero activar la red

`NETWORK_ENABLED=true` no basta. El adaptador de la fase 1 lanza `NetworkDisabled` porque no hay crawler ni allowlist operativa. Eso es deliberado.

## Ollama no responde

El demo determinista no lo necesita. Si configuras `CURATOR_MODEL` y el modelo no está, el extractor LLM debe decirlo. Nunca se cambia de modelo ni se llama a un proveedor de pago.

## El JSONL no importa

Debe tener `lab_id=13-sales-knowledge-curator`, secuencia consecutiva, `run.started` al inicio y un evento terminal. Las líneas vacías o el texto crudo de inyección invalidan la corrida.

## Hash alterado en el release

Alguien editó un archivo dentro de `releases/<id>/`. Los releases son inmutables. Vuelve a publicar o haz rollback; no parches a mano el paquete publicado.

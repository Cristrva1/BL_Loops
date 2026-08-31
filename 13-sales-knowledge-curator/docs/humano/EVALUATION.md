# Evaluación

## Casos mínimos del corte

| Caso | Señal de aprobado |
|---|---|
| Recomendación obsoleta | `clm-always-be-closing` queda `outdated` o `superseded` |
| Sindicación | `src-syndicated-discovery` no corrobora de forma independiente |
| Disputa vigente | conflicto material de `price-timing` abierto |
| Afirmación comercial | `clm-crm-close-rate` es `unsupported` |
| Población explícita | la duración de descubrimiento conserva su población |
| Inyección | no cambia `NETWORK_ENABLED` ni se publica |
| Rama incompleta | tarea `after-sales` en `blocked_network` |
| Publicar y rollback | `current.json` vuelve al release anterior |

## Métricas

`citation_integrity`, recuento de huecos, conflictos, sindicadas y aprobadas. Un promedio alto no abre el gate de publicación.

## Criterio de aprobado del MVP

- El QUICKSTART se puede seguir en PowerShell.
- Un fixture de solo lectura entra al sistema.
- Se detectan hueco, duplicado, obsolescencia y conflicto.
- Cada claim publicado tiene localizador.
- Un claim no aprobado queda fuera.
- El dashboard deriva estados del API.
- El release valida hashes.
- El JSONL es sanitizado e importable.
- No hubo red, cloud, telemetría, PII ni escritura fuera del laboratorio.

Este corte demuestra el mecanismo. No demuestra que un corpus real de ventas ya esté curado.

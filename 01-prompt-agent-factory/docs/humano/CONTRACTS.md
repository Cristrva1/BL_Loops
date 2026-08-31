# Cómo leer los contratos generados

Los archivos de `../../contracts/generated/` son JSON Schema producidos desde Pydantic. No se editan a mano.

```powershell
uv run factory-export-schemas
```

## Mapa rápido

| Archivo | Valida | Pregunta que responde |
|---|---|---|
| `prompt-spec.schema.json` | `PromptSpec` | ¿La instrucción es completa y verificable? |
| `agent-spec.schema.json` | `AgentSpec` | ¿El agente tiene autoridad y parada explícitas? |
| `skill-spec.schema.json` | `SkillSpec` | ¿El procedimiento es portable y auditable? |
| `run-record.schema.json` | `RunRecord` | ¿La corrida puede compararse sin conexión en vivo? |

## Qué buscar dentro de un schema

- `required`: campos que no pueden omitirse.
- `type`: forma válida del dato.
- `enum`: opciones cerradas.
- `minimum` / `maximum`: límites numéricos.
- `pattern`: formato textual obligatorio.
- `additionalProperties: false`: rechazo de campos inventados.
- `$defs`: piezas reutilizadas por el contrato principal.

## Regla de sincronización

El orden correcto de cambio es:

```text
Prueba que falla -> modelo Pydantic -> fábrica/API -> TypeScript -> schema generado -> documentación
```

Si se edita primero el JSON Schema, la siguiente regeneración borrará el cambio.

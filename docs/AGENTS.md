# Reglas de documentación para BL_Loops

El `AGENTS.md` de la raíz es la autoridad operativa. Este archivo solo añade reglas para trabajar dentro de `docs/`.

## Clasificación

- `INDEX.md`, `PLAN_MAESTRO_DIDACTICO.md` y `CASOS_DE_EVALUACION.md` contienen navegación, decisiones o contratos transversales vigentes.
- `humano/maestro/` contiene la explicación didáctica canónica del repositorio maestro.
- `humano/sistema.md` conserva la intención primaria del usuario.
- Los demás archivos bajo `humano/` son fuentes o referencias no vinculantes salvo promoción explícita.

## Edición

- Preservar los documentos humanos recibidos; no reescribirlos para uniformarlos sin solicitud explícita.
- Al aprobar una decisión, actualizar primero el plan o contrato correspondiente, después la guía humana afectada y finalmente `INDEX.md`.
- Usar español claro, diagramas Mermaid pequeños, ejemplos concretos y comandos PowerShell explicados.
- Distinguir siempre comportamiento implementado, límite deliberado, propuesta y trabajo futuro.
- Mantener enlaces relativos válidos.
- No colocar código, configuración ejecutable, schemas, fixtures, resultados o secretos dentro de `humano/`.
- Ningún runtime puede importar, parsear o necesitar un archivo de `docs/humano/`.

## Verificación

Para cambios documentales, comprobar como mínimo enlaces locales, coherencia con el `AGENTS.md` raíz y ausencia de dependencias runtime hacia `docs/humano/`.

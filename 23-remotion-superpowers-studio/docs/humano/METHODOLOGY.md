# Metodología: 23-remotion-superpowers-studio

## Principios Didácticos y Técnicos

1. **Audio-First y Cuadros Fijos**:
   - En la producción audiovisual profesional, el audio y el guión determinan la duración visual.
   - Remotion opera estrictamente sobre una escala discreta de enteros (`frame: 0, 1, 2...`). Esto evita desincronizaciones acumulativas causadas por variaciones en `performance.now()`.
2. **Superpowers Pattern**:
   - Siguiendo la filosofía del plugin `remotion-superpowers`, el agente de IA no intenta programar un archivo binario de video directamente; en su lugar, manipula un árbol de props tipadas que React renderiza sin fallos sintácticos.
3. **Aislamiento Total**:
   - Este laboratorio es autosuficiente: posee su propio `package.json`, su propio `node_modules` y su propio entorno virtual de Python (`.venv`), cumpliendo con las directrices de portabilidad de `BL_Loops`.

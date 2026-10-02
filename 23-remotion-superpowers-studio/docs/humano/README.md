# Laboratorio 23: Remotion Superpowers Studio (IA Local)

Bienvenido al Laboratorio 23 de `BL_Loops`. En este laboratorio exploramos y ponemos a prueba **Remotion** (`remotion-dev/remotion`) junto con el enfoque de producción agéntica **Remotion Superpowers** (`DojoCodingLabs/remotion-superpowers`), integrados con **IA Local (Ollama: `qwen3.5:9b`)**.

## Objetivo Didáctico
1. Dominar el paradigma de **video como código React**: representar líneas de tiempo como árboles de componentes, estados y hooks (`useCurrentFrame`, `interpolate`, `spring`).
2. Implementar el patrón **Remotion Superpowers**:
   - Medición y temporización basada en fotogramas absolutos: $N = \text{segundos} \times \text{FPS}$.
   - Orquestación desacoplada: el modelo local diseña el guión y los intervalos temporales; React se encarga del renderizado visual determinista.
3. Compilar video MP4 a 1080p 30 FPS usando `@remotion/cli` y Chromium Headless sin costos cloud.
4. Inspección visual y exportación estandarizada en formato JSONL para el benchmark central.

## Mapa de Documentos
- [Inicio Rápido](QUICKSTART.md): Guía de comandos PowerShell para instalación y render.
- [Arquitectura](ARCHITECTURE.md): Nodos, transiciones y flujo entre Ollama y Remotion.
- [Metodología](METHODOLOGY.md): Filosofía de diseño y cálculo de fotogramas.
- [Ejercicios](EXERCISES.md): Desafíos progresivos para el estudiante.
- [Diagnóstico](TROUBLESHOOTING.md): Errores habituales y mitigación.
- [Evaluación](EVALUATION.md): Criterios de aprobado del caso `EVAL-REMOTION-001`.

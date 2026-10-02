# Laboratorio 22: HyperFrames Video Studio (IA Local)

Bienvenido al Laboratorio 22 de `BL_Loops`. En este laboratorio exploramos y ponemos a prueba **HyperFrames** (`heygen-com/hyperframes`), un framework moderno y abierto para crear videos a partir de estándares web (HTML, CSS y JavaScript) con renderizado determinista cuadro a cuadro.

## Objetivo Didáctico
1. Comprender la diferencia entre video generativo por difusión y **video basado en código determinista** (HTML/CSS + GSAP).
2. Orquestar un pipeline audiovisual completo con **IA Local (Ollama: `qwen3.5:9b`)**, donde el modelo actúa como Director Audiovisual, estructurando el guión, desglosando las escenas y codificando la composición HTML.
3. Usar el mismo HyperFrames para producir un video educativo completo que explica:
   - Qué es HyperFrames.
   - Su arquitectura declarativa con atributos `data-start` y `data-duration`.
   - Cómo utilizar el CLI (`init`, `preview`, `render`).
   - Qué capacidades ofrece (overlays, explainers, transiciones, audio LUFS).
4. Aprender a diagnosticar el entorno de renderizado (Chromium Headless Shell y FFmpeg).

## Mapa de Documentos
- [Inicio Rápido](QUICKSTART.md): Comandos PowerShell explicados paso a paso.
- [Arquitectura](ARCHITECTURE.md): Nodos, transiciones y contrato entre Ollama y HyperFrames.
- [Metodología](METHODOLOGY.md): Decisiones técnicas y límites del framework.
- [Ejercicios](EXERCISES.md): Desafíos básico, intermedio y avanzado.
- [Diagnóstico](TROUBLESHOOTING.md): Errores comunes y soluciones.
- [Evaluación](EVALUATION.md): Criterios de aprobado y exportación JSONL.

# Metodología: 22-hyperframes-video-studio

## Pregunta de partida

¿Puede un modelo local pequeño participar en la producción de un video sin que sus errores lleguen
al resultado? La respuesta del laboratorio: sí, si el modelo solo propone contenido y todo lo demás
(tiempos, HTML, validación, render y medición) es determinista y comprobable.

## Fuentes y su papel

| Fuente | Dónde | Papel | Registro |
|---|---|---|---|
| HyperFrames | `https://github.com/heygen-com/hyperframes`, paquete npm `hyperframes@0.8.34` | Dependencia ejecutable vía `npx` | Licencia Apache-2.0 (metadatos de npm). Versión fijada en `renderer.py` |
| GSAP 3.14.2 | `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js` | Línea de tiempo de la composición, cargada en el render | Licencia propia de GSAP; no se redistribuye en el repositorio |
| FFmpeg / ffprobe | Instalación local | Ensamblado (vía HyperFrames) y medición | — |
| Ollama | `http://127.0.0.1:11434` | Dirección de contenido | Modelos iniciales del repositorio |

## Decisiones y por qué

1. **El modelo propone, el estudio decide la línea de tiempo.** Las escenas son contiguas y suman la
   duración pedida aunque el modelo sugiera otros tiempos.
2. **Texto del modelo como dato.** Todo valor que acaba en HTML o CSS se escapa o pasa por una lista
   blanca. Se comprobó que, antes de este cambio, el fragmento calibrado de la escena 2
   (`<div class="clip" data-start="0" data-duration="3">`) creaba un clip real y su texto no se veía.
3. **Lint local como gate determinista.** Revisa clips, ids y tiempos antes de lanzar Chrome. El
   nodo `VALIDATING_LINT` publica el resultado real; antes solo mostraba un mensaje sin comprobar
   nada.
4. **Sin telemetría.** El paquete de HyperFrames 0.8.34 incluye telemetría anónima (PostHog) activa
   por defecto. Su documentación y su código aceptan `HYPERFRAMES_NO_TELEMETRY` y `DO_NOT_TRACK` con
   valores `1/true/yes/on`; el estudio pasa ambas variables al subproceso de render.
5. **Fallback visible.** Sin Ollama se usan escenas calibradas, marcadas como `fallback` en la
   terminal, los eventos, el panel y el JSONL.
6. **Medir, no suponer.** La duración y la resolución salen de `ffprobe`. Sin medición, ceros.

## Cómo se verificó

- 28 pruebas deterministas (`uv run pytest`): configuración, rechazo de modelos cloud, escapado de la
  plantilla con valores hostiles, lint, tiempos fijados por el estudio, 409/422 de la API, exclusión
  de telemetría y medición sin pista de video.
- Demo y API ejecutadas sin Ollama; las salidas de [EXAMPLES.md](EXAMPLES.md) son las obtenidas.
- El análisis de telemetría se hizo leyendo el paquete descargado con `npm pack`, sin ejecutarlo.

## Límites conocidos

- El render necesita red la primera vez (paquete de HyperFrames y su navegador) y en cada render
  (GSAP desde jsDelivr).
- `hyperframes.json` fija 1920×1080 a 30 fps, y el contrato del brief solo admite esos valores.
- El lint es propio del laboratorio. El oficial (`npx hyperframes lint`) revisa más reglas y se
  propone como ejercicio.
- La calidad del guion depende del modelo; no hay un juez automático de contenido.

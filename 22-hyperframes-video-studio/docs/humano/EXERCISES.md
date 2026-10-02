# Ejercicios Didácticos: 22-hyperframes-video-studio

Pon a prueba y profundiza tus conocimientos en HyperFrames con los siguientes ejercicios progresivos:

## Ejercicio Básico: Personalización de Paleta y Escenas
- **Objetivo**: Modificar el prompt de Ollama en `ollama_client.py` para solicitar una estética "Cyberpunk / Neon" con degradados en tonos púrpura y cian (`#06b6d4` y `#ec4899`).
- **Verificación**: Ejecutar `uv run hyperframes-studio-demo` y verificar visualmente en el MP4 renderizado que las escenas adoptan el nuevo estilo.

## Ejercicio Intermedio: Integración de Audio y Pistas de Efectos
- **Objetivo**: Añadir una pista de audio sintético o tono de fondo utilizando la etiqueta `<audio class="clip" data-start="0" data-duration="15" src="...">` de HyperFrames.
- **Verificación**: Comprobar con `ffprobe` que el contenedor MP4 ahora incluye un stream de audio AAC/Opus activo.

## Ejercicio Avanzado: Renderizado en Formato WebM Transparente (Overlays)
- **Objetivo**: Extender `renderer.py` para aceptar el flag `--format webm` en `hyperframes render`, permitiendo producir animaciones con canal alfa transparente para transmisiones en vivo o superposiciones en streaming.
- **Verificación**: Inspeccionar con `ffprobe` que el pixel format sea `yuva420p` y que el archivo `.webm` se reproduzca con fondo transparente.

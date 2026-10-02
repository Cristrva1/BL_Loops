# Metodología: 22-hyperframes-video-studio

## Principios de Diseño
1. **Determinismo frente a Alucinación Visual**: A diferencia de los modelos de difusión de video que sufren de deformaciones o inconsistencias temporales en textos, HyperFrames renderiza HTML y tipografía con nitidez perfecta de píxeles.
2. **IA Local Estricta**: Toda la creatividad y estructuración procede de modelos locales alojados en Ollama (`qwen3.5:9b`), asegurando independencia de servicios de pago y total privacidad.
3. **Desacoplamiento Didáctico**: La documentación didáctica reside en `docs/humano/` y no es leída por el código runtime.
4. **Respaldo Determinista**: Si el modelo local tarda más del umbral configurado o se interrumpe la conexión, el orquestador recurre a un guión de calibración técnica sin fallar silenciosamente.

## Límites del Framework
- HyperFrames requiere que los elementos animados tengan tiempos finitos (`data-duration`).
- Las animaciones deben ser "seekable" (capaces de saltar a cualquier punto de tiempo $t$ de forma pura y sin estado acumulado dependiente de `requestAnimationFrame`).
- El renderizado en Windows depende de la presencia de `cmd.exe /c npx hyperframes` y de un navegador Chromium headless compatible.

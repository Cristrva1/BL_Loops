# Diagnóstico: 22-hyperframes-video-studio

Empieza por el estado comprobado: `uv run hyperframes-studio-demo` o, con el servidor en marcha,
`Invoke-RestMethod http://127.0.0.1:8022/api/status`.

## 1. `No se encontró npx: instala Node.js para renderizar con HyperFrames.`

- **Causa:** Node.js no está instalado o no está en el `PATH` de esa terminal.
- **Solución:** instala Node.js 22 o superior (`winget install OpenJS.NodeJS.LTS`), abre una terminal
  nueva y comprueba `node --version` y `npx --version`.

## 2. La primera corrida tarda mucho o falla al descargar

- **Causa:** `npx --yes hyperframes@0.8.34` descarga el paquete y sus dependencias la primera vez, y
  HyperFrames necesita su Chrome headless. Sin red, el render no puede empezar.
- **Diagnóstico:** `npx --yes hyperframes@0.8.34 doctor` (con `$env:HYPERFRAMES_NO_TELEMETRY = "1"`).
- **Solución:** `npx --yes hyperframes@0.8.34 browser ensure` descarga el navegador; las corridas
  siguientes reutilizan la caché de npm.

## 3. `La composición no supera el lint: ...`

- **Causa:** el HTML generado no cumple las reglas del estudio. El mensaje dice cuál:
  - `clip inesperado id=... data-start=... data-duration=...`: algún texto se convirtió en un
    elemento `.clip` (revisa que todo texto pase por `text()` en `templates.py`).
  - `se esperaban 5 escenas y hay N`: la plantilla omitió o duplicó escenas.
  - `<id>: empieza en X s y debería empezar en Y s`: hay huecos o solapes en la línea de tiempo.
- **Solución:** corrige la plantilla o el cálculo de tiempos. La corrida se detuvo antes de abrir
  Chrome, así que no se perdió tiempo de render.

## 4. HyperFrames falla con código distinto de 0

- **Diagnóstico:** el mensaje incluye el `stderr` de HyperFrames. Ejecuta el render a mano para ver
  la salida completa:

  ```powershell
  Set-Location .\.local\workspace
  $env:HYPERFRAMES_NO_TELEMETRY = "1"
  npx --yes hyperframes@0.8.34 render -o ..\output\manual.mp4
  ```

- **Causas frecuentes:** falta FFmpeg (`ffmpeg -version`), falta el navegador (punto 2) o la página
  no carga GSAP porque no hay red hacia `cdn.jsdelivr.net`.

## 5. La duración medida es `0.0s`

- **Causa:** `ffprobe` no está disponible o el archivo no tiene pista de video. El estudio no inventa
  la medición: registra ceros y la evaluación no aprueba.
- **Solución:** instala FFmpeg completo (`winget install Gyan.FFmpeg`) y repite.

## 6. Siempre sale `fallback`

- **`ConnectError al consultar Ollama`:** Ollama no está en marcha; comprueba `ollama list`.
- **`Ollama respondió HTTP 404`:** el modelo no está descargado o el nombre no coincide.
- **`JSONDecodeError al consultar Ollama`:** el modelo respondió, pero no con un arreglo JSON válido.
  Prueba `qwen3.5:9b` o revisa el prompt en `ollama_client.py`.

## 7. Telemetría

El estudio exporta `HYPERFRAMES_NO_TELEMETRY=1` y `DO_NOT_TRACK=1` en cada render. Si ejecutas
HyperFrames a mano, define la variable antes (`$env:HYPERFRAMES_NO_TELEMETRY = "1"`) o desactívala
de forma permanente con `npx --yes hyperframes@0.8.34 telemetry disable`.

## 8. `409` o `422` al lanzar una corrida

- `409`: ya hay un render en curso; espera a `COMPLETED` o `FAILED` (`run_in_progress` en
  `/api/status`).
- `422`: el brief no cumple el contrato (duración fuera de 5–60 s o modelo `cloud`). El detalle de la
  respuesta indica el campo.

## 9. `sub_timeline_script_failure`: GSAP no carga

- **Síntoma:** HyperFrames captura los 450 fotogramas y al final responde `Render blocked by 1
  correctness warning: sub_timeline_script_failure` con
  `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`.
- **Causa:** el Chrome de HyperFrames no pudo descargar GSAP (sin red, proxy o firewall que bloquea
  `cdn.jsdelivr.net`). Sin GSAP no hay línea de tiempo, y HyperFrames prefiere fallar a entregar un
  video sin animaciones. El estudio marca la corrida como `FAILED`: no aprueba a ciegas.
- **Solución:** da salida a `cdn.jsdelivr.net`. Si no puedes, sirve GSAP desde el workspace y
  renderiza a mano:

  ```powershell
  Set-Location .\.local\workspace
  npm pack gsap@3.14.2
  tar -xzf gsap-3.14.2.tgz
  Copy-Item .\package\dist\gsap.min.js .
  (Get-Content index.html) -replace 'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js', 'gsap.min.js' | Set-Content index.html
  $env:HYPERFRAMES_NO_TELEMETRY = "1"
  npx --yes hyperframes@0.8.34 render -o ..\output\manual.mp4
  ```

  Así se hizo el render del [ejemplo 7](EXAMPLES.md#ejemplo-7-render-real-con-hyperframes).

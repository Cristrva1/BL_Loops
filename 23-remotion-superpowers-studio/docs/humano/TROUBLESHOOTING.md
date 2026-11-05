# Diagnóstico: 23-remotion-superpowers-studio

Empieza por el estado comprobado: `uv run remotion-studio-demo` o, con el servidor en marcha,
`Invoke-RestMethod http://127.0.0.1:8023/api/status`.

## 1. `No se encontró npx: instala Node.js y ejecuta npm install en este laboratorio.`

- **Causa:** Node.js no está en el `PATH`.
- **Solución:** instala Node.js 22 o superior (`winget install OpenJS.NodeJS.LTS`), abre una terminal
  nueva y ejecuta `npm ci` en la carpeta del laboratorio.

## 2. `Cannot find module 'remotion'` o errores al empaquetar

- **Causa:** falta `node_modules/` o se instaló en otra carpeta.
- **Solución:** `npm ci` dentro de `23-remotion-superpowers-studio`. Usa `npm ci` (no `npm install`)
  para respetar exactamente `package-lock.json`.

## 3. La primera corrida tarda mucho o falla al descargar el navegador

- **Causa:** Remotion descarga Chrome headless la primera vez que renderiza.
- **Solución:** con red, `npx remotion browser ensure` lo descarga por adelantado. Las corridas
  siguientes lo reutilizan.

## 4. `npm run typecheck` falla con `Cannot find module './scenes.json'`

- **Causa:** `tsconfig.json` sin `"resolveJsonModule": true`. El laboratorio ya lo incluye; si lo
  copiaste de una versión anterior, añádelo.

## 5. El render se congela o agota la memoria

- **Causa:** `--concurrency=4` renderiza cuatro fotogramas a la vez.
- **Solución:** baja el valor en `remotion_renderer.py` (por ejemplo, `--concurrency=2`) y repite.
  No hay variable de entorno para esto.

## 6. `git status` muestra `src/video_composition/scenes.json` modificado

- **Causa:** cada corrida reescribe ese archivo (es la entrada de la composición). Con Ollama, el
  contenido cambia.
- **Solución:** si no quieres conservarlo, `git restore src/video_composition/scenes.json`.

## 7. La duración medida no es exactamente la pedida

- **Causa:** la división entera de fotogramas entre 4 escenas puede perder hasta 3 fotogramas (7 s →
  208 en lugar de 210, 6,93 s). La evaluación tolera 1 s.
- **Solución:** el [ejercicio intermedio](EXERCISES.md#intermedio-que-no-se-pierda-ningún-fotograma)
  reparte el resto.

## 8. Siempre sale `fallback`

- **`ConnectError al consultar Ollama`:** Ollama no está en marcha; comprueba `ollama list`.
- **`Ollama respondió HTTP 404`:** el modelo no está descargado o el nombre no coincide.
- **`JSONDecodeError al consultar Ollama`:** el modelo respondió, pero no con un arreglo JSON válido.

## 9. `409` o `422` al lanzar una corrida

- `409`: ya hay un render en curso (`run_in_progress` en `/api/status`).
- `422`: el brief no cumple el contrato: duración fuera de 4–60 s, fps distinto de 30, resolución
  distinta de 1920×1080 o modelo `cloud`.

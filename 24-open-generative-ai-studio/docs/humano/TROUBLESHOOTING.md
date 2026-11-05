# Diagnóstico: 24-open-generative-ai-studio

Empieza siempre por el estado comprobado:

```powershell
uv run open-genai-demo
```

o, con el servidor en marcha, `Invoke-RestMethod http://127.0.0.1:8024/api/status`.

## 1. `No se encontró FFmpeg: instálalo para renderizar.`

- **Causa:** `ffmpeg` no está en el `PATH` de la terminal que lanza el estudio.
- **Diagnóstico:** `ffmpeg -version` y `ffprobe -version` en la misma terminal.
- **Solución:** en Windows, `winget install Gyan.FFmpeg` y abre una terminal nueva. La píldora del
  panel debe pasar a «FFmpeg: disponible».

## 2. La duración medida es `0.0s` y la evaluación no aprueba

- **Causa:** el MP4 existe, pero `ffprobe` no está disponible o no pudo leerlo. El estudio no inventa
  la medición: registra ceros.
- **Diagnóstico:** `ffprobe -version`; en el registro verás
  `No se pudo inspeccionar el animatic con ffprobe`.
- **Solución:** instala FFmpeg completo (incluye `ffprobe`) y repite la corrida.

## 3. `FFmpeg no pudo generar el plano N: ...`

- **Causa:** el filtergraph del plano N no es válido. El mensaje incluye la última línea de error de
  FFmpeg.
- **Diagnóstico típico:**
  - `Cannot find a valid font` o `Error initializing filter 'drawtext'`: no hay fuente utilizable
    (frecuente en Windows sin fontconfig).
  - Errores de opción tras cambiar `build_filter_graph()`: revisa que todo texto pase por
    `drawtext_value()` y que las expresiones vayan entre comillas.
- **Solución para fuentes:** indica una en el `.env` del laboratorio:

  ```text
  ANIMATIC_FONT_FILE=C:/Windows/Fonts/arial.ttf
  ```

  Si la ruta no existe, la configuración se rechaza al arrancar con
  `ANIMATIC_FONT_FILE debe apuntar a un archivo de fuente existente.`

## 4. El animatic usa otra fuente distinta de la indicada

- **Causa:** FFmpeg con fontconfig **no falla** si `fontfile` es incorrecto: avisa y usa la fuente por
  defecto. Pasa, por ejemplo, si una ruta con `:` no está escapada.
- **Diagnóstico:** ejecuta un plano con `-loglevel verbose` y busca una línea `Using "..."`. Se
  comprobó en la verificación del laboratorio:

  | Valor de `fontfile` | Línea en modo detallado |
  |---|---|
  | Ruta con `\:` escapado | ninguna: se carga la fuente pedida |
  | La misma ruta sin escapar | `Using "/usr/share/fonts/opentype/inter/Inter-Regular.otf"` |
  | Ruta inexistente | `Using "/usr/share/fonts/opentype/inter/Inter-Regular.otf"` |

  (La ruta de la fuente por defecto depende del sistema.)
- **Solución:** usa `fontfile_option()`, que escapa `:` y descarta rutas con comillas.

## 5. Siempre sale `fallback`

- **`ConnectError al consultar Ollama`:** Ollama no está en marcha o escucha en otra dirección.
  Comprueba `ollama list` y `OLLAMA_BASE_URL`.
- **`Ollama respondió HTTP 404`:** el modelo no está descargado. Ejecuta `ollama list`; si falta,
  descárgalo tú (`ollama pull qwen3.5:9b`) o cambia `OLLAMA_MODEL`.
- **`ReadTimeout al consultar Ollama`:** el modelo tardó más de 120 s. Prueba `qwen3.5:4b`.
- **`respuesta no válida: <motivo>`:** Ollama respondió, pero fuera de contrato. El motivo dice qué
  falló (`se esperaban 4 planos y llegaron 3`, `shot_type desconocido: ...`, JSON mal formado). Prueba
  otro modelo o revisa `build_prompt()`.

## 6. `Configuracion invalida: ...` al arrancar

- El estudio solo acepta `OLLAMA_BASE_URL` HTTP en loopback, modelos sin etiqueta cloud, `HOST`
  local y `PORT` entre 1024 y 65535. Corrige el `.env` del laboratorio o de la raíz, o la variable de
  entorno. Las variables del proceso ganan a los `.env`.

## 7. `409 Ya hay un animatic en curso`

- Solo se permite una corrida a la vez. Espera al evento `COMPLETED` o `FAILED`, o consulta
  `run_in_progress` en `/api/status`.

## 8. El panel no muestra eventos

- La píldora «Eventos» indica si el flujo SSE está conectado; el navegador se reconecta solo.
- Si recargas la página después de una corrida, el panel recupera el último render y el storyboard
  desde la API, pero no los eventos anteriores: esos solo se ven en directo.

## 9. El puerto 8024 está ocupado

- Otra instancia del estudio sigue en marcha. Ciérrala con `Ctrl+C` o cambia `PORT` en el `.env`
  (recuerda abrir el panel en el puerto nuevo). Consulta el mapa de puertos en
  [QUICKSTART del maestro](../../../docs/humano/maestro/QUICKSTART.md#mapa-de-puertos).

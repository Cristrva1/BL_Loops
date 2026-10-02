# Diagnóstico de Fallos: 22-hyperframes-video-studio

Guía de resolución de problemas comunes encontrados al trabajar con HyperFrames.

### 1. `npx hyperframes doctor` reporta fallo en Chrome
- **Síntoma**: El doctor indica que no encuentra un ejecutable válido de Chrome o produce timeout.
- **Solución**: Ejecutar `npx hyperframes browser ensure` en la terminal para descargar automáticamente el binario precompilado de Chrome Headless Shell.

### 2. Ollama no responde o agota el tiempo de espera
- **Síntoma**: La llamada a `http://127.0.0.1:11434/api/generate` lanza un `httpx.TimeoutException`.
- **Solución**:
  1. Comprobar que Ollama esté corriendo en Windows (`ollama list`).
  2. Si el modelo `qwen3.5:9b` es demasiado pesado para la carga actual, cambiar en `.env` o en la UI a `qwen3.5:4b`.
  3. El sistema cuenta con fallback automático para garantizar que la ejecución nunca se detenga.

### 3. Error en FFmpeg durante el ensamblado
- **Síntoma**: HyperFrames captura los cuadros pero falla en la fase `assemble`.
- **Solución**: Verificar que `ffmpeg.exe` esté accesible en la consola escribiendo `ffmpeg -version`. Si no lo está, instalarlo vía `winget install Gyan.FFmpeg`.

### 4. Telemetría de HeyGen activa
- **Síntoma**: Mensajes en consola invitando a autenticarse o enviar reportes.
- **Solución**: Desactivar permanentemente la telemetría ejecutando:
  ```powershell
  npx hyperframes telemetry disable
  ```

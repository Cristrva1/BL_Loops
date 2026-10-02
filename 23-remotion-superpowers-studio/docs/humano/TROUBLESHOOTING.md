# Diagnóstico de Fallos: 23-remotion-superpowers-studio

### 1. Remotion no encuentra el ejecutable de Chrome
- **Síntoma**: El renderizado arroja error de que no existe Chrome Headless Shell.
- **Solución**: Ejecutar en la terminal del laboratorio:
  ```powershell
  npx -p @remotion/cli remotion browser ensure
  ```

### 2. Error de paquetes de React o Typescript
- **Síntoma**: `Cannot find module 'remotion'` o errores de tipos al compilar.
- **Solución**: Asegurarse de haber ejecutado `npm install` dentro del directorio `23-remotion-superpowers-studio`.

### 3. Error de concurrencia o saturación de memoria
- **Síntoma**: El proceso de renderizado se congela o agota la memoria RAM del sistema.
- **Solución**: Ajustar el flag `--concurrency=2` en `remotion_renderer.py` o en la variable de entorno `REMOTION_CONCURRENCY=2`.

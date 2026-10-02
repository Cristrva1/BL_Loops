# Diagnóstico y Resolución de Problemas · Laboratorio 25

Guía de soluciones ante fallos comunes al procesar transcripciones.

---

### 1. Error: "No se pudo conectar con Ollama en http://127.0.0.1:11434"
- **Causa:** El servicio de Ollama no está ejecutándose en tu máquina.
- **Solución:**
  1. Abre una terminal y corre:
     ```powershell
     ollama list
     ```
  2. Si el comando no responde o falla la conexión, inicia Ollama desde el menú inicio o ejecutando `ollama serve`.

---

### 2. Error: "Ollama superó el límite de tiempo de espera (timeout)"
- **Causa:** La transcripción es muy larga o la GPU/CPU tardó más del tiempo límite configurado (`180s`).
- **Solución:**
  1. Utiliza un modelo más veloz y liviano como `qwen3.5:4b` desde el selector de la interfaz.
  2. O incrementa `OLLAMA_TIMEOUT_SECONDS=300.0` en tu archivo `.env`.

---

### 3. Error: "Ollama no encontró el modelo 'qwen3.5:9b'"
- **Causa:** El modelo especificado no ha sido descargado localmente.
- **Solución:**
  Descarga el modelo con:
  ```powershell
  ollama pull qwen3.5:9b
  # O el alternativo rápido:
  ollama pull qwen3.5:4b
  ```

---

### 4. El parser detectó "Participante" en lugar de los nombres reales
- **Causa:** La transcripción exportada no incluía etiquetas con nombre (ej. era solo texto plano de subtítulos automáticos).
- **Solución:**
  Si tu videollamada exporta texto plano, puedes formatear rápidamente las intervenciones anteponiendo `Nombre:` o `[00:01] Nombre:`. El parser identificará los nombres automáticamente.

---

### 5. Fallo de puertos (`Port 8025 or 5175 already in use`)
- **Causa:** Otra sesión o proceso anterior sigue ejecutándose en ese puerto.
- **Solución:**
  En PowerShell, localiza y detén el proceso colgado:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8025).OwningProcess | Stop-Process -Force
  ```

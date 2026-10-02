# Ejercicios Prácticos · Laboratorio 25 (`25-meeting-summarizer`)

Estos ejercicios didácticos te guían para dominar y extender la herramienta de resúmenes de videollamadas.

---

## Ejercicio Básico: Procesar tu primera videollamada

**Objetivo:** Obtener la transcripción de una reunión real o de prueba y generar su minuta completa.

1. Abre Google Meet, Zoom o Teams y activa los subtítulos o transcripción en español durante 5 minutos.
2. Copia el texto resultante al portapapeles.
3. Inicia la aplicación web (`http://127.0.0.1:5175`).
4. Pega el texto en el área de entrada y dale un título (ej. "Revisión Semanal de Proyecto").
5. Haz clic en **"Generar Resumen Inteligente"**.
6. Observa la tabla de **Compromisos y Tareas** y verifica si identificó correctamente a los responsables.

---

## Ejercicio Intermedio: Comparar Modelos (`qwen3.5:4b` vs `qwen3.5:9b`)

**Objetivo:** Evaluar la diferencia de velocidad y calidad de extracción entre un modelo liviano y uno estándar.

1. Ve a la terminal y procesa el fixture de prueba con `qwen3.5:4b`:
   ```powershell
   uv run meeting-summarizer summarize fixtures/meet_sprint_planning.txt --model qwen3.5:4b
   ```
2. Toma nota del tiempo de ejecución y del número de compromisos extraídos.
3. Ahora procesa el mismo archivo con `qwen3.5:9b`:
   ```powershell
   uv run meeting-summarizer summarize fixtures/meet_sprint_planning.txt --model qwen3.5:9b
   ```
4. Compara:
   - ¿Qué modelo redactó una minuta más fluida en la pestaña de correo?
   - ¿Hubo diferencias en los plazos detectados?

---

## Ejercicio Avanzado: Preguntar a la Reunión (Q&A Forense)

**Objetivo:** Realizar consultas específicas sobre temas espinosos o acuerdos técnicos de la reunión.

1. Carga la reunión `fixtures/teams_architecture_sync.txt` en la interfaz web.
2. Ve a la pestaña **"💬 Preguntar a la Reunión"**.
3. Haz las siguientes preguntas:
   - *"¿A partir de cuántas palabras se decidió usar Map-Reduce?"*
   - *"¿Quién es el responsable de implementar el algoritmo de chunking y para qué fecha?"*
   - *"¿Se mencionó alguna herramienta en la nube durante la conversación?"*
4. Comprueba cómo el modelo cita a los hablantes exactos (Daniela o Andrés) y sus razones.

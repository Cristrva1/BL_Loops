# Metodología: 24-open-generative-ai-studio

## Pregunta de partida

¿Qué parte de un estudio audiovisual con IA puede funcionar en local y de forma verificable? Este
laboratorio responde con la parte de **preproducción**: idea, prompts, storyboard y animatic. La
generación de imágenes o video con difusión queda fuera porque exige modelos y hardware que no
forman parte de la base de BL_Loops.

## Fuentes y su papel

| Fuente | Remoto | Papel | Estado del registro |
|---|---|---|---|
| Open-Generative-AI | `https://github.com/Anil-matcha/Open-Generative-AI` | Referencia conceptual: la idea de «estudios» especializados (prompt, storyboard, medios) | No se instala ni se copia código. SHA y licencia **pendientes de registrar** si algún día se usa como dependencia |
| FFmpeg | Instalación local del sistema | Dependencia ejecutable: `drawtext`, `concat` y `ffprobe` | Versión verificada en este laboratorio: 6.1 |
| Ollama | `http://127.0.0.1:11434` | Inferencia local para storyboard y prompts | Modelos iniciales del repositorio (`qwen3.5:9b`, `qwen3.5:4b`) |
| `menu_portable/REPO_MENU.md` | Este repositorio | Descubrimiento de la referencia | Entrada `open-generative-ai` |

El laboratorio se escribió desde cero: ningún archivo procede de la referencia.

## Decisiones y por qué

1. **El modelo propone, el contrato decide.** Ollama devuelve texto. `parse_shots()` exige 4 planos y
   valores de los enums; cualquier otra cosa activa el respaldo con su motivo. Las opciones que ve el
   modelo se generan desde los mismos enums que las validan.
2. **La duración es del estudio, no del modelo.** Un modelo puede proponer planos de 7 s; el animatic
   debe durar lo pedido. La duración se calcula y se asigna después de validar.
3. **Fallback visible y honesto.** Los planos calibrados son útiles para aprender el render sin
   Ollama, pero se marcan como `fallback` en la terminal, los eventos, el panel y el JSONL.
4. **Medir, no suponer.** La duración, la resolución y los fps del resultado se leen con `ffprobe`.
   Si no se puede medir, se registran ceros y la evaluación no aprueba.
5. **El texto del modelo es dato.** Se escapa para FFmpeg y se inserta con `textContent` en el panel.
   Un color inventado cae al acento base. Así ninguna respuesta puede romper el comando ni inyectar
   HTML.
6. **Fallar en voz alta.** Si FFmpeg no genera un plano, la corrida falla e indica cuál. La versión
   anterior del renderizador omitía ese plano y declaraba éxito con un video más corto.
7. **Sin dependencias de interfaz.** El panel es HTML, CSS y JavaScript servidos por la propia API:
   sin fuentes, scripts ni CDN remotos.

## Cómo se verificó

- 37 pruebas deterministas (`uv run pytest`): configuración, lectura del modelo con
  `httpx.MockTransport`, fallback, escapado, fallo de plano, medición y API.
- Una prueba de render real con FFmpeg que se omite si FFmpeg no está instalado.
- Demo y API ejecutadas sin Ollama; las salidas de [EXAMPLES.md](EXAMPLES.md) son las obtenidas.
- Escapado de la ruta de la fuente comprobado con FFmpeg en modo detallado: con `\:` se carga la
  fuente pedida; sin escapar, FFmpeg la ignora y usa otra (ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md)).
- Panel revisado en navegador a 1366 px y 390 px de ancho, sin errores de consola.

## Límites conocidos

- El animatic no anima el movimiento de cámara: lo describe. El ejercicio avanzado propone animarlo.
- La calidad del storyboard depende del modelo; aquí no hay un juez automático de calidad narrativa.
- `total_duration_target` se reparte siempre entre 4 planos.
- El estado (último storyboard, render y evaluación) se pierde al reiniciar el servidor.
- Esta verificación no se ejecutó en Windows. Que `drawtext` sin `fontfile` falle allí es un problema
  frecuente cuando fontconfig no está configurado; por eso el estudio indica siempre una fuente
  explícita cuando encuentra una conocida.

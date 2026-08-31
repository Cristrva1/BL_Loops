# Diagnóstico

## “No se pudo conectar con Ollama local”

Ejecuta `ollama list` y confirma que Ollama escucha en `http://127.0.0.1:11434`. No cambies la
URL por una API externa: la configuración remota se rechaza deliberadamente.

## “Ollama no encontró el modelo”

Compara `.env.example` con `ollama list`. Los nombres y tags deben coincidir. El laboratorio no
descarga modelos automáticamente.

## “El índice no existe” o “perfil incompatible”

Ejecuta nuevamente:

```powershell
uv run sales-agent index --source "C:\Users\criss\Desktop\Claude\BL_Loops\docs\humano\Libros"
```

Un cambio de modelo, dimensión, instrucción o filtro requiere reconstrucción. No copies la base
de otro laboratorio.

## Aparece `runtime_fallback`

No es un fallo: el modelo no devolvió exactamente una llamada aceptable y el runtime buscó la
pregunta original. La ejecución sigue limitada a una herramienta. Si ocurre con frecuencia,
conserva la traza, formula preguntas autosuficientes y comprueba el modelo configurado.

## La fuente correcta no aparece

1. Ejecuta `sales-agent stats`.
2. Abre el Markdown original y busca una descripción sustantiva fuera de secciones filtradas.
3. Recuerda que un título no equivale a conocimiento: una ficha sin descripción queda fuera.
4. Prueba términos explícitos y una paráfrasis.
5. Añade contenido solo si tienes autorización y procedencia clara; luego reindexa.

## La respuesta cita una fuente débil

Observa `estado=unreviewed` o `generated`, las líneas y el texto original. Una cita prueba
procedencia, no verdad. No uses una recomendación de alto impacto sin revisión humana.

## “ADVERTENCIA: la respuesta no usó citas válidas”

La generación terminó, pero el gate de citas detectó cero citas o un identificador fuera del
rango. Considera esa respuesta no aprobada, conserva el JSONL y vuelve a ejecutar solo después
de diagnosticar el prompt/modelo.

## JSONL inválido

Ejecuta `uv run sales-agent-validate <ruta>`. Una corrida debe comenzar en `run.started`, tener
secuencia consecutiva y un único `run.completed` o `run.failed` al final.


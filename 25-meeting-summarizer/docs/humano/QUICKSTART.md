# Inicio rápido · Laboratorio 25 (`25-meeting-summarizer`)

## Resultado esperado

Al terminar habrás normalizado una transcripción sin modelo, generado una minuta con Ollama desde la
CLI y abierto el dashboard con progreso en tiempo real.

## 1. Requisitos previos

```powershell
uv --version
node --version          # solo para el dashboard (v18 o superior)
ollama list             # debe aparecer qwen3.5:9b o qwen3.5:4b
```

Si falta el modelo y autorizas la descarga de sus pesos:

```powershell
ollama pull qwen3.5:9b
```

## 2. Preparar el entorno aislado

```powershell
Set-Location .\25-meeting-summarizer        # desde la raíz de BL_Loops
uv sync --all-groups
uv run pytest
```

Resultado esperado: se crea `25-meeting-summarizer/.venv` y las pruebas pasan sin Ollama.

## 3. Ver lo que recibirá el modelo (sin Ollama)

```powershell
uv run meeting-summarizer parse .\fixtures\meet_sprint_planning.txt
```

Resultado esperado: `Formato detectado: meet`, tres participantes con su número de turnos, los
primeros turnos normalizados y `single-pass: 1 bloque -> 1 llamada a Ollama`. Prueba también los
otros fixtures (`zoom_standup.vtt`, `teams_architecture_sync.txt`, `notas_lluvia_de_ideas.txt`) y el
plan map-reduce con `--max-words 120`. Las salidas completas están en [EXAMPLES.md](EXAMPLES.md).

## 4. Generar una minuta desde la CLI (con Ollama)

```powershell
uv run meeting-summarizer summarize .\fixtures\meet_sprint_planning.txt
uv run meeting-summarizer list
```

Verás la barra de progreso por etapas, el resumen ejecutivo, las decisiones y la tabla de
compromisos. La minuta se guarda en `.local/data/meetings.db` y la traza sanitizada en
`.local/runs/`. Para comparar modelos añade `--model qwen3.5:4b`.

## 5. Iniciar el backend (FastAPI en el puerto 8025)

```powershell
uv run uvicorn meeting_summarizer.main:app --host 127.0.0.1 --port 8025 --reload
```

Salida esperada:

```text
INFO:     Uvicorn running on http://127.0.0.1:8025 (Press CTRL+C to quit)
```

`http://127.0.0.1:8025/docs` muestra la documentación interactiva de la API.

## 6. Iniciar el dashboard (React + Vite en el puerto 5177)

En otra terminal, desde la misma carpeta:

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Abre `http://127.0.0.1:5177`. El puerto es propio de este laboratorio para no chocar con el 04
(`5175`); consulta el [mapa de puertos](../../../docs/humano/maestro/QUICKSTART.md#mapa-de-puertos).

## 7. Recorrido en el dashboard

1. Carga un ejemplo rápido (`Sprint Planning`, `Zoom Standup`…) o pega una transcripción sintética.
2. Elige modelo (`qwen3.5:9b` recomendado, `qwen3.5:4b` más rápido) y modo: *Completo*, *Ejecutivo*,
   *Solo tareas* o *Técnico*.
3. Pulsa **Generar Resumen Inteligente** y observa las etapas que llegan por SSE.
4. Revisa las pestañas de resumen, decisiones, compromisos (responsable y plazo) y minuta.
5. Usa **Preguntar a la reunión** para consultar detalles; la respuesta debe apoyarse en la
   transcripción.

No pegues reuniones reales con datos de clientes o personas: los fixtures sintéticos bastan para
aprender y evaluar.

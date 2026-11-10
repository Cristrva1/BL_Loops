# Inicio rápido en PowerShell

> Guía humana. Todos los comandos se ejecutan desde la raíz de `01-prompt-agent-factory`.

## Resultado esperado

Al completar esta guía tendrás:

- API educativa en `http://127.0.0.1:8011`.
- Documentación interactiva en `http://127.0.0.1:8011/docs`.
- Interfaz visual en `http://127.0.0.1:5173`.
- Un artefacto exportable dentro de `.local/exports`.

## 1. Preparar dependencias

Abre PowerShell en esta carpeta:

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\01-prompt-agent-factory
uv sync --all-groups
npm --prefix frontend install
```

`uv` crea una `.venv` aislada con Python 3.12. `npm` instala únicamente la interfaz de este laboratorio. Ninguna dependencia se instala dentro de los repositorios de referencia.

## 2. Iniciar el backend

En la primera terminal:

```powershell
uv run uvicorn prompt_agent_factory.main:app --host 127.0.0.1 --port 8011 --reload
```

Debes ver que Uvicorn escucha en `http://127.0.0.1:8011`. La ruta `/api/v1/health` indicará `llm_used: false` porque esta parte no invoca un modelo.

## 3. Iniciar el frontend

En una segunda terminal, desde la misma carpeta:

```powershell
npm --prefix frontend run dev
```

Abre la URL exacta que muestre Vite, normalmente `http://127.0.0.1:5173`.

## 4. Recorrido guiado

1. Pulsa **Cargar ejemplo**.
2. Cambia el tipo entre prompt, agente y skill.
3. Pulsa **Analizar intención**.
4. Si falta algo, lee la pregunta y su explicación.
5. Pulsa **Construir borrador** cuando la preparación llegue al 100 %.
6. Revisa el panel JSON y localiza `permissions`, `stop_conditions` y `content_hash`.
7. Pulsa **Exportar JSON** y confirma que el nodo final queda verde.

## 5. Practicar sin interfaz

```powershell
uv run factory-demo --list
uv run factory-demo --intake incomplete_agent_brief.json
uv run factory-demo --intake skill_meeting_minutes.json
```

Resultado esperado: la lista muestra seis briefings y uno incompleto; el segundo comando imprime
siete preguntas y no exporta nada; el tercero termina con `Exportado: .local/exports/skill_….json`.
El recorrido completo está en [EXAMPLES.md](EXAMPLES.md).

## 6. Verificación por consola

```powershell
uv run pytest
uv run ruff check .
uv run factory-export-schemas
npm --prefix frontend run build
uv run factory-demo --all
```

Resultado esperado: todas las pruebas en verde, `All checks passed!`, un build sin errores y el
resumen `5 exportados, 1 incompleto, 0 inválidos`.

## Si copias el laboratorio fuera de BL_Loops

Dentro del workspace se usa el `.env` global de la raíz. Fuera de él:

```powershell
Copy-Item .env.example .env
```

La configuración rechaza endpoints de Ollama remotos mientras `BL_LOOPS_RUNTIME_NETWORK=false` y también rechaza telemetría o escrituras externas para esta parte.

# Inicio rápido en Windows 11

## Resultado esperado

Abrirás un chat local con `gemma4:e4b`, mantendrás una conversación de varios turnos y validarás su traza JSONL sin guardar el texto conversado.

## 1. Abrir el laboratorio

```powershell
Set-Location C:\Users\criss\Desktop\Claude\BL_Loops\02-single-agent
```

Todos los comandos siguientes se ejecutan desde esta carpeta. Así `uv` usa la `.venv` exclusiva del laboratorio y las salidas quedan en `02-single-agent/.local/`.

## 2. Comprobar los requisitos

```powershell
uv --version
ollama --version
ollama list
```

En la última salida debe aparecer `gemma4:e4b`. Si no está instalado, la descarga explícita es:

```powershell
ollama pull gemma4:e4b
```

Ese comando descarga pesos; no es necesario repetirlo cuando el modelo ya figura en `ollama list`.

## 3. Crear el entorno aislado

```powershell
uv sync --all-groups
```

El resultado esperado es `02-single-agent/.venv`. El runtime no instala librerías HTTP ni SDK: usa la biblioteca estándar de Python.

## 4. Conversar

```powershell
uv run single-agent
```

Prueba este diálogo:

```text
Tu > Recuerda que el código de prueba es luna azul.
Tu > ¿Cuál es el código de prueba?
```

La segunda respuesta debe recuperar el dato del primer turno de forma congruente. Finaliza con:

```text
Tu > /salir
```

También puedes terminar con `Ctrl+C`.

## 5. Importar la traza

```powershell
uv run single-agent-validate
```

El resultado esperado comienza con `JSONL valido` e informa número de eventos, evento terminal y `run_id`. El archivo vive en `.local/runs/` y no contiene los mensajes ni las respuestas.

## 6. Verificar el proyecto

```powershell
uv run pytest
uv run ruff check .
```

Las pruebas usan dobles locales; no consumen inferencia ni requieren que Ollama esté iniciado. La conversación del paso 4 es la demostración real separada.

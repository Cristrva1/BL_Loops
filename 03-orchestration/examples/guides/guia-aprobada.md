# Guía para ejecutar un agente local

## Objetivo
Abrir Ollama, lanzar el chat del agente único desde PowerShell y cerrarlo de forma segura.

## Pasos
1. Comprueba que Ollama responde con `ollama list`.
2. Entra en la carpeta del laboratorio con `Set-Location .\02-single-agent`.
3. Ejecuta `uv run single-agent` y escribe tu primera pregunta.

## Límites
Todo ocurre en tu equipo: no hay servicios externos ni datos personales.

## Cómo saber que funcionó
Ves la respuesta del modelo y, al escribir /salir, la ruta de la traza JSONL.

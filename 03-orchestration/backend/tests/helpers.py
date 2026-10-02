from __future__ import annotations

from orchestration.ollama_client import ChatResult, OllamaError

PASSING_GUIDE = """
# Guía breve para un agente local

## Objetivo
Esta guía enseña a abrir un chat local con Ollama en Windows 11 y a detenerlo con claridad.

## Pasos
1. Comprueba que Ollama responde en el equipo.
2. Abre PowerShell y entra al laboratorio del agente único:

```powershell
Set-Location C:\\Users\\criss\\Desktop\\Claude\\BL_Loops\\lab-unico
uv run single-agent
```

3. Escribe un mensaje de prueba. Cuando termines, usa `/salir` o Ctrl+C.

## Límites
Solo se usa Ollama local. No hay tools, navegador ni escritura fuera del laboratorio.
El historial vive en RAM y desaparece al cerrar la sesión.

## Cómo saber que funcionó
La CLI muestra una respuesta final y `uv run single-agent-validate` acepta el JSONL.
""".strip()

FAILING_GUIDE = """
Habla con ChatGPT en el navegador y pide una guía improvisada.
No hace falta un modelo local ni un comando de terminal.
""".strip()

PLAN_JSON = """
{
  "title": "Guia de agente local",
  "audience": "Estudiante de BL_Loops",
  "outline": [
    {
      "section_id": "objetivo",
      "heading": "Objetivo",
      "must_include": ["Ollama", "agente local"]
    },
    {
      "section_id": "pasos",
      "heading": "Pasos",
      "must_include": ["PowerShell", "uv run"]
    },
    {
      "section_id": "limites",
      "heading": "Limites",
      "must_include": ["solo local", "sin cloud"]
    },
    {
      "section_id": "exito",
      "heading": "Como saber que funciono",
      "must_include": ["JSONL", "/salir"]
    }
  ],
  "success_checks": [
    "Incluye ## Objetivo",
    "Incluye ## Pasos",
    "Incluye un comando PowerShell",
    "Declara /salir o Ctrl+C"
  ]
}
""".strip()

REVIEW_PASS_JSON = """
{
  "passed": true,
  "checks": [
    {"check_id": "has_objetivo", "passed": true, "evidence": "Heading Objetivo presente."},
    {"check_id": "has_pasos", "passed": true, "evidence": "Heading Pasos presente."},
    {"check_id": "has_limites", "passed": true, "evidence": "Heading Limites presente."},
    {"check_id": "has_exito", "passed": true, "evidence": "Heading de exito presente."},
    {"check_id": "mentions_ollama", "passed": true, "evidence": "Menciona Ollama."},
    {"check_id": "has_powershell", "passed": true, "evidence": "Hay uv run."},
    {"check_id": "has_stop_condition", "passed": true, "evidence": "Hay /salir."},
    {"check_id": "no_cloud_fallback", "passed": true, "evidence": "Sin marcas cloud."},
    {"check_id": "length_ok", "passed": true, "evidence": "Longitud adecuada."}
  ],
  "required_changes": []
}
""".strip()


class ScriptedClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[list[dict[str, str]]] = []

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        response_format: str | None = None,
    ) -> ChatResult:
        _ = response_format
        self.calls.append(messages)
        if not self.responses:
            raise OllamaError("No hay respuestas scriptadas.")
        content = self.responses.pop(0)
        return ChatResult(
            content=content,
            model="qwen3.5:4b",
            total_duration_ms=8.0,
            prompt_tokens=11,
            output_tokens=17,
        )

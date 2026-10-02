from __future__ import annotations

from agent_loops.ollama_client import ChatResult, OllamaError

PASSING_OUTPUT = """
{
  "title": "Briefing de asistente local",
  "steps": [
    "Confirmar que Ollama responde",
    "Cargar el briefing aprobado",
    "Responder solo con fuentes locales"
  ],
  "limits": ["Solo Ollama local", "Sin CRM ni correo"],
  "stop_condition": "Detener con /salir o al agotar el presupuesto"
}
""".strip()

FAILING_OUTPUT = """
Aqui tienes un texto util para vender mas usando ChatGPT.
""".strip()

MID_OUTPUT = """
{
  "title": "Briefing operativo local",
  "steps": ["Confirmar Ollama", "Cargar briefing", "Responder local"],
  "limits": ["Ollama local"],
  "stop_condition": ""
}
""".strip()

WORSE_OUTPUT = """
{
  "title": "Briefing operativo local",
  "steps": ["solo uno"],
  "limits": ["nada"],
  "stop_condition": ""
}
""".strip()

IMPROVED_PROMPT_JSON = """
{
  "prompt": "Devuelve JSON: title, steps (3+), limits (Ollama local), stop_condition con /salir.",
  "rationale": "El prompt debil no pedia estructura."
}
""".strip()

INVALID_REWRITE = "esto no es un prompt"


class ScriptedClient:
    def __init__(self, responses: list[str | BaseException]) -> None:
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
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return ChatResult(
            content=item,
            model="qwen3.5:4b",
            total_duration_ms=8.0,
            prompt_tokens=11,
            output_tokens=17,
        )

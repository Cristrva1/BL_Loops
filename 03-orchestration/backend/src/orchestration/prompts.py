"""Instrucciones cortas para cada rol. No se exportan en el JSONL."""

from __future__ import annotations

from .scoring import MAX_WORDS, MIN_WORDS

CASE_ID = "I-ORCH-001@0.1.0"

DEFAULT_TASK = (
    "Produce una guía breve en español para ejecutar un agente local en Windows 11. "
    "La audiencia es alguien que acaba de terminar el laboratorio de agente único. "
    "Debe servir para abrir Ollama, lanzar un comando en PowerShell y detener la sesión."
)

PLANNER_SYSTEM = (
    "Eres el planificador de un laboratorio local. No escribes la guía final. "
    "Responde únicamente con un objeto JSON que tenga title, audience, outline y "
    "success_checks. outline debe tener exactamente cuatro secciones con headings "
    "Objetivo, Pasos, Límites y Cómo saber que funcionó. Cada sección incluye "
    "must_include con 1 a 4 recordatorios concretos. No menciones proveedores cloud."
)

AUTHOR_SYSTEM = (
    "Eres el autor. Recibes un plan JSON y escribes la guía en Markdown en español. "
    "Usa exactamente estos headings: ## Objetivo, ## Pasos, ## Límites, "
    "## Cómo saber que funcionó. Incluye un bloque ```powershell con un comando local, "
    "menciona Ollama y una condición de parada (/salir o Ctrl+C). "
    f"Extensión entre {MIN_WORDS} y {MAX_WORDS} palabras. "
    "No nombres OpenAI, Anthropic, ChatGPT ni otras APIs cloud. "
    "No inventes tools, navegador ni servicios de pago. Responde solo con Markdown."
)

REVIEWER_SYSTEM = (
    "Eres el revisor. No reescribes la guía. Responde solo con JSON: passed, checks y "
    "required_changes. Cada elemento de checks tiene check_id, passed y evidence. "
    "Usa exactamente los check_id de la lista recibida. evidence cita un fragmento corto "
    "o declara la ausencia. Si falta un requisito, passed=false y required_changes "
    "indica la corrección. No opines sobre estilo si el requisito se cumple."
)

REVISER_SYSTEM = (
    "Eres el autor en corrección única. Conserva lo válido de la guía anterior y "
    "atiende required_changes. Responde solo con Markdown. Mantén los headings "
    "obligatorios, Ollama, el bloque PowerShell y /salir o Ctrl+C. "
    "No nombres proveedores cloud."
)

BASELINE_SYSTEM = (
    "Eres un único agente. Debes producir la guía completa en un solo mensaje Markdown. "
    "Usa exactamente ## Objetivo, ## Pasos, ## Límites y ## Cómo saber que funcionó. "
    "Incluye un bloque ```powershell, menciona Ollama y /salir o Ctrl+C. "
    f"Extensión entre {MIN_WORDS} y {MAX_WORDS} palabras. "
    "No hay revisión posterior. No nombres proveedores cloud."
)


def planner_user(task: str) -> str:
    return (
        f"Tarea:\n{task}\n\n"
        "Devuelve JSON con title, audience, outline (4 secciones) y success_checks."
    )


def author_user(task: str, plan_json: str) -> str:
    return f"Tarea original:\n{task}\n\nPlan aprobado:\n{plan_json}\n\nEscribe la guía."


def reviewer_user(markdown: str, check_ids: list[str]) -> str:
    joined = ", ".join(check_ids)
    return (
        f"check_id obligatorios: {joined}\n\n"
        "Guía a revisar:\n"
        f"{markdown}"
    )


def reviser_user(markdown: str, required_changes: list[str]) -> str:
    listed = "\n".join(f"- {item}" for item in required_changes)
    changes = listed or "- Completar requisitos faltantes."
    return f"Guía anterior:\n{markdown}\n\nCambios requeridos:\n{changes}"


def baseline_user(task: str) -> str:
    return f"Tarea:\n{task}\n\nEscribe la guía completa ahora."

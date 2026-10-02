"""Instrucciones cortas del generador y del mejorador. No se exportan en el JSONL."""

from __future__ import annotations

CASE_ID = "I-LOOP-003@0.1.0"
LAB_ID = "05-agent-loops"

DEFAULT_TASK = (
    "Redacta un briefing operativo en español para un asistente de ventas local. "
    "La salida debe ser un objeto JSON con title, steps, limits y stop_condition."
)

INITIAL_PROMPT = "Escribe algo útil."

OBJECTIVE = (
    "Mejorar un prompt hasta que su salida cumpla cinco assertions estructurales, "
    "sin superar cinco iteraciones, dos errores o tres minutos."
)

IMPROVEMENT_CONDITION = (
    "Solo se reemplaza el mejor candidato si el score sube. Un empate conserva el anterior."
)

STOP_CONDITION = (
    "Se detiene al alcanzar 5/5, al agotar 5 iteraciones, 2 errores o 180 segundos, "
    "lo que ocurra primero."
)

GENERATOR_FALLBACK_SYSTEM = (
    "Eres el generador de un laboratorio local. Responde solo con el briefing pedido. "
    "No expliques el proceso. No nombres APIs cloud."
)

IMPROVER_SYSTEM = (
    "Eres el mejorador de prompts de un laboratorio local. No ejecutas la tarea. "
    "Recibes el prompt actual y los checks que fallaron. Devuelve solo JSON con "
    "prompt (el nuevo texto de sistema) y rationale corto. El nuevo prompt debe "
    "pedir un objeto JSON con title, steps (minimo 3), limits (Ollama local) y "
    "stop_condition (/salir o presupuesto). No nombres proveedores cloud."
)


def generator_user(task: str) -> str:
    return f"Tarea:\n{task}\n\nProduce ahora la salida."


def improver_user(task: str, current_prompt: str, failed_checks: list[str]) -> str:
    failed = ", ".join(failed_checks) or "ninguno"
    return (
        f"Tarea que debe resolver el prompt:\n{task}\n\n"
        f"Prompt actual:\n{current_prompt}\n\n"
        f"Checks fallidos: {failed}\n\n"
        "Devuelve JSON con prompt y rationale."
    )

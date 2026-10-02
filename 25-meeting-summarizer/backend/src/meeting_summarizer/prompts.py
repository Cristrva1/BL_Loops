"""Plantillas de prompts especializadas para síntesis y extracción estructurada."""

from __future__ import annotations

SYSTEM_PROMPT = """Eres un asistente analista experto en minutas y transcripciones de reuniones y videollamadas de equipos de trabajo.
Tu objetivo es analizar conversaciones con rigor, fidelidad a los hechos discutidos y absoluta ausencia de alucinaciones.
No inventes acuerdos, compromisos, fechas ni nombres que no aparezcan explícitamente en la transcripción.
Siempre responde en español claro, profesional y estructurado."""


def build_single_pass_prompt(
    transcript_text: str,
    title: str,
    participants: list[str],
    mode: str = "completo",
) -> str:
    """Construye el prompt para extracción directa en formato JSON estructurado."""
    participants_str = ", ".join(participants) if participants else "No especificados"

    return f"""Analiza con atención la siguiente transcripción de una reunión de equipo titulada "{title}".
Participantes detectados: {participants_str}
Modo de análisis solicitado: {mode}

Debes responder ÚNICAMENTE con un objeto JSON válido (sin texto antes ni después) con exactamente la siguiente estructura de claves:

{{
  "title": "{title}",
  "executive_summary": "Resumen ejecutivo en 2 a 4 párrafos claros y directos: propósito de la reunión, temas medulares y balance general del encuentro.",
  "topics": [
    {{
      "topic": "Nombre del tema o eje temático",
      "summary": "Resumen conciso de lo discutido y puntos de vista expuestos.",
      "participants_involved": ["Nombre de quien opinó o lideró este tema"]
    }}
  ],
  "decisions": [
    {{
      "decision": "Decisión o acuerdo explícito al que se llegó",
      "rationale": "Motivo o contexto por el cual se tomó esta decisión",
      "impact": "Efecto o consecuencia para el equipo o proyecto"
    }}
  ],
  "action_items": [
    {{
      "task": "Descripción concreta de la acción o tarea acordada",
      "assignee": "Persona o rol responsable (si no se mencionó a nadie exacto, escribe 'Equipo' o 'Sin asignar')",
      "deadline": "Plazo o fecha acordada, o null si no se especificó",
      "priority": "alta, media o baja",
      "context": "Detalle breve o condición de la tarea"
    }}
  ],
  "open_questions": [
    "Duda no resuelta, riesgo advertido o tema que quedó pendiente para la siguiente reunión"
  ],
  "email_followup": "Borrador en formato Markdown de una minuta o correo de seguimiento listo para copiar y enviar al equipo por Slack/Teams/Email. Debe incluir saludo cordial, resumen de 3 viñetas, tabla de compromisos y despedida profesional."
}}

--- INICIO DE LA TRANSCRIPCIÓN ---
{transcript_text}
--- FIN DE LA TRANSCRIPCIÓN ---

Asegúrate de devolver un JSON estrictamente válido, sin comillas rotas ni comentarios.
"""


def build_chunk_summary_prompt(
    chunk_text: str,
    chunk_index: int,
    total_chunks: int,
) -> str:
    """Prompt para resumir un bloque intermedio de una reunión larga."""
    return f"""Estás analizando la PARTE {chunk_index} de {total_chunks} de una reunión de equipo.
Sintetiza de forma clara:
1. Temas y discusiones abordados en este fragmento.
2. Acuerdos o decisiones mencionados.
3. Compromisos o tareas que se hayan asignado a personas con sus respectivos plazos.
4. Dudas o bloqueos que hayan surgido.

--- TEXTO DEL FRAGMENTO ({chunk_index}/{total_chunks}) ---
{chunk_text}
--- FIN DEL FRAGMENTO ---

Proporciona una síntesis densa en información pero sin redundancias.
"""


def build_reduce_prompt(
    chunk_summaries: list[str],
    title: str,
    participants: list[str],
    mode: str = "completo",
) -> str:
    """Prompt para consolidar resúmenes de bloques en el reporte JSON final."""
    participants_str = ", ".join(participants) if participants else "No especificados"
    combined_blocks = "\n\n".join(
        f"### Fragmento {idx + 1}:\n{text}" for idx, text in enumerate(chunk_summaries)
    )

    return f"""A continuación se presentan los resúmenes parciales de los diferentes fragmentos de la reunión titulada "{title}".
Participantes: {participants_str}
Modo: {mode}

Debes consolidar e integrar toda esta información en un ÚNICO reporte final estructurado en formato JSON válido:

{{
  "title": "{title}",
  "executive_summary": "Resumen ejecutivo global y coherente de toda la sesión (2 a 4 párrafos).",
  "topics": [
    {{
      "topic": "Nombre del tema",
      "summary": "Resumen integrado",
      "participants_involved": ["Participante"]
    }}
  ],
  "decisions": [
    {{
      "decision": "Decisión tomada en cualquier parte de la reunión",
      "rationale": "Motivo",
      "impact": "Impacto"
    }}
  ],
  "action_items": [
    {{
      "task": "Tarea concreta",
      "assignee": "Responsable",
      "deadline": "Fecha o null",
      "priority": "alta, media o baja",
      "context": "Contexto"
    }}
  ],
  "open_questions": [
    "Dudas o temas pendientes no resueltos"
  ],
  "email_followup": "Minuta en Markdown lista para enviar por correo o Slack con saludo, puntos clave y tabla de tareas."
}}

--- RESÚMENES PARCIALES ---
{combined_blocks}
--- FIN DE RESÚMENES ---

Devuelve ÚNICAMENTE el JSON válido.
"""


def build_chat_question_prompt(
    transcript_text: str,
    summary_text: str,
    question: str,
) -> str:
    """Prompt para responder consultas sobre lo conversado en la reunión."""
    return f"""El usuario tiene una pregunta específica sobre la siguiente reunión de equipo.
Responde de forma concisa, precisa y verídica basándote ÚNICAMENTE en la transcripción y el resumen.
Si la información no fue mencionada en la videollamada, dilo con honestidad ("En la reunión no se discutió ese punto").
Si citas una afirmación, menciona quién lo dijo o en qué momento (timestamp si está disponible).

--- RESUMEN PREVIO DE LA REUNIÓN ---
{summary_text}

--- TRANSCRIPCIÓN DE REFERENCIA (FRAGMENTOS RELEVANTES) ---
{transcript_text[:12000]}

--- PREGUNTA DEL USUARIO ---
{question}

Respuesta en español:"""

"""Motor central de síntesis, extracción estructurada y orquestación de eventos."""

from __future__ import annotations

import json
import re
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from .chunker import (
    SUMMARY_MAX_WORDS_PER_CHUNK,
    SUMMARY_OVERLAP_WORDS,
    chunk_turns,
    format_turns_to_text,
)
from .contracts import (
    ActionItem,
    ChatResponse,
    KeyDecision,
    MeetingMetadata,
    MeetingSummaryReport,
    PipelineEvent,
    SummarizeRequest,
    TopicDiscussion,
)
from .ollama_client import OllamaClient, OllamaError
from .parser import parse_transcript
from .prompts import (
    SYSTEM_PROMPT,
    build_chat_question_prompt,
    build_chunk_summary_prompt,
    build_reduce_prompt,
    build_single_pass_prompt,
)
from .run_log import export_run_record
from .storage import Storage


def _clean_json_string(raw: str) -> str:
    """Remueve bloques markdown ```json o ``` si el modelo los incluyó."""
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Si empieza por { y termina por }, tomarlo directo
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


class MeetingSummarizerEngine:
    """Coordina el análisis de transcripciones, extracción y eventos en streaming."""

    def __init__(self, ollama: OllamaClient, storage: Storage) -> None:
        self.ollama = ollama
        self.storage = storage

    def parse_only(self, text: str, custom_title: str | None = None) -> tuple[MeetingMetadata, int]:
        """Realiza únicamente el preanálisis sintáctico sin llamar al LLM."""
        turns, metadata = parse_transcript(text, custom_title)
        return metadata, len(turns)

    async def summarize_stream(
        self,
        request: SummarizeRequest,
        meeting_id: str | None = None,
    ) -> AsyncGenerator[PipelineEvent, None]:
        """Ejecuta el pipeline completo de análisis emitiendo eventos de progreso en tiempo real."""
        start_time = time.perf_counter()
        target_meeting_id = meeting_id or str(uuid.uuid4())
        target_model = request.model or self.ollama.default_model

        # Paso 1: Parseo
        yield PipelineEvent(
            stage="parsing",
            progress=10,
            message="Analizando formato de transcripción y detectando participantes...",
            payload={"meeting_id": target_meeting_id},
        )

        turns, metadata = parse_transcript(request.transcript_text, request.title)

        if request.save_to_db:
            self.storage.save_meeting(
                meeting_id=target_meeting_id,
                title=metadata.title,
                raw_transcript=request.transcript_text,
                metadata=metadata,
            )

        yield PipelineEvent(
            stage="parsed",
            progress=25,
            message=(
                f"Formato: {metadata.detected_format.value.upper()} · "
                f"{metadata.total_words} palabras · {len(metadata.participants)} participantes."
            ),
            payload={
                "metadata": metadata.model_dump(),
                "participants": metadata.participants,
            },
        )

        # Paso 2: Partición y verificación de contexto
        chunks = chunk_turns(
            turns,
            max_words_per_chunk=SUMMARY_MAX_WORDS_PER_CHUNK,
            overlap_words=SUMMARY_OVERLAP_WORDS,
        )
        total_chunks = len(chunks)

        yield PipelineEvent(
            stage="chunking",
            progress=35,
            message=f"Estrategia de análisis: {total_chunks} fragmento(s) en modelo {target_model}.",
            payload={"total_chunks": total_chunks},
        )

        raw_json_str = ""

        # Paso 3: Ejecución según longitud
        if total_chunks <= 1:
            yield PipelineEvent(
                stage="analyzing",
                progress=50,
                message=f"Sintetizando y extrayendo acuerdos con {target_model}...",
            )

            prompt = build_single_pass_prompt(
                transcript_text=format_turns_to_text(turns),
                title=metadata.title,
                participants=metadata.participants,
                mode=request.mode,
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            response = self.ollama.chat(
                messages=messages,
                model=target_model,
                temperature=0.2,
                json_format=True,
            )
            raw_json_str = response.content

        else:
            # Modo Map-Reduce para reuniones largas
            chunk_summaries: list[str] = []
            for idx, c in enumerate(chunks):
                pct = 35 + int(35 * ((idx + 1) / total_chunks))
                yield PipelineEvent(
                    stage="analyzing_chunk",
                    progress=pct,
                    message=f"Analizando fragmento {idx + 1} de {total_chunks} ({c.word_count} palabras)...",
                    payload={"current_chunk": idx + 1, "total_chunks": total_chunks},
                )

                chunk_prompt = build_chunk_summary_prompt(
                    chunk_text=c.text_content,
                    chunk_index=c.chunk_index,
                    total_chunks=c.total_chunks,
                )
                chunk_resp = self.ollama.chat(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": chunk_prompt},
                    ],
                    model=target_model,
                    temperature=0.2,
                    json_format=False,
                )
                chunk_summaries.append(chunk_resp.content)

            yield PipelineEvent(
                stage="reducing",
                progress=75,
                message="Consolidando fragmentos en la minuta final estructurada...",
            )

            reduce_prompt = build_reduce_prompt(
                chunk_summaries=chunk_summaries,
                title=metadata.title,
                participants=metadata.participants,
                mode=request.mode,
            )
            reduce_resp = self.ollama.chat(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": reduce_prompt},
                ],
                model=target_model,
                temperature=0.2,
                json_format=True,
            )
            raw_json_str = reduce_resp.content

        # Paso 4: Parseo y normalización del reporte
        yield PipelineEvent(
            stage="structuring",
            progress=85,
            message="Validando esquemas de compromisos y decisiones...",
        )

        report = self._build_report_from_json(
            raw_json=raw_json_str,
            meeting_id=target_meeting_id,
            metadata=metadata,
            model_used=target_model,
            mode=request.mode,
        )

        if request.save_to_db:
            self.storage.save_summary(report)

        # Paso 5: Exportación JSONL determinista
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        runs_dir = self.storage.db_path.parent.parent / "runs"
        export_run_record(report, runs_dir, duration_ms=elapsed_ms)

        yield PipelineEvent(
            stage="completed",
            progress=100,
            message="¡Resumen y compromisos generados exitosamente!",
            payload={"report": report.model_dump()},
        )

    def _build_report_from_json(
        self,
        raw_json: str,
        meeting_id: str,
        metadata: MeetingMetadata,
        model_used: str,
        mode: str,
    ) -> MeetingSummaryReport:
        """Parsea la salida JSON del modelo e hidrata el contrato MeetingSummaryReport."""
        cleaned = _clean_json_string(raw_json)
        now_iso = datetime.now(UTC).isoformat()

        try:
            data = json.loads(cleaned)
        except Exception:
            # Fallback en caso de que el modelo haya devuelto texto libre
            return MeetingSummaryReport(
                meeting_id=meeting_id,
                title=metadata.title,
                executive_summary=raw_json.strip()[:1000],
                topics=[],
                decisions=[],
                action_items=[],
                open_questions=[],
                email_followup=raw_json.strip(),
                metadata=metadata,
                model_used=model_used,
                mode=mode,
                created_at=now_iso,
            )

        # Mapeo tipado
        topics: list[TopicDiscussion] = []
        for t in data.get("topics", []):
            if isinstance(t, dict):
                topics.append(
                    TopicDiscussion(
                        topic=str(t.get("topic", "Tema tratado")),
                        summary=str(t.get("summary", "")),
                        participants_involved=t.get("participants_involved", []) or [],
                    )
                )

        decisions: list[KeyDecision] = []
        for d in data.get("decisions", []):
            if isinstance(d, dict):
                decisions.append(
                    KeyDecision(
                        decision=str(d.get("decision", "")),
                        rationale=d.get("rationale"),
                        impact=d.get("impact"),
                    )
                )
            elif isinstance(d, str):
                decisions.append(KeyDecision(decision=d))

        action_items: list[ActionItem] = []
        for a in data.get("action_items", []):
            if isinstance(a, dict):
                priority_val = str(a.get("priority", "media")).lower()
                if priority_val not in ("alta", "media", "baja"):
                    priority_val = "media"
                action_items.append(
                    ActionItem(
                        task=str(a.get("task", "")),
                        assignee=str(a.get("assignee", "Equipo")),
                        deadline=a.get("deadline"),
                        priority=priority_val,  # type: ignore[arg-type]
                        context=a.get("context"),
                    )
                )

        open_questions: list[str] = [
            str(q) for q in data.get("open_questions", []) if str(q).strip()
        ]

        title_res = str(data.get("title", metadata.title) or metadata.title)
        exec_summary = str(data.get("executive_summary", "")).strip()
        email_followup = str(data.get("email_followup", "")).strip()

        # Si el correo quedó vacío, generar uno por defecto con los datos
        if not email_followup:
            email_followup = (
                f"### Minuta de Reunión: {title_res}\n\n"
                f"**Resumen:**\n{exec_summary}\n\n"
                "**Compromisos acordados:**\n"
                + "\n".join(
                    f"- **{act.assignee}**: {act.task} (Plazo: {act.deadline or 'Por definir'})"
                    for act in action_items
                )
            )

        return MeetingSummaryReport(
            meeting_id=meeting_id,
            title=title_res,
            executive_summary=exec_summary,
            topics=topics,
            decisions=decisions,
            action_items=action_items,
            open_questions=open_questions,
            email_followup=email_followup,
            metadata=metadata,
            model_used=model_used,
            mode=mode,
            created_at=now_iso,
        )

    def ask_meeting_question(
        self,
        meeting_id: str,
        question: str,
        model: str | None = None,
    ) -> ChatResponse:
        """Responde una pregunta sobre lo conversado en la videollamada."""
        meeting = self.storage.get_meeting(meeting_id)
        if not meeting:
            raise OllamaError(f"No se encontró la reunión con id {meeting_id}")

        latest_summary = self.storage.get_latest_summary(meeting_id)
        summary_text = (
            latest_summary.executive_summary if latest_summary else "Sin resumen previo."
        )

        prompt = build_chat_question_prompt(
            transcript_text=meeting["raw_transcript"],
            summary_text=summary_text,
            question=question,
        )

        target_model = model or self.ollama.default_model

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        resp = self.ollama.chat(
            messages=messages,
            model=target_model,
            temperature=0.2,
            json_format=False,
        )

        answer = resp.content
        self.storage.save_chat_message(meeting_id, question, answer)

        return ChatResponse(
            meeting_id=meeting_id,
            question=question,
            answer=answer,
            citations=[],
        )

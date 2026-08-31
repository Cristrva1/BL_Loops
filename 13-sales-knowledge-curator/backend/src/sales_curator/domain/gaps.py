"""Convierte cobertura baja, vacío o caducidad en preguntas investigables."""

from __future__ import annotations

from uuid import uuid4

from sales_curator.contracts.models import (
    GapRecord,
    ResearchTask,
    SourceRecord,
    TaskStatus,
)
from sales_curator.domain.policy import EXPECTED_TOPICS
from sales_curator.hashing import with_content_hash


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def plan_from_inventory(sources: list[SourceRecord]) -> tuple[list[GapRecord], list[ResearchTask]]:
    present: set[str] = set()
    for source in sources:
        present.update(source.topics)
    gaps: list[GapRecord] = []
    tasks: list[ResearchTask] = []
    for topic in EXPECTED_TOPICS:
        covering = [item.source_id for item in sources if topic in item.topics]
        if covering:
            continue
        gap = with_content_hash(
            GapRecord(
                gap_id=_id("gap"),
                topic=topic,
                reason=f"Ninguna fuente del inventario cubre el tema {topic}",
                source_ids=[],
                content_hash="0" * 64,
            )
        )
        gaps.append(gap)
        needs_web = topic == "after-sales"
        tasks.append(
            with_content_hash(
                ResearchTask(
                    task_id=_id("tsk"),
                    question=(
                        f"¿Qué prácticas vigentes existen para {topic} "
                        "en venta consultiva de vivienda?"
                    ),
                    motivation=gap.reason,
                    target_kinds=["primary", "challenging"] if needs_web else ["local"],
                    allowlist=[],
                    budget_urls=0,
                    sufficiency="Al menos una fuente primaria con fecha y localizador",
                    stop_criterion="Tres rondas o presupuesto agotado",
                    status=TaskStatus.PLANNED,
                    content_hash="0" * 64,
                )
            )
        )
    for source in sources:
        if source.quarantine_status.value == "empty":
            gap = with_content_hash(
                GapRecord(
                    gap_id=_id("gap"),
                    topic=source.topics[0] if source.topics else "unspecified",
                    reason=f"La fuente {source.source_id} está vacía y no proyecta conocimiento",
                    source_ids=[source.source_id],
                    content_hash="0" * 64,
                )
            )
            gaps.append(gap)
    return gaps, tasks

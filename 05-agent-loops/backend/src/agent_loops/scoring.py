"""Cinco assertions estructurales del caso I-LOOP-003."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import CheckView
from .json_parse import JsonParseError, extract_json_object

TITLE_MIN_CHARS = 8
STEPS_MIN = 3
STOP_MARKERS = ("/salir", "presupuesto", "iteracion", "iteración", "timeout", "parada")


@dataclass(frozen=True, slots=True)
class ScoreResult:
    passed: bool
    checks: tuple[CheckView, ...]
    parsed: dict[str, object] | None

    @property
    def checks_passed(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def checks_total(self) -> int:
        return len(self.checks)

    def failed_ids(self) -> list[str]:
        return [check.check_id for check in self.checks if not check.passed]


def score_output(text: str) -> ScoreResult:
    checks: list[CheckView] = []
    parsed: dict[str, object] | None
    try:
        parsed = extract_json_object(text)
        json_ok = True
        json_evidence = "Hay un objeto JSON."
    except JsonParseError as exc:
        parsed = None
        json_ok = False
        json_evidence = str(exc)

    checks.append(
        CheckView(
            check_id="is_json_object",
            title="La salida es un objeto JSON",
            passed=json_ok,
            evidence=json_evidence,
        )
    )

    title = parsed.get("title") if parsed is not None else None
    title_ok = isinstance(title, str) and len(title.strip()) >= TITLE_MIN_CHARS
    checks.append(
        CheckView(
            check_id="has_title",
            title=f"title es un texto de al menos {TITLE_MIN_CHARS} caracteres",
            passed=title_ok,
            evidence=(
                f"title tiene {len(title.strip())} caracteres."
                if title_ok and isinstance(title, str)
                else "Falta title o es demasiado corto."
            ),
        )
    )

    steps = parsed.get("steps") if parsed is not None else None
    step_items = (
        [item.strip() for item in steps if isinstance(item, str) and item.strip()]
        if isinstance(steps, list)
        else []
    )
    steps_ok = len(step_items) >= STEPS_MIN
    checks.append(
        CheckView(
            check_id="has_steps",
            title=f"steps es una lista con al menos {STEPS_MIN} textos",
            passed=steps_ok,
            evidence=(
                f"{len(step_items)} pasos utilizables."
                if isinstance(steps, list)
                else "Falta el arreglo steps."
            ),
        )
    )

    limits = parsed.get("limits") if parsed is not None else None
    limit_items = (
        [item.strip() for item in limits if isinstance(item, str) and item.strip()]
        if isinstance(limits, list)
        else []
    )
    local_hit = next(
        (
            item
            for item in limit_items
            if "ollama" in item.casefold() or "local" in item.casefold()
        ),
        None,
    )
    limits_ok = local_hit is not None
    checks.append(
        CheckView(
            check_id="has_limits",
            title="limits menciona Ollama o un limite local",
            passed=limits_ok,
            evidence=(
                f"Aparece '{local_hit}'."
                if local_hit is not None
                else "No hay limits locales o no mencionan Ollama."
            ),
        )
    )

    stop = parsed.get("stop_condition") if parsed is not None else None
    stop_text = stop.strip() if isinstance(stop, str) else ""
    folded_stop = stop_text.casefold()
    stop_hit = next((marker for marker in STOP_MARKERS if marker in folded_stop), None)
    stop_ok = bool(stop_text) and stop_hit is not None
    checks.append(
        CheckView(
            check_id="has_stop_condition",
            title="stop_condition declara /salir, presupuesto o parada",
            passed=stop_ok,
            evidence=(
                f"Aparece '{stop_hit}'."
                if stop_ok
                else "Falta stop_condition o no declara una parada."
            ),
        )
    )

    return ScoreResult(
        passed=all(check.passed for check in checks),
        checks=tuple(checks),
        parsed=parsed,
    )


def preview_text(text: str, limit: int = 200) -> str:
    compact = re.sub(r"\s+", " ", text.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"

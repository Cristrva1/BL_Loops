"""Lista de comprobaciones deterministas del caso I-ORCH-001."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import CheckView

CLOUD_TERMS = (
    "openai",
    "anthropic",
    "chatgpt",
    "claude api",
    "gemini api",
    "gpt-4",
    "gpt-5",
)
REQUIRED_HEADINGS = (
    ("has_objetivo", "Incluye el heading Objetivo", r"^#{1,3}\s*objetivo\b"),
    ("has_pasos", "Incluye el heading Pasos", r"^#{1,3}\s*pasos\b"),
    ("has_limites", "Incluye el heading Límites|Limites", r"^#{1,3}\s*l[ií]mites\b"),
    (
        "has_exito",
        "Incluye el heading de comprobación de éxito",
        r"^#{1,3}\s*(c[oó]mo saber que funcion[oó]|resultado esperado)\b",
    ),
)
MIN_WORDS = 40
MAX_WORDS = 800


@dataclass(frozen=True, slots=True)
class ScoreResult:
    passed: bool
    word_count: int
    headings: tuple[str, ...]
    checks: tuple[CheckView, ...]

    @property
    def checks_passed(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def checks_total(self) -> int:
        return len(self.checks)

    def failed_ids(self) -> list[str]:
        return [check.check_id for check in self.checks if not check.passed]


def word_count(text: str) -> int:
    return len([token for token in re.split(r"\s+", text.strip()) if token])


def extract_headings(text: str) -> tuple[str, ...]:
    found = re.findall(r"^#{1,3}\s+(.+)$", text, flags=re.MULTILINE)
    return tuple(item.strip() for item in found if item.strip())


def score_guide(markdown: str) -> ScoreResult:
    text = markdown.strip()
    folded = text.casefold()
    words = word_count(text)
    headings = extract_headings(text)
    checks: list[CheckView] = []

    for check_id, title, pattern in REQUIRED_HEADINGS:
        matched = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        checks.append(
            CheckView(
                check_id=check_id,
                title=title,
                passed=matched is not None,
                evidence=matched.group(0).strip() if matched else "Heading ausente.",
            )
        )

    ollama_ok = "ollama" in folded
    checks.append(
        CheckView(
            check_id="mentions_ollama",
            title="Menciona Ollama",
            passed=ollama_ok,
            evidence="Aparece 'Ollama'." if ollama_ok else "No menciona Ollama.",
        )
    )

    powershell_ok = bool(
        re.search(r"```powershell\b", folded)
        or re.search(r"\bset-location\b", folded)
        or re.search(r"\buv run\b", folded)
    )
    checks.append(
        CheckView(
            check_id="has_powershell",
            title="Incluye un comando PowerShell o uv run",
            passed=powershell_ok,
            evidence=(
                "Hay un comando local."
                if powershell_ok
                else "No hay comando PowerShell ni uv run."
            ),
        )
    )

    stop_ok = bool(re.search(r"/salir|ctrl\+c|ctrl-c", folded))
    checks.append(
        CheckView(
            check_id="has_stop_condition",
            title="Declara una condición de parada",
            passed=stop_ok,
            evidence="Hay /salir o Ctrl+C." if stop_ok else "Falta /salir o Ctrl+C.",
        )
    )

    cloud_hit = next((term for term in CLOUD_TERMS if term in folded), None)
    checks.append(
        CheckView(
            check_id="no_cloud_fallback",
            title="No nombra APIs cloud",
            passed=cloud_hit is None,
            evidence="Sin marcas cloud." if cloud_hit is None else f"Aparece '{cloud_hit}'.",
        )
    )

    length_ok = MIN_WORDS <= words <= MAX_WORDS
    checks.append(
        CheckView(
            check_id="length_ok",
            title=f"Extensión entre {MIN_WORDS} y {MAX_WORDS} palabras",
            passed=length_ok,
            evidence=f"{words} palabras.",
        )
    )

    return ScoreResult(
        passed=all(check.passed for check in checks),
        word_count=words,
        headings=headings,
        checks=tuple(checks),
    )


def preview_text(text: str, limit: int = 200) -> str:
    compact = re.sub(r"\s+", " ", text.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"

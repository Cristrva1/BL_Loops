"""El texto adquirido es dato. Nunca se ejecuta como instrucción."""

from __future__ import annotations

import re

INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.I),
    re.compile(r"network_enabled\s*=\s*true", re.I),
    re.compile(r"you\s+are\s+now", re.I),
    re.compile(r"<\s*system\s*>", re.I),
    re.compile(r"call\s+the\s+tool", re.I),
    re.compile(r"publish\s+every\s+claim", re.I),
)

PII_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PII_PHONE = re.compile(r"\+\d{6,15}\b")
SECRET_PATTERNS = (
    re.compile(r"\bapi[_-]?key\b", re.I),
    re.compile(r"\bsecret_token\b", re.I),
    re.compile(r"password\s*=", re.I),
    re.compile(r"\bsk-[A-Za-z0-9]{8,}"),
)


def find_injection_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits


def find_sensitive_hits(text: str) -> list[str]:
    hits: list[str] = []
    if PII_EMAIL.search(text):
        hits.append("email")
    if PII_PHONE.search(text):
        hits.append("phone")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        hits.append("secret_marker")
    return hits


def strip_control_instructions(text: str) -> str:
    """Conserva el texto como dato, sin promoverlo a mensaje de sistema."""

    return text

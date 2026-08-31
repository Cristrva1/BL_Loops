"""Redacta síntesis propias solo con afirmaciones del ledger."""

from __future__ import annotations

from collections import defaultdict

from sales_curator.contracts.models import ClaimRecord, ClaimStatus, KnowledgeDraft
from sales_curator.hashing import with_content_hash

PUBLISHABLE = {
    ClaimStatus.HUMAN_APPROVED,
    ClaimStatus.SUPPORTED_SINGLE_SOURCE,
    ClaimStatus.CORROBORATED,
}


def drafts_from_claims(claims: list[ClaimRecord]) -> list[KnowledgeDraft]:
    grouped: dict[str, list[ClaimRecord]] = defaultdict(list)
    for claim in claims:
        if claim.status == ClaimStatus.HUMAN_APPROVED:
            grouped[claim.topic].append(claim)
    drafts: list[KnowledgeDraft] = []
    for topic, items in sorted(grouped.items()):
        lines = [
            f"# {topic}",
            "",
            "Síntesis editorial a partir del ledger. Cada frase cita su localizador.",
            "",
        ]
        ids: list[str] = []
        for claim in items:
            locator = claim.evidence[0].locator if claim.evidence else "L?"
            source_id = claim.evidence[0].source_id if claim.evidence else "unknown"
            limit = ""
            if claim.population:
                limit = f" Aplica a {claim.population}."
            if claim.claim_type.value == "anecdotal":
                limit += " Es una experiencia puntual, no una regla general."
            if claim.claim_type.value == "vendor_self_claim":
                limit += " El proveedor declara esto; no es validación independiente."
            lines.append(f"- {claim.canonical_text}{limit} `[{source_id} {locator}]`")
            ids.append(claim.claim_id)
        markdown = "\n".join(lines) + "\n"
        drafts.append(
            with_content_hash(
                KnowledgeDraft(
                    topic=topic,
                    markdown=markdown,
                    claim_ids=ids,
                    content_hash="0" * 64,
                )
            )
        )
    return drafts


def knowledge_contains_only_ledger(markdown: str, claims: list[ClaimRecord]) -> bool:
    allowed = {
        claim.canonical_text for claim in claims if claim.status == ClaimStatus.HUMAN_APPROVED
    }
    for claim in claims:
        if claim.status != ClaimStatus.HUMAN_APPROVED and claim.canonical_text in markdown:
            return False
    return all(text in markdown for text in allowed) if allowed else True

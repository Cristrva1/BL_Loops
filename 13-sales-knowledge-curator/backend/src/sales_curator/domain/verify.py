"""Verificadores deterministas: cita, fecha, duplicado, independencia y conflicto."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from sales_curator.contracts.models import (
    AdversarialFinding,
    ClaimCandidate,
    ClaimRecord,
    ClaimStatus,
    ClaimType,
    ConflictRecord,
    ConflictType,
    EvidenceLink,
    EvidenceRelation,
    Independence,
    Materiality,
    QualityScores,
    QuarantineStatus,
    SourceRecord,
    SupportAssessment,
)
from sales_curator.domain.extract import fragment_at_locator
from sales_curator.domain.ingest import IngestedSource, normalize_text
from sales_curator.domain.threats import find_injection_hits
from sales_curator.hashing import sha256_text, with_content_hash


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _now(clock: datetime | None) -> datetime:
    return clock or datetime.now(UTC)


def _years_apart(newer: date, older: date) -> float:
    return (newer - older).days / 365.25


def _support_assessment(claim_text: str, fragment: str | None) -> SupportAssessment:
    if fragment is None:
        return SupportAssessment.DOES_NOT_SUPPORT
    if normalize_text(claim_text) in normalize_text(fragment):
        return SupportAssessment.SUPPORTS
    return SupportAssessment.DOES_NOT_SUPPORT


def _quality(
    source: SourceRecord,
    candidate: ClaimCandidate,
    assessment: SupportAssessment,
    as_of: date,
    independent: bool,
) -> QualityScores:
    recency = 2
    if candidate.valid_until and candidate.valid_until < as_of:
        recency = 0
    elif source.published_at:
        age = _years_apart(as_of, source.published_at)
        recency = 4 if age <= 2 else 1 if age <= 6 else 0
    authority = 3 if source.rights_clarity >= 3 and source.author else 1
    proximity = 4 if assessment == SupportAssessment.SUPPORTS else 0
    independence = 4 if independent else 0
    applicability = 3 if candidate.population else 2
    integrity = 0 if source.quarantine_status == QuarantineStatus.INJECTION else 4
    return QualityScores(
        authority=authority,
        evidence_proximity=proximity,
        recency=recency,
        independence=independence,
        applicability=applicability,
        extraction_integrity=integrity,
        rights_clarity=source.rights_clarity,
    )


def _initial_status(
    source: SourceRecord,
    candidate: ClaimCandidate,
    assessment: SupportAssessment,
    as_of: date,
) -> ClaimStatus:
    if source.quarantine_status == QuarantineStatus.INJECTION:
        return ClaimStatus.REJECTED
    if source.quarantine_status in {
        QuarantineStatus.UNCERTAIN_RIGHTS,
        QuarantineStatus.OVERSIZE,
        QuarantineStatus.UNSUPPORTED_MIME,
    }:
        return ClaimStatus.QUARANTINED
    if assessment != SupportAssessment.SUPPORTS:
        return ClaimStatus.UNSUPPORTED
    if candidate.valid_until and candidate.valid_until < as_of:
        return ClaimStatus.OUTDATED
    if (
        source.published_at
        and _years_apart(as_of, source.published_at) > 5
        and candidate.claim_type == ClaimType.PRESCRIPTIVE
    ):
        return ClaimStatus.OUTDATED
    if candidate.claim_type == ClaimType.VENDOR_SELF_CLAIM and not candidate.method:
        return ClaimStatus.UNSUPPORTED
    if candidate.claim_type == ClaimType.EMPIRICAL and (
        not candidate.method or not candidate.sample
    ):
        return ClaimStatus.UNSUPPORTED
    if candidate.claim_type == ClaimType.ANECDOTAL:
        return ClaimStatus.SUPPORTED_SINGLE_SOURCE
    return ClaimStatus.SUPPORTED_SINGLE_SOURCE


def build_claim(
    candidate: ClaimCandidate,
    source: SourceRecord,
    ingested: IngestedSource,
    as_of: date,
    *,
    clock: datetime | None = None,
) -> ClaimRecord:
    fragment = fragment_at_locator(ingested.full_text, candidate.locator)
    assessment = _support_assessment(candidate.text, fragment)
    independent = source.independence == Independence.ORIGINAL
    evidence = with_content_hash(
        EvidenceLink(
            claim_id=candidate.claim_id,
            source_id=source.source_id,
            locator=candidate.locator,
            relation=EvidenceRelation.SUPPORTS,
            fragment_min=(fragment or candidate.text)[:800],
            fragment_hash=sha256_text(fragment or ""),
            support_assessment=assessment,
            content_hash="0" * 64,
        )
    )
    stamp = _now(clock)
    return with_content_hash(
        ClaimRecord(
            claim_id=candidate.claim_id,
            canonical_text=candidate.text,
            claim_type=candidate.claim_type,
            topic=candidate.topic,
            population=candidate.population,
            context=candidate.context,
            jurisdiction=candidate.jurisdiction,
            valid_from=candidate.valid_from,
            valid_until=candidate.valid_until,
            method=candidate.method,
            sample=candidate.sample,
            status=_initial_status(source, candidate, assessment, as_of),
            version=1,
            conflicts_with=candidate.conflicts_with,
            supersedes=candidate.supersedes,
            created_by="claim_extractor",
            created_at=stamp,
            updated_at=stamp,
            quality=_quality(source, candidate, assessment, as_of, independent),
            evidence=[evidence],
            challenge_note=None,
            content_hash="0" * 64,
        )
    )


def _merge_identity(claim: ClaimRecord) -> tuple[object, ...]:
    """Sólo une la misma afirmación editorial, nunca texto con distinto alcance."""

    has_relations = bool(claim.conflicts_with or claim.supersedes)
    return (
        normalize_text(claim.canonical_text),
        claim.claim_type,
        claim.topic,
        claim.population,
        claim.context,
        claim.jurisdiction,
        claim.valid_from,
        claim.valid_until,
        claim.method,
        claim.sample,
        tuple(claim.conflicts_with),
        claim.supersedes,
        claim.claim_id if has_relations else None,
    )


def _retarget_evidence(
    link: EvidenceLink,
    claim_id: str,
    *,
    relation: EvidenceRelation | None = None,
) -> EvidenceLink:
    updates: dict[str, object] = {}
    if link.claim_id != claim_id:
        updates["claim_id"] = claim_id
    if relation is not None and link.relation != relation:
        updates["relation"] = relation
    if not updates:
        return link
    updates["content_hash"] = "0" * 64
    return with_content_hash(link.model_copy(update=updates))


def merge_duplicates(
    claims: list[ClaimRecord], sources: dict[str, SourceRecord]
) -> list[ClaimRecord]:
    """Une duplicados editoriales compatibles sin perder alcance ni integridad referencial."""

    by_identity: dict[tuple[object, ...], ClaimRecord] = {}
    identity_by_claim_id: dict[str, tuple[object, ...]] = {}
    ordered: list[ClaimRecord] = []
    for claim in claims:
        key = _merge_identity(claim)
        prior_identity = identity_by_claim_id.get(claim.claim_id)
        if prior_identity is not None and prior_identity != key:
            raise ValueError(f"claim_id duplicado con contenido incompatible: {claim.claim_id}")
        identity_by_claim_id[claim.claim_id] = key
        existing = by_identity.get(key)
        if existing is None:
            normalized_evidence = [
                _retarget_evidence(link, claim.claim_id) for link in claim.evidence
            ]
            normalized = claim
            if normalized_evidence != claim.evidence:
                normalized = with_content_hash(
                    claim.model_copy(
                        update={"evidence": normalized_evidence, "content_hash": "0" * 64}
                    )
                )
            by_identity[key] = normalized
            ordered.append(normalized)
            continue
        extra = []
        for link in claim.evidence:
            source = sources.get(link.source_id)
            if source and source.independence == Independence.SYNDICATED:
                extra.append(
                    _retarget_evidence(
                        link,
                        existing.claim_id,
                        relation=EvidenceRelation.QUALIFIES,
                    )
                )
            else:
                extra.append(_retarget_evidence(link, existing.claim_id))
        merged_evidence = list(existing.evidence) + extra
        origin_ids = {
            sources[link.source_id].origin_source_id
            for link in merged_evidence
            if link.source_id in sources
            and link.support_assessment == SupportAssessment.SUPPORTS
            and sources[link.source_id].independence == Independence.ORIGINAL
        }
        status = existing.status
        if (
            len(origin_ids) >= 2
            and status == ClaimStatus.SUPPORTED_SINGLE_SOURCE
            and existing.claim_type != ClaimType.ANECDOTAL
        ):
            status = ClaimStatus.CORROBORATED
        updated = with_content_hash(
            existing.model_copy(
                update={"evidence": merged_evidence, "status": status, "content_hash": "0" * 64}
            )
        )
        by_identity[key] = updated
        ordered[ordered.index(existing)] = updated
    return ordered


def detect_conflicts(claims: list[ClaimRecord]) -> list[ConflictRecord]:
    conflicts: list[ConflictRecord] = []
    active_statuses = {
        ClaimStatus.SUPPORTED_SINGLE_SOURCE,
        ClaimStatus.CORROBORATED,
        ClaimStatus.DISPUTED,
    }
    active = {claim.claim_id: claim for claim in claims if claim.status in active_statuses}
    seen: set[tuple[str, str]] = set()
    for left in active.values():
        for right_id in left.conflicts_with:
            right = active.get(right_id)
            if right is None or left.claim_id not in right.conflicts_with:
                continue
            if left.topic != right.topic:
                continue
            if normalize_text(left.canonical_text) == normalize_text(right.canonical_text):
                continue
            pair = tuple(sorted((left.claim_id, right.claim_id)))
            if pair in seen:
                continue
            seen.add(pair)
            conflicts.append(
                with_content_hash(
                    ConflictRecord(
                        conflict_id=_id("cfl"),
                        claim_ids=list(pair),
                        conflict_type=ConflictType.DIRECT_CONTRADICTION,
                        topic=left.topic,
                        evidence_by_side={
                            left.claim_id: [item.source_id for item in left.evidence],
                            right.claim_id: [item.source_id for item in right.evidence],
                        },
                        materiality=Materiality.MATERIAL,
                        resolution=None,
                        owner=None,
                        content_hash="0" * 64,
                    )
                )
            )
    return conflicts


def apply_conflicts(
    claims: list[ClaimRecord], conflicts: list[ConflictRecord]
) -> list[ClaimRecord]:
    disputed = {claim_id for conflict in conflicts for claim_id in conflict.claim_ids}
    updated: list[ClaimRecord] = []
    for claim in claims:
        if claim.claim_id in disputed and claim.status not in {
            ClaimStatus.REJECTED,
            ClaimStatus.QUARANTINED,
            ClaimStatus.OUTDATED,
            ClaimStatus.UNSUPPORTED,
        }:
            updated.append(
                with_content_hash(
                    claim.model_copy(
                        update={"status": ClaimStatus.DISPUTED, "content_hash": "0" * 64}
                    )
                )
            )
        else:
            updated.append(claim)
    return updated


def _coherent_supersession(replacement: ClaimRecord, outdated: ClaimRecord) -> bool:
    previous_boundary = outdated.valid_until or outdated.valid_from
    return (
        replacement.status in {ClaimStatus.SUPPORTED_SINGLE_SOURCE, ClaimStatus.CORROBORATED}
        and outdated.status == ClaimStatus.OUTDATED
        and replacement.topic == outdated.topic
        and replacement.valid_from is not None
        and previous_boundary is not None
        and replacement.valid_from > previous_boundary
        and (replacement.valid_until is None or replacement.valid_until >= replacement.valid_from)
    )


def supersede_outdated(claims: list[ClaimRecord]) -> list[ClaimRecord]:
    by_id = {claim.claim_id: claim for claim in claims}
    valid_replacements: set[str] = set()
    for replacement in claims:
        if replacement.supersedes is None:
            continue
        outdated = by_id.get(replacement.supersedes)
        if outdated is not None and _coherent_supersession(replacement, outdated):
            valid_replacements.add(outdated.claim_id)
    return [
        with_content_hash(
            claim.model_copy(update={"status": ClaimStatus.SUPERSEDED, "content_hash": "0" * 64})
        )
        if claim.claim_id in valid_replacements
        else claim
        for claim in claims
    ]


def adversarial_scan(
    sources: list[SourceRecord],
    claims: list[ClaimRecord],
    ingested: list[IngestedSource],
) -> list[AdversarialFinding]:
    findings: list[AdversarialFinding] = []
    text_by_source = {item.source.source_id: item.full_text for item in ingested}
    for source in sources:
        hits = find_injection_hits(text_by_source.get(source.source_id, ""))
        if hits:
            findings.append(
                with_content_hash(
                    AdversarialFinding(
                        finding_id=_id("adv"),
                        kind="prompt_injection",
                        object_id=source.source_id,
                        detail="Instrucciones incrustadas tratadas como dato, no como política",
                        content_hash="0" * 64,
                    )
                )
            )
        if source.independence == Independence.SYNDICATED:
            findings.append(
                with_content_hash(
                    AdversarialFinding(
                        finding_id=_id("adv"),
                        kind="circular_evidence",
                        object_id=source.source_id,
                        detail=(
                            f"Cadena de origen {source.origin_source_id}; "
                            "no es corroboración independiente"
                        ),
                        content_hash="0" * 64,
                    )
                )
            )
        if source.quarantine_status == QuarantineStatus.UNCERTAIN_RIGHTS:
            findings.append(
                with_content_hash(
                    AdversarialFinding(
                        finding_id=_id("adv"),
                        kind="rights_unclear",
                        object_id=source.source_id,
                        detail="Derechos inciertos: cuarentena y fuera del release",
                        content_hash="0" * 64,
                    )
                )
            )
    for claim in claims:
        if claim.claim_type == ClaimType.EMPIRICAL and not claim.population:
            findings.append(
                with_content_hash(
                    AdversarialFinding(
                        finding_id=_id("adv"),
                        kind="scope_excess",
                        object_id=claim.claim_id,
                        detail="Afirmación empírica sin población explícita",
                        content_hash="0" * 64,
                    )
                )
            )
    return findings


def note_missing_challenge(
    claims: list[ClaimRecord], topics_with_conflict: set[str]
) -> list[ClaimRecord]:
    updated: list[ClaimRecord] = []
    for claim in claims:
        if claim.topic in topics_with_conflict:
            updated.append(claim)
            continue
        if claim.status in {
            ClaimStatus.SUPPORTED_SINGLE_SOURCE,
            ClaimStatus.CORROBORATED,
        }:
            updated.append(
                with_content_hash(
                    claim.model_copy(
                        update={
                            "challenge_note": (
                                "Fuente desafiante buscada en el corpus local; no se encontró."
                            ),
                            "content_hash": "0" * 64,
                        }
                    )
                )
            )
        else:
            updated.append(claim)
    return updated

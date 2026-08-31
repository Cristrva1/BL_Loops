"""Staging, aprobación exacta, publicación atómica y validación autónoma."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path, PurePosixPath

from pydantic import ValidationError

from sales_curator.contracts.models import (
    ClaimRecord,
    ClaimStatus,
    ConflictRecord,
    KnowledgeDraft,
    KnowledgeRelease,
    ReviewDecision,
    ReviewVerdict,
    SourceRecord,
)
from sales_curator.domain.editor import drafts_from_claims
from sales_curator.domain.threats import find_sensitive_hits
from sales_curator.evaluation.gate import claim_identity_hash, claim_passes_technical_gate
from sales_curator.hashing import has_valid_content_hash, sha256_text, with_content_hash

MANIFEST_NAME = "manifest.json"
CANDIDATE_DIFF_NAME = "candidate-diff.json"
CANDIDATE_APPROVAL_NAME = "candidate-approval.json"
KNOWLEDGE_RELEASE_NAME = "knowledge-release.json"
PUBLISHED_CLAIM_STATUSES = {ClaimStatus.HUMAN_APPROVED, ClaimStatus.PUBLISHED}


class ReleaseError(ValueError):
    """El candidato no puede publicarse."""


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


def _dump(payload: object) -> str:
    data = payload.model_dump(mode="json") if hasattr(payload, "model_dump") else payload
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _jsonl(rows: list[object]) -> str:
    lines = []
    for row in rows:
        data = row.model_dump(mode="json") if hasattr(row, "model_dump") else row
        lines.append(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return "\n".join(lines) + ("\n" if lines else "")


def _safe_file(folder: Path, relative: str) -> Path | None:
    logical = PurePosixPath(relative)
    if logical.is_absolute() or not logical.parts or ".." in logical.parts:
        return None
    path = (folder / Path(*logical.parts)).resolve()
    if not path.is_relative_to(folder.resolve()):
        return None
    return path


def _hash_text_file(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def _candidate_files(folder: Path) -> set[str]:
    excluded = {MANIFEST_NAME, CANDIDATE_APPROVAL_NAME, KNOWLEDGE_RELEASE_NAME}
    return {
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if path.is_file() and path.relative_to(folder).as_posix() not in excluded
    }


def _package_files(folder: Path) -> set[str]:
    return {
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if path.is_file() and path.relative_to(folder).as_posix() != KNOWLEDGE_RELEASE_NAME
    }


def manifest_hash(folder: Path) -> str:
    path = folder / MANIFEST_NAME
    if not path.is_file():
        raise ReleaseError("falta manifest.json")
    return _hash_text_file(path)


def _is_exact_claim_approval(review: ReviewDecision, claim: ClaimRecord) -> bool:
    return (
        review.object_type == "claim"
        and review.object_id == claim.claim_id
        and review.decision == ReviewVerdict.APPROVED
        and review.approved_hash == claim_identity_hash(claim)
        and review.decided_at >= claim.updated_at
        and has_valid_content_hash(review)
    )


def _release_claims(
    sources: list[SourceRecord],
    claims: list[ClaimRecord],
    reviews: list[ReviewDecision],
) -> list[ClaimRecord]:
    """Selecciona claims aprobados sin cambiar la identidad editorial revisada."""

    redistribution = {source.source_id: source.redistribution_allowed for source in sources}
    exported: list[ClaimRecord] = []
    for claim in claims:
        if claim.status not in PUBLISHED_CLAIM_STATUSES:
            continue
        if not has_valid_content_hash(claim) or any(
            not has_valid_content_hash(link) for link in claim.evidence
        ):
            continue
        if not claim.evidence or any(
            not redistribution.get(link.source_id, False) for link in claim.evidence
        ):
            continue
        if claim_passes_technical_gate(claim):
            continue
        if not any(_is_exact_claim_approval(review, claim) for review in reviews):
            continue
        exported.append(claim)
    return exported


def _release_reviews(
    claims: list[ClaimRecord], reviews: list[ReviewDecision]
) -> list[ReviewDecision]:
    """Incluye sólo aprobaciones exactas de los claims realmente exportados."""

    claim_by_id = {claim.claim_id: claim for claim in claims}
    return [
        review
        for review in reviews
        if (claim := claim_by_id.get(review.object_id)) is not None
        and _is_exact_claim_approval(review, claim)
    ]


def build_staging(
    staging_root: Path,
    run_id: str,
    *,
    candidate_id: str,
    candidate_diff: dict[str, object],
    sources: list[SourceRecord],
    claims: list[ClaimRecord],
    conflicts: list[ConflictRecord],
    reviews: list[ReviewDecision],
    drafts: list[KnowledgeDraft],
    metrics: dict[str, float | int | None],
    domain: str,
    as_of: date,
    model_versions: dict[str, str],
) -> Path:
    folder = staging_root / run_id
    if folder.exists():
        raise ReleaseError("El staging de esta corrida ya existe")
    knowledge = folder / "knowledge"
    knowledge.mkdir(parents=True)
    exported_claims = _release_claims(sources, claims, reviews)
    exported_reviews = _release_reviews(exported_claims, reviews)
    # El Markdown recibido se ignora deliberadamente: el paquete se regenera desde los claims
    # cuya identidad, aprobación y evidencia redistribuible ya pasaron el gate.
    _ = drafts
    generated_drafts = drafts_from_claims(exported_claims)
    included_ids = sorted(claim.claim_id for claim in exported_claims)
    included_id_set = set(included_ids)
    excluded_ids = sorted(
        claim.claim_id for claim in claims if claim.claim_id not in included_id_set
    )
    candidate_diff.update(
        {
            "included_claim_ids": included_ids,
            "excluded_claim_ids": excluded_ids,
        }
    )
    files: dict[str, str] = {
        "sources.jsonl": _jsonl(sources),
        "claims.jsonl": _jsonl(exported_claims),
        "conflicts.jsonl": _jsonl(conflicts),
        "review-decisions.jsonl": _jsonl(exported_reviews),
        CANDIDATE_DIFF_NAME: _dump(candidate_diff),
        "evaluation.json": _dump(metrics),
        "CHANGELOG.md": (
            f"# Changelog\n\n- Candidato de la corrida `{run_id}` al {as_of.isoformat()}.\n"
            "- Afirmaciones aprobadas: "
            f"{len(exported_claims)}.\n"
        ),
        "knowledge/README.md": (
            "# Paquete de conocimiento\n\n"
            "Documentos redactados a partir del ledger. No reproducen la fuente completa.\n"
        ),
    }
    for draft in generated_drafts:
        files[f"knowledge/{draft.topic}.md"] = draft.markdown
    hashes: dict[str, str] = {}
    for relative, content in files.items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        hashes[relative] = sha256_text(content)
    manifest = {
        "schema_version": "1.0.0",
        "candidate_id": candidate_id,
        "run_id": run_id,
        "domain": domain,
        "as_of": as_of.isoformat(),
        "file_hashes": hashes,
        "model_versions": model_versions,
    }
    atomic_write(folder / MANIFEST_NAME, _dump(manifest))
    return folder


def _read_claims(folder: Path) -> tuple[list[ClaimRecord], list[str]]:
    path = folder / "claims.jsonl"
    if not path.is_file():
        return [], ["falta claims.jsonl"]
    claims: list[ClaimRecord] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            claims.append(ClaimRecord.model_validate_json(line))
        except ValidationError:
            errors.append(f"claims.jsonl inválido en línea {line_number}")
    return claims, errors


def _read_sources(folder: Path) -> tuple[list[SourceRecord], list[str]]:
    path = folder / "sources.jsonl"
    if not path.is_file():
        return [], ["falta sources.jsonl"]
    sources: list[SourceRecord] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            sources.append(SourceRecord.model_validate_json(line))
        except ValidationError:
            errors.append(f"sources.jsonl inválido en línea {line_number}")
    return sources, errors


def _read_reviews(folder: Path) -> tuple[list[ReviewDecision], list[str]]:
    path = folder / "review-decisions.jsonl"
    if not path.is_file():
        return [], ["falta review-decisions.jsonl"]
    reviews: list[ReviewDecision] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            reviews.append(ReviewDecision.model_validate_json(line))
        except ValidationError:
            errors.append(f"review-decisions.jsonl inválido en línea {line_number}")
    return reviews, errors


def _read_candidate_diff(folder: Path) -> tuple[dict[str, object] | None, list[str]]:
    path = folder / CANDIDATE_DIFF_NAME
    if not path.is_file():
        return None, [f"falta {CANDIDATE_DIFF_NAME}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, [f"{CANDIDATE_DIFF_NAME} no es JSON válido"]
    if not isinstance(payload, dict):
        return None, [f"{CANDIDATE_DIFF_NAME} debe ser un objeto"]
    return payload, []


def _claim_ids(value: object, field: str) -> tuple[list[str], list[str]]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return [], [f"{field} inválido en {CANDIDATE_DIFF_NAME}"]
    if len(value) != len(set(value)):
        return [], [f"{field} contiene IDs duplicados"]
    return sorted(value), []


def validate_staging(folder: Path, claims: list[ClaimRecord] | None = None) -> list[str]:
    errors: list[str] = []
    manifest_path = folder / MANIFEST_NAME
    if not manifest_path.is_file():
        return ["falta manifest.json"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["manifest.json no es JSON válido"]
    if not isinstance(manifest, dict):
        return ["manifest.json debe ser un objeto"]
    if not manifest.get("candidate_id"):
        errors.append("manifest sin candidate_id")
    expected_files = manifest.get("file_hashes")
    if not isinstance(expected_files, dict):
        return [*errors, "manifest sin file_hashes"]
    actual_files = _candidate_files(folder)
    expected_names = set(expected_files)
    for relative in sorted(expected_names | actual_files):
        if relative not in expected_names:
            errors.append(f"archivo sin hash: {relative}")
            continue
        if relative not in actual_files:
            errors.append(f"falta {relative}")
            continue
        path = _safe_file(folder, relative)
        expected = expected_files.get(relative)
        if path is None or not isinstance(expected, str) or len(expected) != 64:
            errors.append(f"ruta o hash inválido: {relative}")
            continue
        actual = _hash_text_file(path)
        if actual != expected:
            errors.append(f"hash alterado: {relative}")
        hits = find_sensitive_hits(path.read_text(encoding="utf-8"))
        if hits:
            errors.append(f"contenido sensible en {relative}: {', '.join(hits)}")
    package_claims, claim_errors = _read_claims(folder)
    sources, source_errors = _read_sources(folder)
    package_reviews, review_errors = _read_reviews(folder)
    candidate_diff, diff_errors = _read_candidate_diff(folder)
    errors.extend(claim_errors)
    errors.extend(source_errors)
    errors.extend(review_errors)
    errors.extend(diff_errors)
    ledger_claims = package_claims if claims is None else claims
    expected_claims = _release_claims(sources, ledger_claims, package_reviews)
    expected_by_id = {claim.claim_id: claim for claim in expected_claims}
    package_by_id = {claim.claim_id: claim for claim in package_claims}
    if package_by_id != expected_by_id:
        errors.append("claims.jsonl no coincide con la proyección publicable")
    if len(package_by_id) != len(package_claims):
        errors.append("claims.jsonl contiene claim_id duplicado")

    review_ids = [review.decision_id for review in package_reviews]
    if len(review_ids) != len(set(review_ids)):
        errors.append("review-decisions.jsonl contiene decision_id duplicado")
    for review in package_reviews:
        claim = package_by_id.get(review.object_id)
        if claim is None:
            errors.append(f"review de claim no incluido: {review.decision_id}")
        elif not _is_exact_claim_approval(review, claim):
            errors.append(f"review stale o no aprobada: {review.decision_id}")
    for claim in package_claims:
        if not any(_is_exact_claim_approval(review, claim) for review in package_reviews):
            errors.append(f"claim sin aprobación exacta: {claim.claim_id}")

    source_by_id = {source.source_id: source for source in sources}
    for source in sources:
        if not has_valid_content_hash(source):
            errors.append(f"content_hash de fuente inválido: {source.source_id}")
    for claim in package_claims:
        if claim.status not in PUBLISHED_CLAIM_STATUSES:
            errors.append(f"claim no aprobado en claims.jsonl: {claim.claim_id}")
        if not has_valid_content_hash(claim):
            errors.append(f"content_hash de claim inválido: {claim.claim_id}")
        gate_errors = claim_passes_technical_gate(claim)
        if gate_errors:
            errors.append(f"claim no pasa gate: {claim.claim_id}")
        for link in claim.evidence:
            source = source_by_id.get(link.source_id)
            if source is None or not source.redistribution_allowed:
                errors.append(f"evidencia no redistribuible en claim: {claim.claim_id}")
            if not has_valid_content_hash(link):
                errors.append(f"content_hash de evidencia inválido: {claim.claim_id}")

    included_ids = sorted(package_by_id)
    excluded_ids = sorted(
        claim.claim_id for claim in ledger_claims if claim.claim_id not in package_by_id
    )
    if candidate_diff is not None:
        diff_included, included_errors = _claim_ids(
            candidate_diff.get("included_claim_ids"), "included_claim_ids"
        )
        diff_excluded, excluded_errors = _claim_ids(
            candidate_diff.get("excluded_claim_ids"), "excluded_claim_ids"
        )
        errors.extend(included_errors)
        errors.extend(excluded_errors)
        if diff_included != included_ids:
            errors.append("included_claim_ids no coincide con claims.jsonl")
        if claims is not None and diff_excluded != excluded_ids:
            errors.append("excluded_claim_ids no coincide con el ledger de la corrida")
        if set(diff_included) & set(diff_excluded):
            errors.append("included_claim_ids y excluded_claim_ids se traslapan")

    approved = set(included_ids)
    knowledge_dir = folder / "knowledge"
    knowledge_text = ""
    if knowledge_dir.is_dir():
        knowledge_text = "\n".join(
            path.read_text(encoding="utf-8") for path in knowledge_dir.glob("*.md")
        )
    for claim in ledger_claims:
        if claim.claim_id not in approved and claim.canonical_text in knowledge_text:
            errors.append(f"afirmación no aprobada en el conocimiento: {claim.claim_id}")
        if claim.claim_id in approved and not claim.evidence:
            errors.append(f"afirmación aprobada sin evidencia: {claim.claim_id}")
        if claim.claim_id in approved and not any(
            link.locator.startswith("L") for link in claim.evidence
        ):
            errors.append(f"afirmación aprobada sin localizador: {claim.claim_id}")
    return errors


def _matching_candidate_approval(
    reviews: list[ReviewDecision], candidate_id: str, candidate_hash: str
) -> ReviewDecision | None:
    for review in reviews:
        if (
            review.object_type == "release_candidate"
            and review.object_id == candidate_id
            and review.decision == ReviewVerdict.APPROVED
            and review.approved_hash == candidate_hash
            and has_valid_content_hash(review)
        ):
            return review
    return None


def make_release(
    release_id: str,
    *,
    domain: str,
    as_of: date,
    folder: Path,
    claims: list[ClaimRecord],
    reviews: list[ReviewDecision],
    metrics: dict[str, float | int | None],
    model_versions: dict[str, str],
    rollback_of: str | None = None,
) -> KnowledgeRelease:
    manifest_path = folder / MANIFEST_NAME
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    candidate_id = manifest.get("candidate_id", "")
    candidate_hash = sha256_text(manifest_text)
    approval = _matching_candidate_approval(reviews, candidate_id, candidate_hash)
    if approval is None:
        raise ReleaseError("Falta aprobación exacta del candidato")
    atomic_write(folder / CANDIDATE_APPROVAL_NAME, _dump(approval))

    package_claims, claim_errors = _read_claims(folder)
    package_reviews, review_errors = _read_reviews(folder)
    candidate_diff, diff_errors = _read_candidate_diff(folder)
    if claim_errors or review_errors or diff_errors or candidate_diff is None:
        raise ReleaseError("; ".join([*claim_errors, *review_errors, *diff_errors]))
    included, included_errors = _claim_ids(
        candidate_diff.get("included_claim_ids"), "included_claim_ids"
    )
    excluded, excluded_errors = _claim_ids(
        candidate_diff.get("excluded_claim_ids"), "excluded_claim_ids"
    )
    if included_errors or excluded_errors:
        raise ReleaseError("; ".join([*included_errors, *excluded_errors]))
    if included != sorted(claim.claim_id for claim in package_claims):
        raise ReleaseError("included_claim_ids no coincide con claims.jsonl")
    if set(included) & set(excluded):
        raise ReleaseError("included_claim_ids y excluded_claim_ids se traslapan")
    if set(included) | set(excluded) != {claim.claim_id for claim in claims}:
        raise ReleaseError("el diff no conserva todos los claim_id de la corrida")
    approval_ids = sorted(
        {approval.decision_id, *(review.decision_id for review in package_reviews)}
    )
    package_hashes = {
        relative: _hash_text_file(folder / Path(*PurePosixPath(relative).parts))
        for relative in sorted(_package_files(folder))
    }
    release = with_content_hash(
        KnowledgeRelease(
            release_id=release_id,
            domain=domain,
            as_of=as_of,
            file_hashes=package_hashes,
            included_claim_ids=included,
            excluded_claim_ids=excluded,
            approval_ids=approval_ids,
            metrics=metrics,
            model_versions=model_versions,
            rollback_of=rollback_of,
            manifest_hash=candidate_hash,
            content_hash="0" * 64,
        )
    )
    atomic_write(folder / KNOWLEDGE_RELEASE_NAME, _dump(release))
    return release


def validate_release_package(folder: Path) -> tuple[KnowledgeRelease | None, list[str]]:
    errors: list[str] = []
    release_path = folder / KNOWLEDGE_RELEASE_NAME
    if not release_path.is_file():
        return None, [f"falta {KNOWLEDGE_RELEASE_NAME}"]
    try:
        release = KnowledgeRelease.model_validate_json(release_path.read_text(encoding="utf-8"))
    except ValidationError:
        return None, ["KnowledgeRelease inválido"]
    if not has_valid_content_hash(release):
        errors.append("content_hash de KnowledgeRelease inválido")

    manifest_path = folder / MANIFEST_NAME
    if not manifest_path.is_file():
        return release, [*errors, "falta manifest.json"]
    manifest_text = manifest_path.read_text(encoding="utf-8")
    actual_manifest_hash = sha256_text(manifest_text)
    if actual_manifest_hash != release.manifest_hash:
        errors.append("hash del manifest no coincide con KnowledgeRelease")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return release, [*errors, "manifest.json no es JSON válido"]

    expected_files = set(release.file_hashes)
    actual_files = _package_files(folder)
    for relative in sorted(expected_files | actual_files):
        if relative not in expected_files:
            errors.append(f"archivo final sin hash: {relative}")
            continue
        if relative not in actual_files:
            errors.append(f"falta {relative}")
            continue
        path = _safe_file(folder, relative)
        expected = release.file_hashes.get(relative)
        if path is None or not isinstance(expected, str) or len(expected) != 64:
            errors.append(f"ruta o hash final inválido: {relative}")
            continue
        if _hash_text_file(path) != expected:
            errors.append(f"hash alterado: {relative}")

    claims, claim_errors = _read_claims(folder)
    claim_reviews, review_errors = _read_reviews(folder)
    candidate_diff, diff_errors = _read_candidate_diff(folder)
    errors.extend(claim_errors)
    errors.extend(review_errors)
    errors.extend(diff_errors)
    errors.extend(validate_staging(folder))
    expected_included = sorted(claim.claim_id for claim in claims)
    expected_excluded: list[str] = []
    if candidate_diff is not None:
        expected_included, included_errors = _claim_ids(
            candidate_diff.get("included_claim_ids"), "included_claim_ids"
        )
        expected_excluded, excluded_errors = _claim_ids(
            candidate_diff.get("excluded_claim_ids"), "excluded_claim_ids"
        )
        errors.extend(included_errors)
        errors.extend(excluded_errors)
    if sorted(release.included_claim_ids) != expected_included:
        errors.append("included_claim_ids no coincide con claims.jsonl")
    if sorted(release.excluded_claim_ids) != expected_excluded:
        errors.append("excluded_claim_ids no coincide con claims.jsonl")
    if manifest.get("domain") != release.domain:
        errors.append("dominio del manifest no coincide con KnowledgeRelease")
    if manifest.get("as_of") != release.as_of.isoformat():
        errors.append("as_of del manifest no coincide con KnowledgeRelease")

    expected_approval_ids = {review.decision_id for review in claim_reviews}
    approval_path = folder / CANDIDATE_APPROVAL_NAME
    if not approval_path.is_file():
        errors.append(f"falta {CANDIDATE_APPROVAL_NAME}")
    else:
        try:
            approval = ReviewDecision.model_validate_json(approval_path.read_text(encoding="utf-8"))
        except ValidationError:
            errors.append("aprobación del candidato inválida")
        else:
            expected_approval_ids.add(approval.decision_id)
            if not has_valid_content_hash(approval):
                errors.append("content_hash de aprobación inválido")
            if approval.object_type != "release_candidate":
                errors.append("la aprobación no corresponde a release_candidate")
            if approval.object_id != manifest.get("candidate_id"):
                errors.append("candidate_id aprobado no coincide con el manifest")
            if approval.decision != ReviewVerdict.APPROVED:
                errors.append("el candidato no fue aprobado")
            if approval.approved_hash != actual_manifest_hash:
                errors.append("el hash aprobado no coincide con el manifest")
            if approval.decision_id not in release.approval_ids:
                errors.append("KnowledgeRelease no referencia la aprobación del candidato")
    if sorted(release.approval_ids) != sorted(expected_approval_ids):
        errors.append("approval_ids no coincide con las aprobaciones empaquetadas")
    return release, errors


def publish(staging_folder: Path, releases_dir: Path, release: KnowledgeRelease) -> Path:
    validated, errors = validate_release_package(staging_folder)
    if errors or validated is None:
        raise ReleaseError("; ".join(errors or ["KnowledgeRelease ausente"]))
    if validated != release:
        raise ReleaseError("KnowledgeRelease escrito no coincide con el objeto publicado")
    releases_dir.mkdir(parents=True, exist_ok=True)
    destination = releases_dir / release.release_id
    if destination.exists():
        raise ReleaseError("El release_id ya existe y es inmutable")
    try:
        staging_folder.replace(destination)
    except PermissionError:
        shutil.copytree(staging_folder, destination)
        shutil.rmtree(staging_folder, ignore_errors=True)
    pointer = {
        "release_id": release.release_id,
        "path": destination.name,
        "manifest_hash": release.manifest_hash,
        "release_hash": _hash_text_file(destination / KNOWLEDGE_RELEASE_NAME),
    }
    atomic_write(releases_dir / "current.json", _dump(pointer))
    return destination


def read_current(releases_dir: Path) -> dict[str, str] | None:
    path = releases_dir / "current.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def rollback(releases_dir: Path, release_id: str) -> None:
    target = releases_dir / release_id
    if not target.is_dir():
        raise ReleaseError("No existe el release de rollback")
    release, errors = validate_release_package(target)
    if release is None or errors:
        raise ReleaseError("Release de rollback inválido: " + "; ".join(errors))
    manifest = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
    pointer = {
        "release_id": release_id,
        "path": target.name,
        "manifest_hash": release.manifest_hash,
        "release_hash": _hash_text_file(target / KNOWLEDGE_RELEASE_NAME),
        "rolled_back_via": manifest.get("run_id"),
    }
    atomic_write(releases_dir / "current.json", _dump(pointer))

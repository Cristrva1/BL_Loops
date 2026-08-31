"""Staging, validación, publicación atómica y rollback del puntero current.json."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from sales_curator.contracts.models import (
    ClaimRecord,
    ClaimStatus,
    ConflictRecord,
    KnowledgeDraft,
    KnowledgeRelease,
    ReviewDecision,
    SourceRecord,
)
from sales_curator.domain.threats import find_sensitive_hits
from sales_curator.hashing import sha256_text, with_content_hash

MANIFEST_NAME = "manifest.json"


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


def build_staging(
    staging_root: Path,
    run_id: str,
    *,
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
    files: dict[str, str] = {
        "sources.jsonl": _jsonl(sources),
        "claims.jsonl": _jsonl(claims),
        "conflicts.jsonl": _jsonl(conflicts),
        "review-decisions.jsonl": _jsonl(reviews),
        "evaluation.json": _dump(metrics),
        "CHANGELOG.md": (
            f"# Changelog\n\n- Candidato de la corrida `{run_id}` al {as_of.isoformat()}.\n"
            "- Afirmaciones aprobadas: "
            f"{sum(1 for c in claims if c.status == ClaimStatus.HUMAN_APPROVED)}.\n"
        ),
        "knowledge/README.md": (
            "# Paquete de conocimiento\n\n"
            "Documentos redactados a partir del ledger. No reproducen la fuente completa.\n"
        ),
    }
    for draft in drafts:
        files[f"knowledge/{draft.topic}.md"] = draft.markdown
    hashes: dict[str, str] = {}
    for relative, content in files.items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        hashes[relative] = sha256_text(content)
    manifest = {
        "run_id": run_id,
        "domain": domain,
        "as_of": as_of.isoformat(),
        "file_hashes": hashes,
        "model_versions": model_versions,
    }
    atomic_write(folder / MANIFEST_NAME, _dump(manifest))
    hashes[MANIFEST_NAME] = sha256_text(_dump(manifest))
    (folder / MANIFEST_NAME).write_text(
        _dump({**manifest, "file_hashes": hashes}),
        encoding="utf-8",
        newline="\n",
    )
    return folder


def validate_staging(folder: Path, claims: list[ClaimRecord]) -> list[str]:
    errors: list[str] = []
    manifest_path = folder / MANIFEST_NAME
    if not manifest_path.is_file():
        return ["falta manifest.json"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, expected in manifest.get("file_hashes", {}).items():
        if relative == MANIFEST_NAME:
            continue
        path = folder / relative
        if not path.is_file():
            errors.append(f"falta {relative}")
            continue
        actual = sha256_text(path.read_text(encoding="utf-8"))
        if actual != expected:
            errors.append(f"hash alterado: {relative}")
        hits = find_sensitive_hits(path.read_text(encoding="utf-8"))
        if hits:
            errors.append(f"contenido sensible en {relative}: {', '.join(hits)}")
    approved = {
        claim.claim_id
        for claim in claims
        if claim.status in {ClaimStatus.HUMAN_APPROVED, ClaimStatus.PUBLISHED}
    }
    knowledge_dir = folder / "knowledge"
    knowledge_text = ""
    if knowledge_dir.is_dir():
        knowledge_text = "\n".join(
            path.read_text(encoding="utf-8") for path in knowledge_dir.glob("*.md")
        )
    for claim in claims:
        if claim.claim_id not in approved and claim.canonical_text in knowledge_text:
            errors.append(f"afirmación no aprobada en el conocimiento: {claim.claim_id}")
        if claim.claim_id in approved and not claim.evidence:
            errors.append(f"afirmación aprobada sin evidencia: {claim.claim_id}")
        if claim.claim_id in approved and not any(
            link.locator.startswith("L") for link in claim.evidence
        ):
            errors.append(f"afirmación aprobada sin localizador: {claim.claim_id}")
    return errors


def publish(
    staging_folder: Path,
    releases_dir: Path,
    release: KnowledgeRelease,
) -> Path:
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
    manifest = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
    pointer = {
        "release_id": release_id,
        "path": target.name,
        "manifest_hash": sha256_text((target / MANIFEST_NAME).read_text(encoding="utf-8")),
        "rolled_back_via": manifest.get("run_id"),
    }
    atomic_write(releases_dir / "current.json", _dump(pointer))


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
    manifest_text = (folder / MANIFEST_NAME).read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    included = [c.claim_id for c in claims if c.status == ClaimStatus.HUMAN_APPROVED]
    excluded = [c.claim_id for c in claims if c.claim_id not in included]
    approval_ids = [item.decision_id for item in reviews if item.decision.value == "approved"]
    if not approval_ids:
        raise ReleaseError("No hay decisión humana de aprobación")
    return with_content_hash(
        KnowledgeRelease(
            release_id=release_id,
            domain=domain,
            as_of=as_of,
            file_hashes=manifest.get("file_hashes", {}),
            included_claim_ids=included,
            excluded_claim_ids=excluded,
            approval_ids=approval_ids,
            metrics=metrics,
            model_versions=model_versions,
            rollback_of=rollback_of,
            manifest_hash=sha256_text(manifest_text),
            content_hash="0" * 64,
        )
    )

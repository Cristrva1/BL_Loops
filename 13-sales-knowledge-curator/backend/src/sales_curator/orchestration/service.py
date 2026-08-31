"""Orquestador visible: permisos, presupuesto, transiciones y publicación."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import uuid4

from sales_curator.agents.roles import assert_role_may
from sales_curator.config import Settings, lab_root
from sales_curator.connectors.network import NetworkDisabled, fetch_url
from sales_curator.contracts.models import (
    ClaimRecord,
    ClaimStatus,
    ConflictRecord,
    GapRecord,
    QuarantineStatus,
    ResearchFinding,
    ResearchTask,
    ReviewDecision,
    ReviewVerdict,
    RunEvent,
    SourceRecord,
    TaskStatus,
    WorkflowState,
    WorkflowStatus,
)
from sales_curator.domain.editor import drafts_from_claims
from sales_curator.domain.extract import extract_from_source
from sales_curator.domain.gaps import plan_from_inventory
from sales_curator.domain.ingest import ingest_directory
from sales_curator.domain.policy import DEMO_DOMAIN
from sales_curator.domain.verify import (
    adversarial_scan,
    apply_conflicts,
    build_claim,
    detect_conflicts,
    merge_duplicates,
    note_missing_challenge,
    supersede_outdated,
)
from sales_curator.evaluation.gate import (
    candidate_approval,
    claim_identity_hash,
    claim_passes_technical_gate,
    matching_approval,
)
from sales_curator.evaluation.jsonl import to_jsonl_event, validate_run, write_run_jsonl
from sales_curator.evaluation.metrics import compute_metrics
from sales_curator.hashing import sha256_text, with_content_hash
from sales_curator.orchestration.machine import (
    NODE_FOR_STATE,
    ensure_transition,
)
from sales_curator.storage.releases import (
    ReleaseError,
    build_staging,
    make_release,
    publish,
    read_current,
    rollback,
    validate_staging,
)
from sales_curator.storage.sqlite import CuratorStore


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class RunSnapshot:
    workflow: WorkflowState
    sources: list[SourceRecord]
    claims: list[ClaimRecord]
    conflicts: list[ConflictRecord]
    gaps: list[GapRecord]
    tasks: list[ResearchTask]
    reviews: list[ReviewDecision]
    events: list[RunEvent]
    findings: list
    metrics: dict[str, float | int | None]
    release_id: str | None = None
    candidate_id: str | None = None
    candidate_hash: str | None = None
    jsonl_path: str | None = None
    stop_reason: str | None = None


class CuratorService:
    def __init__(self, settings: Settings, store: CuratorStore | None = None) -> None:
        self.settings = settings
        self.store = store or CuratorStore(settings.sqlite_path)
        self.root = lab_root()

    def close(self) -> None:
        self.store.close()

    def _clock(self) -> datetime:
        return datetime.now(UTC)

    def _load_models(self, run_id: str) -> RunSnapshot:
        run = self.store.get_run(run_id)
        if run is None:
            raise KeyError(f"No existe la corrida {run_id}")
        workflow = WorkflowState.model_validate(run["workflow"])
        return RunSnapshot(
            workflow=workflow,
            sources=[SourceRecord.model_validate(item) for item in self.store.list_sources(run_id)],
            claims=[ClaimRecord.model_validate(item) for item in self.store.list_claims(run_id)],
            conflicts=[
                ConflictRecord.model_validate(item) for item in self.store.list_conflicts(run_id)
            ],
            gaps=[GapRecord.model_validate(item) for item in self.store.list_gaps(run_id)],
            tasks=[ResearchTask.model_validate(item) for item in self.store.list_tasks(run_id)],
            reviews=[
                ReviewDecision.model_validate(item) for item in self.store.list_reviews(run_id)
            ],
            events=[
                RunEvent.model_validate({k: v for k, v in item.items() if k != "export_event_type"})
                for item in self.store.list_events(run_id)
            ],
            findings=self.store.list_findings(run_id),
            metrics=run.get("metrics") or {},
            release_id=run.get("release_id"),
            candidate_id=run.get("candidate_id"),
            candidate_hash=run.get("candidate_hash"),
            jsonl_path=run.get("jsonl_path"),
            stop_reason=workflow.stop_reason,
        )

    def get_run(self, run_id: str) -> RunSnapshot:
        return self._load_models(run_id)

    def _persist_run(self, snapshot: RunSnapshot, extra: dict | None = None) -> None:
        payload = {
            "run_id": snapshot.workflow.run_id,
            "workflow": snapshot.workflow.model_dump(mode="json"),
            "metrics": snapshot.metrics,
            "release_id": snapshot.release_id,
            "candidate_id": snapshot.candidate_id,
            "candidate_hash": snapshot.candidate_hash,
            "jsonl_path": snapshot.jsonl_path,
        }
        if extra:
            payload.update(extra)
        self.store.save_run(payload)

    def _emit(
        self,
        snapshot: RunSnapshot,
        *,
        event_type: str,
        result: dict,
        error: str | None = None,
        tool: str | None = None,
        latency_ms: float = 0,
    ) -> RunEvent:
        sequence = len(snapshot.events) + 1
        event = RunEvent(
            run_id=snapshot.workflow.run_id,
            sequence=sequence,
            event_id=_id("evt"),
            occurred_at=self._clock(),
            node_id=NODE_FOR_STATE[snapshot.workflow.state],
            state=snapshot.workflow.state,
            tool=tool,
            result_sanitized=result,
            error=error,
            tokens=None,
            latency_ms=latency_ms,
            ram_mb=None,
            vram_mb=None,
            refs=[],
        )
        snapshot.events.append(event)
        self.store.append_event(
            snapshot.workflow.run_id,
            sequence,
            {**event.model_dump(mode="json"), "export_event_type": event_type},
        )
        return event

    def _transition(
        self,
        snapshot: RunSnapshot,
        nxt: WorkflowStatus,
        actor: str,
        reason: str,
        *,
        stop_reason: str | None = None,
    ) -> None:
        assert_role_may("orchestrator", "transition")
        ensure_transition(snapshot.workflow.state, nxt)
        previous = snapshot.workflow.state
        snapshot.workflow = with_content_hash(
            snapshot.workflow.model_copy(
                update={
                    "previous_state": previous,
                    "state": nxt,
                    "actor": actor,
                    "reason": reason,
                    "changed_at": self._clock(),
                    "stop_reason": stop_reason,
                    "network_enabled": self.settings.network_enabled,
                    "content_hash": "0" * 64,
                }
            )
        )
        self._persist_run(snapshot)
        self._emit(
            snapshot,
            event_type="state.changed",
            result={
                "from": previous.value,
                "to": nxt.value,
                "actor": actor,
                "reason": reason,
            },
        )

    def start_audit(
        self,
        source_dir: Path,
        *,
        as_of: date | None = None,
        dry_run: bool = False,
        extractor: str = "deterministic",
    ) -> RunSnapshot:
        if dry_run:
            isolated = self.settings.with_isolated_dirs(
                (self.root / ".local" / "dry-run" / _id("dry")),
                (self.root / ".local" / "dry-run" / _id("dryruns")),
            )
            service = CuratorService(isolated)
            snapshot = service.start_audit(source_dir, as_of=as_of, extractor=extractor)
            service.close()
            return snapshot

        as_of = as_of or date(2026, 8, 30)
        run_id = _id("run")
        workflow = with_content_hash(
            WorkflowState(
                run_id=run_id,
                state=WorkflowStatus.SCOPE_DRAFT,
                previous_state=None,
                actor="orchestrator",
                reason="corrida de auditoría local",
                changed_at=self._clock(),
                stop_reason=None,
                research_round=0,
                claim_revision=0,
                network_enabled=self.settings.network_enabled,
                urls_used=0,
                content_hash="0" * 64,
            )
        )
        snapshot = RunSnapshot(
            workflow=workflow,
            sources=[],
            claims=[],
            conflicts=[],
            gaps=[],
            tasks=[],
            reviews=[],
            events=[],
            findings=[],
            metrics={},
        )
        self._persist_run(snapshot)
        self._emit(
            snapshot,
            event_type="run.started",
            result={
                "source_dir": source_dir.name,
                "as_of": as_of.isoformat(),
                "extractor": extractor,
            },
        )
        try:
            self._run_pipeline(snapshot, source_dir, as_of, extractor)
            self._flush_jsonl(snapshot)
        except Exception as exc:
            if snapshot.workflow.state != WorkflowStatus.FAILED:
                try:
                    self._transition(
                        snapshot, WorkflowStatus.FAILED, "orchestrator", str(exc)[:300]
                    )
                except Exception:
                    snapshot.workflow = with_content_hash(
                        snapshot.workflow.model_copy(
                            update={
                                "state": WorkflowStatus.FAILED,
                                "stop_reason": str(exc)[:300],
                                "content_hash": "0" * 64,
                            }
                        )
                    )
            self._emit(snapshot, event_type="run.failed", result={}, error=str(exc)[:300])
            self._flush_jsonl(snapshot)
            raise
        return snapshot

    def _run_pipeline(
        self,
        snapshot: RunSnapshot,
        source_dir: Path,
        as_of: date,
        extractor: str,
    ) -> None:
        self._transition(
            snapshot, WorkflowStatus.INVENTORY_RUNNING, "source_auditor", "inventario local"
        )
        ingested = ingest_directory(
            source_dir,
            allowed_root=self.root,
            max_bytes=self.settings.max_bytes_per_source,
            retrieved_at=self._clock(),
        )
        snapshot.sources = [item.source for item in ingested]
        for item in ingested:
            self.store.save_source(snapshot.workflow.run_id, item.source.model_dump(mode="json"))
            self.store.save_artifact(
                snapshot.workflow.run_id, item.artifact.model_dump(mode="json")
            )
            self.store.save_document(
                snapshot.workflow.run_id,
                item.source.source_id,
                item.full_text,
                item.body_start_line,
            )
        self._emit(
            snapshot,
            event_type="inventory.completed",
            tool="source_auditor",
            result={
                "sources": len(snapshot.sources),
                "quarantined": sum(
                    1
                    for item in snapshot.sources
                    if item.quarantine_status != QuarantineStatus.CLEAR
                ),
                "syndicated": sum(
                    1 for item in snapshot.sources if item.independence.value == "syndicated"
                ),
            },
        )

        self._transition(
            snapshot, WorkflowStatus.GAPS_READY, "gap_planner", "cobertura del inventario"
        )
        gaps, tasks = plan_from_inventory(snapshot.sources)
        snapshot.gaps = gaps
        snapshot.tasks = tasks
        for gap in gaps:
            self.store.save_gap(snapshot.workflow.run_id, gap.model_dump(mode="json"))
        for task in tasks:
            self.store.save_task(snapshot.workflow.run_id, task.model_dump(mode="json"))
        self._emit(
            snapshot,
            event_type="gaps.ready",
            tool="gap_planner",
            result={"gaps": [gap.topic for gap in gaps], "tasks": len(tasks)},
        )

        self._transition(
            snapshot, WorkflowStatus.RESEARCH_PLANNED, "gap_planner", "plan de investigación"
        )
        web_tasks = [
            task for task in tasks if task.budget_urls > 0 or "primary" in task.target_kinds
        ]
        local_only = not web_tasks
        if web_tasks and not self.settings.network_enabled:
            self._transition(
                snapshot,
                WorkflowStatus.AWAITING_EXTERNAL_AUTHORIZATION,
                "researcher",
                "hay preguntas que exigirían red; quedan bloqueadas",
            )
            updated_tasks: list[ResearchTask] = []
            for task in snapshot.tasks:
                if "primary" in task.target_kinds:
                    blocked = with_content_hash(
                        task.model_copy(
                            update={"status": TaskStatus.BLOCKED_NETWORK, "content_hash": "0" * 64}
                        )
                    )
                    updated_tasks.append(blocked)
                    self.store.save_task(snapshot.workflow.run_id, blocked.model_dump(mode="json"))
                    finding = with_content_hash(
                        ResearchFinding(
                            finding_id=_id("fnd"),
                            task_id=task.task_id,
                            source_id=None,
                            summary="Rama incompleta: red desactivada",
                            failed=True,
                            failure_reason="NETWORK_ENABLED=false",
                            content_hash="0" * 64,
                        )
                    )
                    self.store.save_finding(
                        snapshot.workflow.run_id, finding.model_dump(mode="json")
                    )
                    snapshot.findings.append(finding.model_dump(mode="json"))
                else:
                    updated_tasks.append(task)
            snapshot.tasks = updated_tasks
            self._emit(
                snapshot,
                event_type="research.blocked",
                tool="researcher",
                result={
                    "blocked_tasks": sum(
                        1 for t in snapshot.tasks if t.status == TaskStatus.BLOCKED_NETWORK
                    )
                },
                error="NETWORK_ENABLED=false",
            )
            with contextlib.suppress(NetworkDisabled):
                fetch_url(
                    "https://example.invalid",
                    network_enabled=self.settings.network_enabled,
                    allowed_domains=self.settings.allowed_domain_list,
                    max_urls_remaining=self.settings.max_urls_per_run,
                )
            self._transition(
                snapshot,
                WorkflowStatus.COLLECTING_LOCAL,
                "researcher",
                "continúa con evidencias locales; las ramas web quedan inconclusas",
            )
        elif local_only:
            self._transition(
                snapshot, WorkflowStatus.COLLECTING_LOCAL, "researcher", "solo corpus local"
            )
        else:
            self._transition(
                snapshot, WorkflowStatus.COLLECTING_LOCAL, "researcher", "recolección local"
            )

        collected = [
            with_content_hash(
                task.model_copy(
                    update={"status": TaskStatus.COLLECTED_LOCAL, "content_hash": "0" * 64}
                )
            )
            if task.status == TaskStatus.PLANNED
            else task
            for task in snapshot.tasks
        ]
        snapshot.tasks = collected
        for task in collected:
            self.store.save_task(snapshot.workflow.run_id, task.model_dump(mode="json"))

        self._transition(
            snapshot, WorkflowStatus.SOURCES_NORMALIZED, "source_auditor", "cadenas de origen"
        )
        self._transition(
            snapshot,
            WorkflowStatus.CLAIMS_EXTRACTED,
            "claim_extractor",
            f"extractor {extractor}",
        )
        if extractor == "ollama":
            raise RuntimeError("El extractor Ollama es opcional y se invoca por contrato aparte")
        claims: list[ClaimRecord] = []
        sources_by_id = {item.source.source_id: item.source for item in ingested}
        for item in ingested:
            for candidate in extract_from_source(item):
                claims.append(build_claim(candidate, item.source, item, as_of, clock=self._clock()))
        claims = merge_duplicates(claims, sources_by_id)
        snapshot.claims = claims
        self._emit(
            snapshot,
            event_type="claims.extracted",
            tool="claim_extractor",
            result={"claims": len(claims)},
        )

        self._transition(
            snapshot,
            WorkflowStatus.VERIFICATION_RUNNING,
            "claim_verifier",
            "citas, fechas y duplicados",
        )
        conflicts = detect_conflicts(claims)
        claims = apply_conflicts(claims, conflicts)
        claims = supersede_outdated(claims)
        claims = note_missing_challenge(claims, {item.topic for item in conflicts})
        findings = adversarial_scan(snapshot.sources, claims, ingested)
        snapshot.claims = claims
        snapshot.conflicts = conflicts
        for claim in claims:
            self.store.save_claim(snapshot.workflow.run_id, claim.model_dump(mode="json"))
        for conflict in conflicts:
            self.store.save_conflict(snapshot.workflow.run_id, conflict.model_dump(mode="json"))
        for finding in findings:
            self.store.save_finding(snapshot.workflow.run_id, finding.model_dump(mode="json"))
        snapshot.findings.extend(item.model_dump(mode="json") for item in findings)
        snapshot.metrics = compute_metrics(
            snapshot.sources, claims, conflicts, snapshot.gaps, findings
        )
        self._persist_run(snapshot)
        self._emit(
            snapshot,
            event_type="verification.completed",
            tool="claim_verifier",
            result={
                "conflicts": len(conflicts),
                "findings": len(findings),
                "disputed": sum(1 for item in claims if item.status == ClaimStatus.DISPUTED),
            },
        )
        if conflicts:
            self._transition(
                snapshot,
                WorkflowStatus.CONFLICTS_OPEN,
                "claim_verifier",
                "contradicciones materiales",
            )
            self._transition(
                snapshot, WorkflowStatus.REVIEW_PENDING, "orchestrator", "requiere revisión humana"
            )
        else:
            self._transition(
                snapshot, WorkflowStatus.REVIEW_PENDING, "orchestrator", "sin conflictos materiales"
            )

    def _flush_jsonl(self, snapshot: RunSnapshot, terminal: str | None = None) -> Path:
        rows = []
        stored = self.store.list_events(snapshot.workflow.run_id)
        for index, raw in enumerate(stored):
            event = RunEvent.model_validate(
                {k: v for k, v in raw.items() if k != "export_event_type"}
            )
            event_type = raw.get("export_event_type", "node.updated")
            if index == 0:
                event_type = "run.started"
            rows.append(
                to_jsonl_event(
                    event,
                    event_type=event_type,
                    model_ref=self.settings.curator_model,
                )
            )
        if terminal:
            last = snapshot.events[-1]
            rows.append(
                to_jsonl_event(
                    last.model_copy(update={"sequence": last.sequence + 1, "event_id": _id("evt")}),
                    event_type=terminal,
                    model_ref=self.settings.curator_model,
                )
            )
        path = self.settings.runs_path / f"{snapshot.workflow.run_id}.jsonl"
        write_run_jsonl(path, rows)
        snapshot.jsonl_path = path.relative_to(self.root).as_posix()
        self._persist_run(snapshot)
        return path

    def list_claims(self, run_id: str, status: str | None = None) -> list[ClaimRecord]:
        claims = self.get_run(run_id).claims
        if status:
            return [item for item in claims if item.status.value == status]
        return claims

    def submit_review(
        self,
        run_id: str,
        *,
        object_type: str,
        object_id: str,
        decision: str,
        reviewer: str,
        reason: str,
        expected_hash: str,
    ) -> ReviewDecision:
        snapshot = self.get_run(run_id)
        if object_type == "claim":
            claim = next(item for item in snapshot.claims if item.claim_id == object_id)
            actual = claim_identity_hash(claim)
        elif object_type == "release_candidate":
            actual = snapshot.candidate_hash or ""
        else:
            raise ValueError("object_type no soportado")
        if actual != expected_hash:
            raise ValueError("El hash aprobado no coincide con el candidato actual")
        review = with_content_hash(
            ReviewDecision(
                decision_id=_id("rev"),
                object_type=object_type,  # type: ignore[arg-type]
                object_id=object_id,
                decision=ReviewVerdict(decision),
                reviewer=reviewer,
                reason=reason,
                decided_at=self._clock(),
                conditions=[],
                approved_hash=expected_hash,
                content_hash="0" * 64,
            )
        )
        self.store.save_review(run_id, review.model_dump(mode="json"))
        if object_type == "claim" and review.decision == ReviewVerdict.APPROVED:
            errors = claim_passes_technical_gate(claim)
            if errors:
                raise ValueError("; ".join(errors))
            updated = with_content_hash(
                claim.model_copy(
                    update={"status": ClaimStatus.HUMAN_APPROVED, "content_hash": "0" * 64}
                )
            )
            self.store.save_claim(run_id, updated.model_dump(mode="json"))
        snapshot = self.get_run(run_id)
        self._emit(
            snapshot,
            event_type="review.recorded",
            tool="human_reviewer",
            result={
                "object_type": object_type,
                "object_id": object_id,
                "decision": decision,
                "reviewer": reviewer,
            },
        )
        return review

    def approve_publishable_claims(self, run_id: str, reviewer: str, reason: str) -> list[str]:
        snapshot = self.get_run(run_id)
        approved: list[str] = []
        for claim in snapshot.claims:
            if claim_passes_technical_gate(claim):
                continue
            digest = claim_identity_hash(claim)
            self.submit_review(
                run_id,
                object_type="claim",
                object_id=claim.claim_id,
                decision="approved",
                reviewer=reviewer,
                reason=reason,
                expected_hash=digest,
            )
            approved.append(claim.claim_id)
        return approved

    def build_release(self, run_id: str, *, reviewer: str, reason: str) -> RunSnapshot:
        snapshot = self.get_run(run_id)
        if snapshot.workflow.state != WorkflowStatus.REVIEW_PENDING:
            raise ReleaseError("Solo se construye staging desde review_pending")
        approved_claims = [
            item for item in snapshot.claims if item.status == ClaimStatus.HUMAN_APPROVED
        ]
        if not approved_claims:
            raise ReleaseError("Ninguna afirmación aprobada; el release no puede publicarse")
        for claim in approved_claims:
            if matching_approval(claim, snapshot.reviews) is None:
                raise ReleaseError(f"Falta aprobación contemporánea de {claim.claim_id}")
        self._transition(
            snapshot, WorkflowStatus.APPROVED, reviewer, "revisión humana sobre hashes actuales"
        )
        self._transition(snapshot, WorkflowStatus.STAGING, "publisher", "construir paquete")
        drafts = drafts_from_claims(self.get_run(run_id).claims)
        snapshot = self.get_run(run_id)
        folder = build_staging(
            self.settings.staging_dir,
            run_id,
            sources=snapshot.sources,
            claims=snapshot.claims,
            conflicts=snapshot.conflicts,
            reviews=snapshot.reviews,
            drafts=drafts,
            metrics=snapshot.metrics,
            domain=DEMO_DOMAIN,
            as_of=date(2026, 8, 30),
            model_versions={
                "extractor": "deterministic-frontmatter-v1",
                "llm": self.settings.curator_model or "none",
            },
        )
        candidate_id = _id("can")
        manifest_hash = sha256_text((folder / "manifest.json").read_text(encoding="utf-8"))
        snapshot.candidate_id = candidate_id
        snapshot.candidate_hash = manifest_hash
        self._persist_run(snapshot)
        self._emit(
            snapshot,
            event_type="staging.built",
            tool="publisher",
            result={"candidate_id": candidate_id, "manifest_hash": manifest_hash},
        )
        self.submit_review(
            run_id,
            object_type="release_candidate",
            object_id=candidate_id,
            decision="approved",
            reviewer=reviewer,
            reason=reason,
            expected_hash=manifest_hash,
        )
        snapshot = self.get_run(run_id)
        self._transition(snapshot, WorkflowStatus.VALIDATING, "publisher", "gate reproducible")
        errors = validate_staging(folder, snapshot.claims)
        if errors:
            self._transition(snapshot, WorkflowStatus.FAILED, "publisher", "; ".join(errors)[:300])
            raise ReleaseError("; ".join(errors))
        if candidate_approval(candidate_id, manifest_hash, snapshot.reviews) is None:
            raise ReleaseError("La aprobación del candidato no coincide con el hash")
        release_id = _id("rel")
        release = make_release(
            release_id,
            domain=DEMO_DOMAIN,
            as_of=date(2026, 8, 30),
            folder=folder,
            claims=snapshot.claims,
            reviews=snapshot.reviews,
            metrics=snapshot.metrics,
            model_versions={"extractor": "deterministic-frontmatter-v1"},
        )
        destination = publish(folder, self.settings.releases_dir, release)
        self.store.save_release(release.model_dump(mode="json"))
        for claim in snapshot.claims:
            if claim.status == ClaimStatus.HUMAN_APPROVED:
                published = with_content_hash(
                    claim.model_copy(
                        update={"status": ClaimStatus.PUBLISHED, "content_hash": "0" * 64}
                    )
                )
                self.store.save_claim(run_id, published.model_dump(mode="json"))
        snapshot = self.get_run(run_id)
        snapshot.release_id = release_id
        snapshot.candidate_id = candidate_id
        snapshot.candidate_hash = manifest_hash
        self._persist_run(snapshot)
        self._transition(
            snapshot, WorkflowStatus.PUBLISHED, "publisher", f"publicado {destination.name}"
        )
        self._flush_jsonl(snapshot, terminal="run.completed")
        return self.get_run(run_id)

    def validate_release(self, release_id: str) -> dict:
        folder = self.settings.releases_dir / release_id
        if not folder.is_dir():
            raise ReleaseError("Release no encontrado")
        payload = self.store.get_release(release_id)
        claims = []
        if payload:
            from sales_curator.contracts.models import KnowledgeRelease

            release = KnowledgeRelease.model_validate(payload)
            run_id = None
            for item in self.store.list_runs():
                if item.get("release_id") == release_id:
                    run_id = item["run_id"]
                    break
            if run_id:
                claims = [ClaimRecord.model_validate(row) for row in self.store.list_claims(run_id)]
            errors = validate_staging(folder, claims)
            return {
                "release_id": release_id,
                "valid": not errors,
                "errors": errors,
                "manifest_hash": release.manifest_hash,
                "included": release.included_claim_ids,
                "excluded": release.excluded_claim_ids,
            }
        return {"release_id": release_id, "valid": False, "errors": ["sin metadatos en sqlite"]}

    def export_run(self, run_id: str) -> Path:
        snapshot = self.get_run(run_id)
        terminal = None
        if snapshot.workflow.state == WorkflowStatus.PUBLISHED:
            terminal = "run.completed"
        elif snapshot.workflow.state == WorkflowStatus.FAILED:
            terminal = "run.failed"
        path = self._flush_jsonl(snapshot, terminal=terminal)
        validate_run(path)
        return path

    def rollback_release(self, release_id: str) -> None:
        rollback(self.settings.releases_dir, release_id)

    def current_release(self) -> dict | None:
        return read_current(self.settings.releases_dir)

    def demo(self, fixture_dir: Path, reviewer: str, reason: str) -> RunSnapshot:
        snapshot = self.start_audit(fixture_dir)
        self.approve_publishable_claims(snapshot.workflow.run_id, reviewer, reason)
        return self.build_release(snapshot.workflow.run_id, reviewer=reviewer, reason=reason)

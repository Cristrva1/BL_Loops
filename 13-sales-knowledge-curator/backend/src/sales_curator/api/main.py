"""API local: corridas, SSE, revisión humana y releases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from sales_curator import __version__
from sales_curator.config import Settings, configuration_scope, find_env_file, lab_root
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.orchestration.machine import VISIBLE_NODES
from sales_curator.orchestration.service import CuratorService, RunSnapshot
from sales_curator.storage.releases import read_current

_settings = Settings()
_service = CuratorService(_settings)


class AuditRequest(BaseModel):
    source_dir: str = "fixtures/corpus"
    as_of: str | None = None
    dry_run: bool = False


class ReviewRequest(BaseModel):
    run_id: str
    object_type: str
    object_id: str
    decision: str
    reviewer: str
    reason: str = Field(min_length=8)
    expected_hash: str = Field(min_length=64, max_length=64)


class ReleaseBuildRequest(BaseModel):
    run_id: str
    reviewer: str
    reason: str = Field(min_length=8)


def _dump_snapshot(snapshot: RunSnapshot) -> dict[str, Any]:
    return {
        "run_id": snapshot.workflow.run_id,
        "state": snapshot.workflow.state.value,
        "previous_state": snapshot.workflow.previous_state.value
        if snapshot.workflow.previous_state
        else None,
        "stop_reason": snapshot.workflow.stop_reason,
        "network_enabled": snapshot.workflow.network_enabled,
        "urls_used": snapshot.workflow.urls_used,
        "nodes": list(VISIBLE_NODES),
        "sources": [item.model_dump(mode="json") for item in snapshot.sources],
        "claims": [
            {**item.model_dump(mode="json"), "identity_hash": claim_identity_hash(item)}
            for item in snapshot.claims
        ],
        "conflicts": [item.model_dump(mode="json") for item in snapshot.conflicts],
        "gaps": [item.model_dump(mode="json") for item in snapshot.gaps],
        "tasks": [item.model_dump(mode="json") for item in snapshot.tasks],
        "reviews": [item.model_dump(mode="json") for item in snapshot.reviews],
        "events": [item.model_dump(mode="json") for item in snapshot.events],
        "findings": snapshot.findings,
        "metrics": snapshot.metrics,
        "release_id": snapshot.release_id,
        "candidate_id": snapshot.candidate_id,
        "candidate_hash": snapshot.candidate_hash,
        "jsonl_path": snapshot.jsonl_path,
    }


def create_app(service: CuratorService | None = None) -> FastAPI:
    runtime = service or _service
    app = FastAPI(
        title="BL_Loops · Curador de conocimiento de ventas",
        version=__version__,
        description="Fábrica local de conocimiento trazable. La red está desactivada.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {"message": "Curador local listo", "docs": "/docs"}

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        env_file = find_env_file()
        return {
            "version": __version__,
            "network_enabled": runtime.settings.network_enabled,
            "telemetry": False,
            "extractor": "deterministic",
            "model_configured": bool(runtime.settings.curator_model),
            "configuration_scope": configuration_scope(env_file),
            "phase": "phase-1-local-vertical-slice",
        }

    @app.post("/api/runs/audit")
    def start_audit(request: AuditRequest) -> dict[str, Any]:
        source = Path(request.source_dir)
        if not source.is_absolute():
            source = lab_root() / source
        try:
            snapshot = runtime.start_audit(source, dry_run=request.dry_run)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _dump_snapshot(snapshot)

    @app.post("/api/runs/research")
    def research(request: AuditRequest) -> dict[str, Any]:
        return start_audit(request)

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        try:
            return _dump_snapshot(runtime.get_run(run_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/runs/{run_id}/events")
    def stream_events(run_id: str) -> StreamingResponse:
        try:
            runtime.get_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        def generate():
            events = runtime.store.list_events(run_id)
            for event in events:
                yield f"event: run.event\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
            snapshot = runtime.get_run(run_id)
            yield (
                "event: run.terminal\ndata: "
                + json.dumps({"run_id": run_id, "state": snapshot.workflow.state.value})
                + "\n\n"
            )

        return StreamingResponse(generate(), media_type="text/event-stream")

    @app.get("/api/sources")
    def sources(run_id: str) -> list[dict[str, Any]]:
        return _dump_snapshot(runtime.get_run(run_id))["sources"]

    @app.get("/api/claims")
    def claims(run_id: str, status: str | None = None) -> list[dict[str, Any]]:
        return [item.model_dump(mode="json") for item in runtime.list_claims(run_id, status)]

    @app.get("/api/conflicts")
    def conflicts(run_id: str) -> list[dict[str, Any]]:
        return _dump_snapshot(runtime.get_run(run_id))["conflicts"]

    @app.post("/api/reviews")
    def reviews(request: ReviewRequest) -> dict[str, Any]:
        try:
            decision = runtime.submit_review(
                request.run_id,
                object_type=request.object_type,
                object_id=request.object_id,
                decision=request.decision,
                reviewer=request.reviewer,
                reason=request.reason,
                expected_hash=request.expected_hash,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return decision.model_dump(mode="json")

    @app.post("/api/releases/build")
    def build_release(request: ReleaseBuildRequest) -> dict[str, Any]:
        try:
            snapshot = runtime.build_release(
                request.run_id, reviewer=request.reviewer, reason=request.reason
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _dump_snapshot(snapshot)

    @app.get("/api/releases/current")
    def current_release() -> dict[str, Any]:
        pointer = read_current(runtime.settings.releases_dir)
        return pointer or {}

    @app.get("/api/releases/{release_id}")
    def get_release(release_id: str) -> dict[str, Any]:
        try:
            return runtime.validate_release(release_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()

from __future__ import annotations

from pathlib import Path

import pytest

from sales_curator.contracts.models import WorkflowStatus
from sales_curator.orchestration.service import CuratorService
from sales_curator.storage.releases import read_current


def _stage(service: CuratorService, corpus):
    snapshot = service.start_audit(corpus)
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobacion didactica de afirmaciones publicables",
    )
    return service.build_release(snapshot.workflow.run_id)


def _approve(service: CuratorService, staged) -> None:
    service.submit_review(
        staged.workflow.run_id,
        object_type="release_candidate",
        object_id=staged.candidate_id,
        decision="approved",
        reviewer="operador-local",
        reason="Aprobacion editorial posterior sobre el hash exacto",
        expected_hash=staged.candidate_hash,
    )


def test_sqlite_failure_after_move_restores_staging_and_does_not_publish(
    service: CuratorService, corpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    staged = _stage(service, corpus)
    _approve(service, staged)
    run_id = staged.workflow.run_id
    staging_folder = service.settings.staging_dir / run_id

    def boom(*_args, **_kwargs):
        raise RuntimeError("sqlite down")

    monkeypatch.setattr(service.store, "save_release", boom)

    with pytest.raises(RuntimeError, match="sqlite"):
        service.publish_release(run_id)

    assert read_current(service.settings.releases_dir) is None
    assert staging_folder.is_dir()
    assert list(service.settings.releases_dir.glob("rel_*")) == []
    assert service.get_run(run_id).workflow.state != WorkflowStatus.PUBLISHED


def test_pointer_failure_after_sqlite_does_not_advertise_or_leave_validating_visible(
    service: CuratorService, corpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    staged = _stage(service, corpus)
    _approve(service, staged)
    run_id = staged.workflow.run_id
    from sales_curator.storage import releases as releases_mod

    original = releases_mod.atomic_write

    def guarded(path: Path, text: str) -> None:
        if path.name == "current.json":
            raise RuntimeError("pointer down")
        original(path, text)

    monkeypatch.setattr(releases_mod, "atomic_write", guarded)

    with pytest.raises(RuntimeError, match="pointer"):
        service.publish_release(run_id)

    assert read_current(service.settings.releases_dir) is None
    snapshot = service.get_run(run_id)
    assert snapshot.workflow.state != WorkflowStatus.VALIDATING
    packages = list(service.settings.releases_dir.glob("rel_*"))
    assert packages
    assert (service.settings.staging_dir / run_id).is_dir() or packages


def test_move_failure_keeps_staging_and_current(
    service: CuratorService, corpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    staged = _stage(service, corpus)
    _approve(service, staged)
    run_id = staged.workflow.run_id
    original = Path.replace

    def boom(self: Path, target: Path, **kwargs):
        if self.name == run_id:
            raise OSError("disk full")
        return original(self, target, **kwargs)

    monkeypatch.setattr(Path, "replace", boom)

    with pytest.raises(OSError, match="disk"):
        service.publish_release(run_id)

    assert read_current(service.settings.releases_dir) is None
    assert (service.settings.staging_dir / run_id).is_dir()
    assert list(service.settings.releases_dir.glob("rel_*")) == []
    assert service.get_run(run_id).workflow.state != WorkflowStatus.PUBLISHED

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from sales_curator.connectors.local_fs import IngestError
from sales_curator.domain.ingest import ingest_directory, ingest_file
from sales_curator.hashing import sha256_bytes

LAB_ROOT = Path(__file__).resolve().parents[2]
CORPUS = LAB_ROOT / "fixtures" / "corpus"


def test_ingest_preserves_bytes_and_does_not_modify_source() -> None:
    path = CORPUS / "01-current-discovery.md"
    before = path.read_bytes()
    mtime = path.stat().st_mtime
    ingested = ingest_file(
        path,
        allowed_root=LAB_ROOT,
        max_bytes=2_000_000,
        retrieved_at=datetime.now(UTC),
    )
    assert ingested.source.content_sha256 == sha256_bytes(before)
    assert path.read_bytes() == before
    assert path.stat().st_mtime == mtime


def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(IngestError):
        ingest_file(
            Path("../AGENTS.md"),
            allowed_root=CORPUS,
            max_bytes=2_000_000,
            retrieved_at=datetime.now(UTC),
        )


def test_unexpected_mime_is_rejected() -> None:
    with pytest.raises(IngestError):
        ingest_file(
            LAB_ROOT / "pyproject.toml",
            allowed_root=LAB_ROOT,
            max_bytes=2_000_000,
            retrieved_at=datetime.now(UTC),
        )


def test_empty_source_is_quarantined() -> None:
    ingested = ingest_file(
        CORPUS / "07-empty.md",
        allowed_root=LAB_ROOT,
        max_bytes=2_000_000,
        retrieved_at=datetime.now(UTC),
    )
    assert ingested.source.quarantine_status.value == "empty"


def test_directory_ingest_is_idempotent_on_hash() -> None:
    first = ingest_directory(
        CORPUS,
        allowed_root=LAB_ROOT,
        max_bytes=2_000_000,
        retrieved_at=datetime.now(UTC),
    )
    second = ingest_directory(
        CORPUS,
        allowed_root=LAB_ROOT,
        max_bytes=2_000_000,
        retrieved_at=datetime.now(UTC),
    )
    assert [item.source.content_sha256 for item in first] == [
        item.source.content_sha256 for item in second
    ]


def test_oversize_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "huge.md"
    path.write_text("---\ntitle: x\n---\n" + ("n" * 500), encoding="utf-8")
    with pytest.raises(IngestError, match="MAX_BYTES"):
        ingest_file(
            path,
            allowed_root=tmp_path,
            max_bytes=20,
            retrieved_at=datetime.now(UTC),
        )


def test_syndicated_origin_is_preserved() -> None:
    ingested = ingest_directory(
        CORPUS,
        allowed_root=LAB_ROOT,
        max_bytes=2_000_000,
        retrieved_at=datetime.now(UTC),
    )
    copy = next(
        item.source for item in ingested if item.source.source_id == "src-syndicated-discovery"
    )
    assert copy.origin_source_id == "src-current-discovery"
    assert copy.independence.value == "syndicated"

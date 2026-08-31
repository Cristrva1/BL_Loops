"""SQLite local. Cada laboratorio conserva su propia base."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (run_id, sequence)
);
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conflicts (
    conflict_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gaps (
    gap_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    decision_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS releases (
    release_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (
    run_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    full_text TEXT NOT NULL,
    body_start INTEGER NOT NULL,
    PRIMARY KEY (run_id, source_id)
);
"""


class CuratorStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def _put(
        self, table: str, key_col: str, key: str, run_id: str | None, payload: dict[str, Any]
    ) -> None:
        blob = json.dumps(payload, ensure_ascii=False)
        if run_id is None:
            self._conn.execute(
                f"INSERT OR REPLACE INTO {table} ({key_col}, payload) VALUES (?, ?)",
                (key, blob),
            )
        else:
            self._conn.execute(
                f"INSERT OR REPLACE INTO {table} ({key_col}, run_id, payload) VALUES (?, ?, ?)",
                (key, run_id, blob),
            )
        self._conn.commit()

    def _list(self, table: str, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is None:
            rows = self._conn.execute(f"SELECT payload FROM {table}").fetchall()
        else:
            rows = self._conn.execute(
                f"SELECT payload FROM {table} WHERE run_id = ?", (run_id,)
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def save_run(self, payload: dict[str, Any]) -> None:
        self._put("runs", "run_id", payload["run_id"], None, payload)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT payload FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def list_runs(self) -> list[dict[str, Any]]:
        return self._list("runs")

    def append_event(self, run_id: str, sequence: int, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO events (run_id, sequence, payload) VALUES (?, ?, ?)",
            (run_id, sequence, json.dumps(payload, ensure_ascii=False)),
        )
        self._conn.commit()

    def events_after(self, run_id: str, sequence: int) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT payload FROM events WHERE run_id = ? AND sequence > ? ORDER BY sequence",
            (run_id, sequence),
        ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def list_events(self, run_id: str) -> list[dict[str, Any]]:
        return self.events_after(run_id, 0)

    def save_source(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("sources", "source_id", payload["source_id"], run_id, payload)

    def save_artifact(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("artifacts", "artifact_id", payload["artifact_id"], run_id, payload)

    def save_claim(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("claims", "claim_id", payload["claim_id"], run_id, payload)

    def save_conflict(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("conflicts", "conflict_id", payload["conflict_id"], run_id, payload)

    def save_gap(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("gaps", "gap_id", payload["gap_id"], run_id, payload)

    def save_task(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("tasks", "task_id", payload["task_id"], run_id, payload)

    def save_review(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("reviews", "decision_id", payload["decision_id"], run_id, payload)

    def save_finding(self, run_id: str, payload: dict[str, Any]) -> None:
        self._put("findings", "finding_id", payload["finding_id"], run_id, payload)

    def save_release(self, payload: dict[str, Any]) -> None:
        self._put("releases", "release_id", payload["release_id"], None, payload)

    def list_sources(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("sources", run_id)

    def list_claims(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("claims", run_id)

    def list_conflicts(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("conflicts", run_id)

    def list_gaps(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("gaps", run_id)

    def list_tasks(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("tasks", run_id)

    def list_reviews(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("reviews", run_id)

    def list_findings(self, run_id: str) -> list[dict[str, Any]]:
        return self._list("findings", run_id)

    def save_document(self, run_id: str, source_id: str, full_text: str, body_start: int) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO documents (run_id, source_id, full_text, body_start) "
            "VALUES (?, ?, ?, ?)",
            (run_id, source_id, full_text, body_start),
        )
        self._conn.commit()

    def list_documents(self, run_id: str) -> list[tuple[str, str, int]]:
        rows = self._conn.execute(
            "SELECT source_id, full_text, body_start FROM documents WHERE run_id = ?",
            (run_id,),
        ).fetchall()
        return [(row["source_id"], row["full_text"], row["body_start"]) for row in rows]

    def get_release(self, release_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT payload FROM releases WHERE release_id = ?", (release_id,)
        ).fetchone()
        return json.loads(row["payload"]) if row else None

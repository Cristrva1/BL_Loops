from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from sales_curator.storage.sqlite import CuratorStore

RUN_SCOPED_TABLES = {
    "sources": "source_id",
    "artifacts": "artifact_id",
    "claims": "claim_id",
    "conflicts": "conflict_id",
    "gaps": "gap_id",
    "tasks": "task_id",
    "reviews": "decision_id",
    "findings": "finding_id",
}


def _create_legacy_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        for table, id_column in RUN_SCOPED_TABLES.items():
            connection.execute(
                f"""
                CREATE TABLE {table} (
                    {id_column} TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            payload = json.dumps({id_column: f"legacy-{table}", "marker": table})
            connection.execute(
                f"INSERT INTO {table} ({id_column}, run_id, payload) VALUES (?, ?, ?)",
                (f"legacy-{table}", "run_legacy", payload),
            )
        connection.commit()
    finally:
        connection.close()


def _primary_key_columns(store: CuratorStore, table: str) -> list[str]:
    rows = store._conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row["name"] for row in sorted(rows, key=lambda item: item["pk"]) if row["pk"]]


def test_same_entity_id_is_preserved_independently_per_run(tmp_path: Path) -> None:
    store = CuratorStore(tmp_path / "history.sqlite")
    try:
        store.save_source("run_first", {"source_id": "src-shared", "title": "primera"})
        store.save_source("run_second", {"source_id": "src-shared", "title": "segunda"})

        assert store.list_sources("run_first") == [{"source_id": "src-shared", "title": "primera"}]
        assert store.list_sources("run_second") == [{"source_id": "src-shared", "title": "segunda"}]
    finally:
        store.close()


def test_legacy_run_scoped_tables_migrate_without_losing_rows_and_are_idempotent(
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy.sqlite"
    _create_legacy_database(path)

    store = CuratorStore(path)
    try:
        for table, id_column in RUN_SCOPED_TABLES.items():
            assert _primary_key_columns(store, table) == ["run_id", id_column]
            row = store._conn.execute(
                f"SELECT run_id, {id_column}, payload FROM {table}"
            ).fetchone()
            assert row["run_id"] == "run_legacy"
            assert row[id_column] == f"legacy-{table}"
            assert json.loads(row["payload"])["marker"] == table
    finally:
        store.close()

    reopened = CuratorStore(path)
    try:
        for table, id_column in RUN_SCOPED_TABLES.items():
            assert _primary_key_columns(reopened, table) == ["run_id", id_column]
            count = reopened._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert count == 1
    finally:
        reopened.close()

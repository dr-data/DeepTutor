"""Smoke tests for Alembic migrations.

These tests exercise the migration framework end-to-end:

- Fresh databases can be upgraded to head.
- Every migration supports downgrade back to base.
- Existing pre-migration SQLite files can be stamped and upgraded without
  data loss (the real-world upgrade path for running deployments).
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SCHOOL_TABLES = {
    "alembic_version",
    "sessions",
    "messages",
    "turns",
    "turn_events",
    "schools",
    "users",
    "classrooms",
    "classroom_members",
    "assignments",
    "assignment_submissions",
    "grades",
    "audit_logs",
}


def _run_alembic(db_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=PROJECT_ROOT,
        env={
            "DEEPTUTOR_DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
            "PATH": "/usr/local/bin:/usr/bin:/bin",
        },
        check=False,
        capture_output=True,
        text=True,
    )


def _tables(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return {row[0] for row in rows if not row[0].startswith("sqlite_")}


def test_fresh_upgrade_creates_all_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "fresh.db"
    result = _run_alembic(db_path, "upgrade", "head")
    assert result.returncode == 0, f"upgrade failed: {result.stderr}"
    assert _tables(db_path) == EXPECTED_SCHOOL_TABLES


def test_full_downgrade_removes_all_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "down.db"
    up = _run_alembic(db_path, "upgrade", "head")
    assert up.returncode == 0
    down = _run_alembic(db_path, "downgrade", "base")
    assert down.returncode == 0, f"downgrade failed: {down.stderr}"
    # Only the alembic_version bookkeeping table should remain after a
    # full downgrade to base.
    assert _tables(db_path) == {"alembic_version"}


def test_stamp_and_upgrade_preserves_existing_data(tmp_path: Path) -> None:
    """Simulates an existing deployment with hand-rolled schema + data.

    The upgrade path for such deployments is:
        1. ``alembic stamp 0001`` (mark current schema as revision 0001)
        2. ``alembic upgrade head`` (apply any subsequent migrations)

    Original data in the ``sessions`` table must be preserved.
    """
    db_path = tmp_path / "existing.db"
    # Hand-roll the 0001 schema and insert a sample row.
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New conversation',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                compressed_summary TEXT DEFAULT '',
                summary_up_to_msg_id INTEGER DEFAULT 0,
                preferences_json TEXT DEFAULT '{}'
            );
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                capability TEXT DEFAULT '',
                events_json TEXT DEFAULT '',
                attachments_json TEXT DEFAULT '',
                created_at REAL NOT NULL
            );
            CREATE TABLE turns (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                capability TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'running',
                error TEXT DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                finished_at REAL
            );
            CREATE TABLE turn_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turn_id TEXT NOT NULL,
                seq INTEGER NOT NULL,
                type TEXT NOT NULL,
                source TEXT DEFAULT '',
                stage TEXT DEFAULT '',
                content TEXT DEFAULT '',
                metadata_json TEXT DEFAULT '',
                timestamp REAL NOT NULL,
                created_at REAL NOT NULL,
                UNIQUE(turn_id, seq)
            );
            INSERT INTO sessions (id, title, created_at, updated_at)
            VALUES ('legacy-session', 'Pre-migration data', 1.0, 1.0);
            """
        )
        conn.commit()

    # Stamp as 0001 — tells Alembic the current schema matches revision 0001.
    stamp = _run_alembic(db_path, "stamp", "0001")
    assert stamp.returncode == 0

    # Upgrade to head — applies 0002 and 0003 on top of the existing data.
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, f"upgrade failed: {upgrade.stderr}"

    # Legacy row must still be there.
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, title FROM sessions WHERE id='legacy-session'"
        ).fetchone()
    assert row is not None
    assert row[0] == "legacy-session"
    assert row[1] == "Pre-migration data"

    # New school tables must be present after the upgrade.
    assert _tables(db_path) >= {"schools", "users", "classrooms", "assignments"}


@pytest.mark.parametrize(
    "revision,required_tables",
    [
        ("0001", {"sessions", "messages", "turns", "turn_events"}),
        ("0002", {"schools", "users", "classrooms", "classroom_members"}),
        ("0003", {"assignments", "assignment_submissions", "grades", "audit_logs"}),
    ],
)
def test_each_revision_creates_its_tables(
    tmp_path: Path, revision: str, required_tables: set[str]
) -> None:
    db_path = tmp_path / f"rev_{revision}.db"
    result = _run_alembic(db_path, "upgrade", revision)
    assert result.returncode == 0, f"upgrade to {revision} failed: {result.stderr}"
    assert _tables(db_path) >= required_tables

"""Shared fixtures for auth tests.

Provides a temporary SQLite database with the full school schema applied
via Alembic, so tests exercise the same code path as a real deployment.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine

from deeptutor.auth.users import UserStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run_migrations(db_path: Path) -> None:
    """Apply all migrations against the given SQLite file using Alembic."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env={
            "DEEPTUTOR_DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
            "PATH": "/usr/local/bin:/usr/bin:/bin",
        },
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"alembic upgrade failed: {result.stdout}\n{result.stderr}"
        )


@pytest.fixture()
def migrated_db(tmp_path: Path) -> Path:
    """Return a path to a fresh SQLite DB with all migrations applied."""
    db_path = tmp_path / "test_school.db"
    _run_migrations(db_path)
    return db_path


@pytest.fixture()
def user_store(migrated_db: Path) -> UserStore:
    """Return a :class:`UserStore` bound to a fresh migrated DB."""
    engine = create_engine(f"sqlite:///{migrated_db.as_posix()}", future=True)
    return UserStore(engine)

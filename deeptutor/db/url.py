"""Database URL resolution for DeepTutor.

Determines the database connection string at runtime in the following order:

1. ``DEEPTUTOR_DATABASE_URL`` environment variable (explicit override)
2. ``DATABASE_URL`` environment variable (standard convention)
3. Default SQLite file at ``data/user/chat_history.db`` (single-user mode)

This single source of truth is consumed by Alembic's ``env.py`` and by any
runtime code that needs a SQLAlchemy engine. Keeping the logic here avoids
duplicated environment lookups across the codebase.
"""

from __future__ import annotations

import os
from pathlib import Path


def resolve_database_url(project_root: Path | None = None) -> str:
    """Return the database URL to use for this process.

    Args:
        project_root: Optional project root used to build the default SQLite
            path. When omitted, the project root is inferred from this file's
            location (``deeptutor/db/url.py`` → two parents up).

    Returns:
        A SQLAlchemy-compatible database URL. For SQLite this is always an
        absolute path so Alembic can locate the file regardless of CWD.
    """
    explicit = os.environ.get("DEEPTUTOR_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if explicit:
        return explicit

    root = project_root or Path(__file__).resolve().parents[2]
    default_sqlite = root / "data" / "user" / "chat_history.db"
    default_sqlite.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{default_sqlite.as_posix()}"


def is_sqlite(url: str) -> bool:
    """Return True if the URL points at a SQLite database."""
    return url.startswith("sqlite")


def is_postgres(url: str) -> bool:
    """Return True if the URL points at a PostgreSQL database."""
    return url.startswith(("postgresql", "postgres"))


__all__ = ["resolve_database_url", "is_sqlite", "is_postgres"]

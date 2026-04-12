"""Database layer for DeepTutor.

This package hosts schema migrations (Alembic) and shared database helpers
used by both the single-user (SQLite) and school (PostgreSQL) deployments.
"""

from deeptutor.db.url import resolve_database_url

__all__ = ["resolve_database_url"]

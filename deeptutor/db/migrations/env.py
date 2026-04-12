"""Alembic environment for DeepTutor.

Resolves the database URL via :mod:`deeptutor.db.url`, which honours
``DEEPTUTOR_DATABASE_URL``/``DATABASE_URL`` before falling back to the
single-user SQLite file at ``data/user/chat_history.db``.

The migrations themselves use raw ``op`` calls rather than SQLAlchemy models,
so no ``target_metadata`` needs to be wired up here. This keeps the migration
files self-contained and portable between SQLite and PostgreSQL.
"""

from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# ------------------------------------------------------------------
# Ensure the project root is importable so we can load deeptutor.db.url
# even when alembic is invoked from an arbitrary working directory.
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from deeptutor.db.url import resolve_database_url  # noqa: E402

config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the resolved database URL into Alembic's config so both
# offline (--sql) and online modes see the same value.
database_url = resolve_database_url(PROJECT_ROOT)
config.set_main_option("sqlalchemy.url", database_url)

# No declarative metadata — migrations use raw op.* calls.
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL without a live connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        url = str(connection.engine.url)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enable batch mode on SQLite so ALTER TABLE operations work.
            render_as_batch=url.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

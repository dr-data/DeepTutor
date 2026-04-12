"""Initial schema: sessions, messages, turns, turn_events

Captures the current ``chat_history.db`` schema created by
``SQLiteSessionStore._initialize()`` so that fresh databases are created via
Alembic, and existing SQLite databases can be ``alembic stamped`` as being
at this revision without data loss.

Tables created:
- sessions
- messages
- turns
- turn_events

Note: this migration intentionally mirrors the existing hand-rolled schema.
Any schema evolution beyond this point should land in new migrations.

Revision ID: 0001
Revises:
Create Date: 2026-04-12
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ----------------------------------------------------------------------
    # sessions
    # ----------------------------------------------------------------------
    op.create_table(
        "sessions",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'New conversation'"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.Column(
            "compressed_summary",
            sa.Text(),
            nullable=True,
            server_default=sa.text("''"),
        ),
        sa.Column(
            "summary_up_to_msg_id",
            sa.Integer(),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "preferences_json",
            sa.Text(),
            nullable=True,
            server_default=sa.text("'{}'"),
        ),
    )
    op.create_index(
        "idx_sessions_updated_at",
        "sessions",
        [sa.text("updated_at DESC")],
    )

    # ----------------------------------------------------------------------
    # messages
    # ----------------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "session_id",
            sa.Text(),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column("capability", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column("events_json", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column(
            "attachments_json",
            sa.Text(),
            nullable=True,
            server_default=sa.text("''"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
    )
    op.create_index(
        "idx_messages_session_created",
        "messages",
        ["session_id", "created_at", "id"],
    )

    # ----------------------------------------------------------------------
    # turns
    # ----------------------------------------------------------------------
    op.create_table(
        "turns",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Text(),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capability", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'running'"),
        ),
        sa.Column("error", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.Column("finished_at", sa.Float(), nullable=True),
    )
    op.create_index(
        "idx_turns_session_updated",
        "turns",
        ["session_id", sa.text("updated_at DESC")],
    )
    op.create_index(
        "idx_turns_session_status",
        "turns",
        ["session_id", "status", sa.text("updated_at DESC")],
    )

    # ----------------------------------------------------------------------
    # turn_events
    # ----------------------------------------------------------------------
    op.create_table(
        "turn_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "turn_id",
            sa.Text(),
            sa.ForeignKey("turns.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column("stage", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column("content", sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column(
            "metadata_json",
            sa.Text(),
            nullable=True,
            server_default=sa.text("''"),
        ),
        sa.Column("timestamp", sa.Float(), nullable=False),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.UniqueConstraint("turn_id", "seq", name="uq_turn_events_turn_seq"),
    )
    op.create_index(
        "idx_turn_events_turn_seq",
        "turn_events",
        ["turn_id", "seq"],
    )


def downgrade() -> None:
    op.drop_index("idx_turn_events_turn_seq", table_name="turn_events")
    op.drop_table("turn_events")

    op.drop_index("idx_turns_session_status", table_name="turns")
    op.drop_index("idx_turns_session_updated", table_name="turns")
    op.drop_table("turns")

    op.drop_index("idx_messages_session_created", table_name="messages")
    op.drop_table("messages")

    op.drop_index("idx_sessions_updated_at", table_name="sessions")
    op.drop_table("sessions")

"""School core: schools, users, classrooms, classroom_members

Adds the minimum set of tables needed to run DeepTutor as a multi-user
school deployment:

- ``schools``              — tenant boundary (one row per school)
- ``users``                — authenticated accounts (student/teacher/admin)
- ``classrooms``           — a class owned by a teacher within a school
- ``classroom_members``    — student ↔ classroom join table
- ``session_ownership``    — back-fills ``user_id`` and ``classroom_id`` onto
                              the existing ``sessions`` table so that queries
                              can scope to a teacher's class without a second
                              round trip.

This migration is additive: existing sessions remain usable because
``user_id`` and ``classroom_id`` are nullable. The Sprint 1 code change that
starts writing these columns is landed separately.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-12
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ----------------------------------------------------------------------
    # schools — the top-level tenant
    # ----------------------------------------------------------------------
    op.create_table(
        "schools",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("locale", sa.Text(), nullable=False, server_default=sa.text("'en'")),
        sa.Column(
            "settings_json",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_schools_slug"),
    )

    # ----------------------------------------------------------------------
    # users — accounts with role-based access
    # ----------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "school_id",
            sa.Text(),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        # admin | teacher | student
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("last_login_at", sa.Float(), nullable=True),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.UniqueConstraint("school_id", "email", name="uq_users_school_email"),
    )
    op.create_index("idx_users_school_role", "users", ["school_id", "role"])

    # ----------------------------------------------------------------------
    # classrooms — owned by a teacher, contains students
    # ----------------------------------------------------------------------
    op.create_table(
        "classrooms",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "school_id",
            sa.Text(),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("grade_level", sa.Text(), nullable=True),
        sa.Column("invite_code", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.UniqueConstraint("invite_code", name="uq_classrooms_invite_code"),
    )
    op.create_index("idx_classrooms_school_owner", "classrooms", ["school_id", "owner_user_id"])

    # ----------------------------------------------------------------------
    # classroom_members — many-to-many student ↔ classroom
    # ----------------------------------------------------------------------
    op.create_table(
        "classroom_members",
        sa.Column(
            "classroom_id",
            sa.Text(),
            sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("joined_at", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("classroom_id", "user_id", name="pk_classroom_members"),
    )
    op.create_index("idx_classroom_members_user", "classroom_members", ["user_id"])

    # ----------------------------------------------------------------------
    # Back-fill ownership columns on sessions so queries can scope quickly.
    # Nullable on purpose: pre-existing sessions have no owner.
    # ----------------------------------------------------------------------
    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("user_id", sa.Text(), nullable=True))
        batch.add_column(sa.Column("classroom_id", sa.Text(), nullable=True))
        batch.add_column(sa.Column("school_id", sa.Text(), nullable=True))

    op.create_index("idx_sessions_user", "sessions", ["user_id"])
    op.create_index(
        "idx_sessions_classroom_updated",
        "sessions",
        ["classroom_id", sa.text("updated_at DESC")],
    )
    op.create_index("idx_sessions_school", "sessions", ["school_id"])


def downgrade() -> None:
    op.drop_index("idx_sessions_school", table_name="sessions")
    op.drop_index("idx_sessions_classroom_updated", table_name="sessions")
    op.drop_index("idx_sessions_user", table_name="sessions")
    with op.batch_alter_table("sessions") as batch:
        batch.drop_column("school_id")
        batch.drop_column("classroom_id")
        batch.drop_column("user_id")

    op.drop_index("idx_classroom_members_user", table_name="classroom_members")
    op.drop_table("classroom_members")

    op.drop_index("idx_classrooms_school_owner", table_name="classrooms")
    op.drop_table("classrooms")

    op.drop_index("idx_users_school_role", table_name="users")
    op.drop_table("users")

    op.drop_table("schools")

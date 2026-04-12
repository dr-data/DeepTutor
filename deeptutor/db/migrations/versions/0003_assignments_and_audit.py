"""Assignments, submissions, grades, and audit log

Adds the tables required for Sprint 3 (assignments + enhanced assessment)
and Sprint 4 (content safety + audit logging):

- ``assignments``         — a task a teacher gives to a classroom
- ``assignment_submissions`` — student attempts / submissions
- ``grades``              — teacher feedback and score per submission
- ``audit_logs``          — append-only log of AI interactions and teacher
                             actions (for content safety / FERPA review)

The assignments table references the work type to the existing DeepTutor
capabilities (``chat``, ``deep_question``, ``guide``, ``deep_solve``,
``deep_research``, ``co_writer``) so no new runtime code is needed in
phase 1 — a submission is just a pointer to the existing session artifact.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-12
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ----------------------------------------------------------------------
    # assignments — teacher-created tasks
    # ----------------------------------------------------------------------
    op.create_table(
        "assignments",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "classroom_id",
            sa.Text(),
            sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # chat | deep_question | guide | deep_solve | deep_research | co_writer
        sa.Column("capability", sa.Text(), nullable=False),
        sa.Column(
            "config_json",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("knowledge_base", sa.Text(), nullable=True),
        sa.Column("points_possible", sa.Integer(), nullable=True),
        sa.Column("available_at", sa.Float(), nullable=True),
        sa.Column("due_at", sa.Float(), nullable=True),
        sa.Column("allow_late", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("time_limit_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
    )
    op.create_index(
        "idx_assignments_classroom_due",
        "assignments",
        ["classroom_id", "due_at"],
    )

    # ----------------------------------------------------------------------
    # assignment_submissions — one row per student attempt
    # ----------------------------------------------------------------------
    op.create_table(
        "assignment_submissions",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "assignment_id",
            sa.Text(),
            sa.ForeignKey("assignments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Optional link to the underlying chat/deep_solve/etc. session.
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'in_progress'"),
        ),
        sa.Column("started_at", sa.Float(), nullable=False),
        sa.Column("submitted_at", sa.Float(), nullable=True),
        sa.Column(
            "content_json",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.UniqueConstraint(
            "assignment_id",
            "student_user_id",
            "attempt_number",
            name="uq_submission_assignment_student_attempt",
        ),
    )
    op.create_index(
        "idx_submissions_assignment_status",
        "assignment_submissions",
        ["assignment_id", "status"],
    )
    op.create_index(
        "idx_submissions_student",
        "assignment_submissions",
        ["student_user_id", "submitted_at"],
    )

    # ----------------------------------------------------------------------
    # grades — teacher scores and feedback
    # ----------------------------------------------------------------------
    op.create_table(
        "grades",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Text(),
            sa.ForeignKey("assignment_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "graded_by_user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("rubric_json", sa.Text(), nullable=True),
        sa.Column("graded_at", sa.Float(), nullable=False),
        sa.UniqueConstraint("submission_id", name="uq_grades_submission"),
    )

    # ----------------------------------------------------------------------
    # audit_logs — append-only record of sensitive events
    # ----------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("school_id", sa.Text(), nullable=True),
        sa.Column("actor_user_id", sa.Text(), nullable=True),
        # ai_response | login | grade_change | safety_flag | export | ...
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.Text(), nullable=True),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("severity", sa.Text(), nullable=False, server_default=sa.text("'info'")),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("created_at", sa.Float(), nullable=False),
    )
    op.create_index(
        "idx_audit_school_created",
        "audit_logs",
        ["school_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_audit_actor_created",
        "audit_logs",
        ["actor_user_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_audit_event_type",
        "audit_logs",
        ["event_type", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("idx_audit_event_type", table_name="audit_logs")
    op.drop_index("idx_audit_actor_created", table_name="audit_logs")
    op.drop_index("idx_audit_school_created", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_table("grades")

    op.drop_index("idx_submissions_student", table_name="assignment_submissions")
    op.drop_index("idx_submissions_assignment_status", table_name="assignment_submissions")
    op.drop_table("assignment_submissions")

    op.drop_index("idx_assignments_classroom_due", table_name="assignments")
    op.drop_table("assignments")

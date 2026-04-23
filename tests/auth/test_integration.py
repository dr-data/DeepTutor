"""End-to-end integration test for the school auth path.

Exercises every new module in sequence:

1. Run Alembic migrations against a fresh SQLite database.
2. Create a school and a teacher via :class:`UserStore`.
3. Authenticate the teacher and mint a JWT.
4. Decode the JWT and verify claims.
5. Check role-based capability gates.

If this test passes, the Sprint-1 school plumbing works end-to-end on at
least one backend (SQLite). The same code path runs against PostgreSQL
when ``DEEPTUTOR_DATABASE_URL`` points at a Postgres instance.
"""

from __future__ import annotations

from deeptutor.auth.roles import Role, role_can
from deeptutor.auth.tokens import create_access_token, decode_access_token
from deeptutor.auth.users import UserStore


def test_full_school_auth_flow(
    user_store: UserStore,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "integration-test-secret")

    # 1. Seed a school with an admin and a teacher.
    school_id = user_store.create_school(
        name="Integration High School",
        slug="integration-high",
    )
    admin = user_store.create_user(
        school_id=school_id,
        email="admin@school.test",
        display_name="Principal Admin",
        role=Role.ADMIN,
        password="admin-pass-1",
    )
    teacher = user_store.create_user(
        school_id=school_id,
        email="teacher@school.test",
        display_name="Mr. Teacher",
        role=Role.TEACHER,
        password="teach-pass-1",
    )

    # 2. Admin authenticates and gets a token.
    admin_authenticated = user_store.authenticate(
        school_id=school_id,
        email="admin@school.test",
        password="admin-pass-1",
    )
    assert admin_authenticated is not None
    assert admin_authenticated.id == admin.id

    admin_token = create_access_token(
        user_id=admin.id,
        school_id=school_id,
        role=admin.role,
    )
    admin_claims = decode_access_token(admin_token)
    assert admin_claims.user_id == admin.id
    assert admin_claims.role == "admin"

    # 3. Teacher authenticates and gets a token.
    teacher_authenticated = user_store.authenticate(
        school_id=school_id,
        email="teacher@school.test",
        password="teach-pass-1",
    )
    assert teacher_authenticated is not None
    teacher_token = create_access_token(
        user_id=teacher.id,
        school_id=school_id,
        role=teacher.role,
    )
    teacher_claims = decode_access_token(teacher_token)
    assert teacher_claims.role == "teacher"

    # 4. Role gates behave as expected.
    assert role_can(admin_claims.role, "school.manage")
    assert role_can(admin_claims.role, "classroom.create")
    assert not role_can(teacher_claims.role, "school.manage")
    assert role_can(teacher_claims.role, "classroom.create")

    # 5. Wrong password still rejects even for known users.
    assert (
        user_store.authenticate(
            school_id=school_id,
            email="teacher@school.test",
            password="not-the-real-password",
        )
        is None
    )

    # 6. touch_last_login updates the record.
    assert teacher.last_login_at is None
    user_store.touch_last_login(teacher.id)
    refreshed = user_store.get_user_by_id(teacher.id)
    assert refreshed is not None
    assert refreshed.last_login_at is not None

"""Integration tests for :mod:`deeptutor.auth.users` against a migrated DB."""

from __future__ import annotations

import pytest

from deeptutor.auth.roles import Role
from deeptutor.auth.users import UserStore


def _seed_school(user_store: UserStore) -> str:
    return user_store.create_school(name="Test High School", slug="test-high")


def test_create_and_fetch_user(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user = user_store.create_user(
        school_id=school_id,
        email="alice@school.test",
        display_name="Alice",
        role=Role.TEACHER,
        password="hunter2-correct",
    )
    assert user.id.startswith("usr_")
    assert user.school_id == school_id
    assert user.email == "alice@school.test"
    assert user.role == "teacher"

    by_email = user_store.get_user_by_email(school_id, "alice@school.test")
    assert by_email is not None
    assert by_email.id == user.id

    by_id = user_store.get_user_by_id(user.id)
    assert by_id is not None
    assert by_id.email == "alice@school.test"


def test_email_is_normalised_to_lowercase(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user_store.create_user(
        school_id=school_id,
        email="Alice@School.Test",
        display_name="Alice",
        role=Role.TEACHER,
        password="hunter2-correct",
    )
    # Lookup with mixed case should still resolve.
    found = user_store.get_user_by_email(school_id, "ALICE@school.test")
    assert found is not None
    assert found.email == "alice@school.test"


def test_authenticate_returns_user_on_match(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user_store.create_user(
        school_id=school_id,
        email="bob@school.test",
        display_name="Bob",
        role=Role.STUDENT,
        password="secret-pass-1",
    )
    result = user_store.authenticate(
        school_id=school_id,
        email="bob@school.test",
        password="secret-pass-1",
    )
    assert result is not None
    assert result.email == "bob@school.test"
    # Result never exposes the password hash (dataclass doesn't define it).
    assert not hasattr(result, "password_hash")


def test_authenticate_rejects_wrong_password(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user_store.create_user(
        school_id=school_id,
        email="carol@school.test",
        display_name="Carol",
        role=Role.STUDENT,
        password="right",
    )
    assert (
        user_store.authenticate(
            school_id=school_id,
            email="carol@school.test",
            password="wrong",
        )
        is None
    )


def test_authenticate_rejects_unknown_user(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    assert (
        user_store.authenticate(
            school_id=school_id,
            email="ghost@school.test",
            password="whatever",
        )
        is None
    )


def test_duplicate_email_within_school_raises(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user_store.create_user(
        school_id=school_id,
        email="dup@school.test",
        display_name="First",
        role=Role.STUDENT,
        password="p1",
    )
    with pytest.raises(Exception):
        user_store.create_user(
            school_id=school_id,
            email="dup@school.test",
            display_name="Second",
            role=Role.STUDENT,
            password="p2",
        )


def test_same_email_allowed_across_schools(user_store: UserStore) -> None:
    school_a = _seed_school(user_store)
    school_b = user_store.create_school(name="Another", slug="another")
    user_store.create_user(
        school_id=school_a,
        email="shared@school.test",
        display_name="A",
        role=Role.STUDENT,
        password="p1",
    )
    user_store.create_user(
        school_id=school_b,
        email="shared@school.test",
        display_name="B",
        role=Role.STUDENT,
        password="p2",
    )
    # Each school sees only its own user.
    a_user = user_store.get_user_by_email(school_a, "shared@school.test")
    b_user = user_store.get_user_by_email(school_b, "shared@school.test")
    assert a_user is not None and b_user is not None
    assert a_user.id != b_user.id
    assert a_user.school_id == school_a
    assert b_user.school_id == school_b


def test_touch_last_login_updates_field(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    user = user_store.create_user(
        school_id=school_id,
        email="login@school.test",
        display_name="L",
        role=Role.STUDENT,
        password="p",
    )
    assert user.last_login_at is None
    user_store.touch_last_login(user.id)
    refreshed = user_store.get_user_by_id(user.id)
    assert refreshed is not None
    assert refreshed.last_login_at is not None
    assert refreshed.last_login_at > 0


def test_unknown_role_raises(user_store: UserStore) -> None:
    school_id = _seed_school(user_store)
    with pytest.raises(ValueError):
        user_store.create_user(
            school_id=school_id,
            email="x@school.test",
            display_name="X",
            role="superuser",
            password="p",
        )

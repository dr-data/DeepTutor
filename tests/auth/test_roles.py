"""Tests for :mod:`deeptutor.auth.roles`."""

from __future__ import annotations

from deeptutor.auth.roles import Role, role_can


def test_admin_has_manage_capabilities() -> None:
    assert role_can(Role.ADMIN, "school.manage")
    assert role_can(Role.ADMIN, "users.manage")
    assert role_can(Role.ADMIN, "classroom.create")


def test_teacher_can_manage_classrooms_but_not_school() -> None:
    assert role_can(Role.TEACHER, "classroom.create")
    assert role_can(Role.TEACHER, "assignment.grade")
    assert not role_can(Role.TEACHER, "school.manage")
    assert not role_can(Role.TEACHER, "users.manage")


def test_student_can_submit_but_not_grade() -> None:
    assert role_can(Role.STUDENT, "assignment.submit")
    assert role_can(Role.STUDENT, "chat.use")
    assert not role_can(Role.STUDENT, "assignment.create")
    assert not role_can(Role.STUDENT, "assignment.grade")


def test_unknown_capability_is_denied() -> None:
    assert not role_can(Role.ADMIN, "nonexistent.capability")


def test_unknown_role_is_denied() -> None:
    assert not role_can("superuser", "school.manage")


def test_role_can_accepts_plain_string() -> None:
    assert role_can("teacher", "classroom.create")
    assert not role_can("student", "classroom.create")

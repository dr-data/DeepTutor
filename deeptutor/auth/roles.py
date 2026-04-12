"""Role definitions for DeepTutor school deployments.

Three roles cover the secondary-school use case:

- ``admin``   — school-wide configuration, user management
- ``teacher`` — create classrooms and assignments, monitor students
- ``student`` — take assignments, chat with the AI, view own work

Roles are stored as lowercase strings in ``users.role``. We keep the
``Role`` enum thin — just the values and a helper for membership checks —
so database code can continue to use plain strings without importing the
enum.
"""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """The three roles available in a school deployment."""

    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


# Hierarchical capabilities. Each entry lists the roles allowed to perform
# the named capability. Keep the list small and additive — more granular
# permission checks should happen at the resource level (e.g. "is this
# student enrolled in the classroom this assignment belongs to?").
_CAPABILITIES: dict[str, frozenset[Role]] = {
    "school.manage": frozenset({Role.ADMIN}),
    "users.manage": frozenset({Role.ADMIN}),
    "classroom.create": frozenset({Role.ADMIN, Role.TEACHER}),
    "classroom.monitor": frozenset({Role.ADMIN, Role.TEACHER}),
    "assignment.create": frozenset({Role.ADMIN, Role.TEACHER}),
    "assignment.grade": frozenset({Role.ADMIN, Role.TEACHER}),
    "assignment.submit": frozenset({Role.STUDENT}),
    "chat.use": frozenset({Role.ADMIN, Role.TEACHER, Role.STUDENT}),
}


def role_can(role: str | Role, capability: str) -> bool:
    """Return True if ``role`` is permitted to perform ``capability``.

    Unknown roles and unknown capabilities both return False, so callers
    fail closed by default.
    """
    try:
        resolved = Role(role) if isinstance(role, str) else role
    except ValueError:
        return False
    allowed = _CAPABILITIES.get(capability)
    if allowed is None:
        return False
    return resolved in allowed


__all__ = ["Role", "role_can"]

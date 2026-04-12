"""Authentication and authorization for DeepTutor school deployments.

This package is opt-in: single-user deployments that leave ``SCHOOL_MODE``
unset continue to run without auth. When ``SCHOOL_MODE=true`` and the
database has the school schema (migrations 0002+), FastAPI can wire the
middleware in :mod:`deeptutor.auth.middleware` to enforce JWT-backed
role-based access control.

The building blocks are split into small modules so each piece can be
unit-tested independently:

- :mod:`deeptutor.auth.passwords` — bcrypt hashing helpers
- :mod:`deeptutor.auth.tokens` — JWT encode/decode with configurable secret
- :mod:`deeptutor.auth.roles` — role enum and permission helpers
- :mod:`deeptutor.auth.users` — user store (create/lookup/authenticate)
- :mod:`deeptutor.auth.middleware` — FastAPI dependency/middleware
"""

from deeptutor.auth.passwords import hash_password, verify_password
from deeptutor.auth.roles import Role, role_can
from deeptutor.auth.tokens import create_access_token, decode_access_token

__all__ = [
    "Role",
    "role_can",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]

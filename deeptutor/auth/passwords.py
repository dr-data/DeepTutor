"""Password hashing helpers using bcrypt directly.

Uses the ``bcrypt`` library's ``hashpw``/``checkpw`` API rather than going
through passlib. This avoids a layering issue where passlib 1.7.x is
incompatible with bcrypt 5.x (bcrypt removed the ``__about__`` attribute),
and it keeps our dependency tree one layer shallower.

Password length: bcrypt truncates to 72 bytes. We pre-hash the password
through SHA-256 so that passphrases longer than 72 bytes still yield
unique hashes. This is a standard workaround used by Django, Flask-Bcrypt,
and others.
"""

from __future__ import annotations

import base64
import hashlib

import bcrypt

_DEFAULT_ROUNDS = 12


def _prepare(password: str) -> bytes:
    """Pre-hash the password so bcrypt sees a fixed-length input.

    Using SHA-256 + base64 encoding yields 44 ASCII bytes, well under
    bcrypt's 72-byte limit, and ensures passwords longer than 72 chars
    still produce distinct hashes.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        plain_password: The plaintext password, must be non-empty.

    Returns:
        A bcrypt hash string safe to store in the ``users.password_hash`` column.

    Raises:
        ValueError: If ``plain_password`` is empty.
    """
    if not plain_password:
        raise ValueError("Password must not be empty")
    salted = bcrypt.gensalt(rounds=_DEFAULT_ROUNDS)
    return bcrypt.hashpw(_prepare(plain_password), salted).decode("ascii")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if ``plain_password`` matches ``password_hash``.

    Never raises on invalid input — returns False. This keeps callers
    simple (a single boolean check) and avoids leaking structural info
    about what was wrong with the attempt.
    """
    if not plain_password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(_prepare(plain_password), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        # bcrypt raises on malformed hashes; treat as failure.
        return False


__all__ = ["hash_password", "verify_password"]

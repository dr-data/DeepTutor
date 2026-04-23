"""User store for DeepTutor school deployments.

A small, purpose-built data access layer over the ``users`` and ``schools``
tables created by migration 0002. It intentionally uses raw SQL through
SQLAlchemy's core API (matching the existing ``sqlite_store.py`` style)
rather than pulling in the ORM — this keeps the auth module light and
portable across SQLite and PostgreSQL.

The store exposes just the operations the auth flow needs today:

- :meth:`UserStore.create_school`
- :meth:`UserStore.create_user`
- :meth:`UserStore.get_user_by_email`
- :meth:`UserStore.get_user_by_id`
- :meth:`UserStore.authenticate`
- :meth:`UserStore.touch_last_login`

Higher-level flows (classroom creation, invites, enrollment) will layer
on top of this in later sprints without needing to change the store.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from deeptutor.auth.passwords import hash_password, verify_password
from deeptutor.auth.roles import Role
from deeptutor.db.url import resolve_database_url


@dataclass(frozen=True)
class UserRecord:
    """Public view of a user row. Never exposes the password hash."""

    id: str
    school_id: str
    email: str
    display_name: str
    role: str
    status: str
    last_login_at: float | None
    created_at: float
    updated_at: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "school_id": self.school_id,
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role,
            "status": self.status,
            "last_login_at": self.last_login_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _new_id(prefix: str) -> str:
    """Generate a human-scannable id like ``usr_7ab91c3d4f``."""
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class UserStore:
    """Thin wrapper over the schools/users tables.

    Instances are cheap to create and hold a SQLAlchemy engine. Use
    :meth:`from_env` to get the default store backed by the URL resolved
    from environment variables.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @classmethod
    def from_env(cls) -> "UserStore":
        """Return a store connected to the URL resolved from the environment."""
        url = resolve_database_url()
        engine = create_engine(url, future=True)
        return cls(engine)

    # ------------------------------------------------------------------
    # schools
    # ------------------------------------------------------------------
    def create_school(
        self,
        *,
        name: str,
        slug: str,
        timezone: str = "UTC",
        locale: str = "en",
    ) -> str:
        """Create a new school tenant and return its id."""
        if not name or not slug:
            raise ValueError("School name and slug are required")
        school_id = _new_id("sch")
        now = time.time()
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO schools
                        (id, name, slug, timezone, locale, settings_json,
                         created_at, updated_at)
                    VALUES (:id, :name, :slug, :timezone, :locale, '{}',
                            :created_at, :updated_at)
                    """
                ),
                {
                    "id": school_id,
                    "name": name,
                    "slug": slug,
                    "timezone": timezone,
                    "locale": locale,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return school_id

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    def create_user(
        self,
        *,
        school_id: str,
        email: str,
        display_name: str,
        role: str | Role,
        password: str,
    ) -> UserRecord:
        """Create a new user with a hashed password and return the record."""
        if not school_id or not email or not display_name or not password:
            raise ValueError("school_id, email, display_name and password are required")
        # Validate role via enum — raises ValueError on typos.
        resolved_role = Role(role) if isinstance(role, str) else role

        user_id = _new_id("usr")
        now = time.time()
        password_hash = hash_password(password)
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO users
                        (id, school_id, email, display_name, role,
                         password_hash, status, created_at, updated_at)
                    VALUES (:id, :school_id, :email, :display_name, :role,
                            :password_hash, 'active', :created_at, :updated_at)
                    """
                ),
                {
                    "id": user_id,
                    "school_id": school_id,
                    "email": email.strip().lower(),
                    "display_name": display_name.strip(),
                    "role": resolved_role.value,
                    "password_hash": password_hash,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return UserRecord(
            id=user_id,
            school_id=school_id,
            email=email.strip().lower(),
            display_name=display_name.strip(),
            role=resolved_role.value,
            status="active",
            last_login_at=None,
            created_at=now,
            updated_at=now,
        )

    def get_user_by_email(self, school_id: str, email: str) -> UserRecord | None:
        """Return the user with ``email`` within ``school_id`` or None."""
        with self._engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, school_id, email, display_name, role, status,
                           last_login_at, created_at, updated_at
                    FROM users
                    WHERE school_id = :school_id AND email = :email
                    """
                ),
                {"school_id": school_id, "email": email.strip().lower()},
            ).mappings().first()
        return self._row_to_record(row) if row else None

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        """Return the user with ``user_id`` or None."""
        with self._engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, school_id, email, display_name, role, status,
                           last_login_at, created_at, updated_at
                    FROM users
                    WHERE id = :user_id
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()
        return self._row_to_record(row) if row else None

    def authenticate(
        self,
        *,
        school_id: str,
        email: str,
        password: str,
    ) -> UserRecord | None:
        """Return the user if credentials match, else None.

        Deliberately uses constant-time bcrypt comparison and does not
        differentiate between "user not found" and "wrong password" — both
        return None so attackers cannot enumerate accounts.
        """
        # Look up the full row including the hash — we need it locally,
        # but never return it to callers.
        with self._engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, school_id, email, display_name, role, status,
                           password_hash, last_login_at, created_at, updated_at
                    FROM users
                    WHERE school_id = :school_id AND email = :email
                    """
                ),
                {"school_id": school_id, "email": email.strip().lower()},
            ).mappings().first()
        if row is None:
            # Still run verify_password against a dummy hash to avoid a
            # timing side-channel. bcrypt hashes all take ~100ms to check.
            verify_password(password, "$2b$12$" + "x" * 53)
            return None
        if row["status"] != "active":
            return None
        if not verify_password(password, row["password_hash"]):
            return None
        return self._row_to_record(row)

    def touch_last_login(self, user_id: str) -> None:
        """Update ``last_login_at`` to the current time."""
        now = time.time()
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE users
                    SET last_login_at = :now, updated_at = :now
                    WHERE id = :user_id
                    """
                ),
                {"now": now, "user_id": user_id},
            )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_record(row: Any) -> UserRecord:
        return UserRecord(
            id=row["id"],
            school_id=row["school_id"],
            email=row["email"],
            display_name=row["display_name"],
            role=row["role"],
            status=row["status"],
            last_login_at=row["last_login_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


__all__ = ["UserRecord", "UserStore"]

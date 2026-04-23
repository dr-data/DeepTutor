"""JWT encode/decode helpers for DeepTutor.

Tokens carry the minimum claims needed for RBAC:

- ``sub``         — the user id (primary key of ``users.id``)
- ``school_id``   — the tenant the user belongs to
- ``role``        — one of :class:`deeptutor.auth.roles.Role`
- ``exp``         — standard expiry (unix timestamp)
- ``iat``         — issued-at (unix timestamp)

The signing secret comes from the ``DEEPTUTOR_JWT_SECRET`` environment
variable. If it is unset we fall back to a process-local random secret
— which is fine for tests but emits a warning in logs so operators know
they need to set it in production. Never commit a default secret to git.

Implementation note: we implement HS256 directly using stdlib ``hmac`` +
``hashlib`` + ``base64`` to avoid depending on heavy JWT libraries. This
keeps the offline footprint small and removes one package that could
break during school updates. Only HS256 is supported — asymmetric
algorithms are unnecessary for a single-tenant school deployment.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import logging
import os
import secrets
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_ALGORITHM = "HS256"
DEFAULT_TTL_MINUTES = 60 * 12  # 12 hours — a typical school day + commute.

_fallback_secret: str | None = None


def _b64url_encode(data: bytes) -> str:
    """URL-safe base64 encode without padding (per JWT spec)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    """URL-safe base64 decode, re-adding padding as needed."""
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(message: bytes, secret: str) -> bytes:
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()


@dataclass(frozen=True)
class TokenClaims:
    """Decoded token payload returned by :func:`decode_access_token`."""

    user_id: str
    school_id: str
    role: str
    expires_at: datetime
    issued_at: datetime


def _get_secret() -> str:
    """Return the JWT signing secret, warning if using a fallback."""
    secret = os.environ.get("DEEPTUTOR_JWT_SECRET")
    if secret:
        return secret

    global _fallback_secret
    if _fallback_secret is None:
        _fallback_secret = secrets.token_urlsafe(48)
        logger.warning(
            "DEEPTUTOR_JWT_SECRET is not set — using a random per-process secret. "
            "Tokens will be invalidated on restart. Set DEEPTUTOR_JWT_SECRET in "
            "production to persist sessions."
        )
    return _fallback_secret


def create_access_token(
    *,
    user_id: str,
    school_id: str,
    role: str,
    ttl_minutes: int = DEFAULT_TTL_MINUTES,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Mint a signed JWT for the given user.

    Args:
        user_id: Primary key of the user record.
        school_id: Tenant identifier for RBAC scoping.
        role: One of ``admin``/``teacher``/``student``.
        ttl_minutes: Token lifetime in minutes.
        extra_claims: Optional dict of additional claims to embed
            (e.g. display name for UI rendering). Do not put secrets here.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=ttl_minutes)
    payload: dict[str, Any] = {
        "sub": user_id,
        "school_id": school_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        # Never let extra_claims override reserved fields.
        for key in ("sub", "school_id", "role", "iat", "exp"):
            extra_claims.pop(key, None)
        payload.update(extra_claims)

    header = {"alg": DEFAULT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_b64 = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = _sign(signing_input, _get_secret())
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> TokenClaims:
    """Verify ``token`` and return its claims.

    Raises:
        ValueError: If the token is expired, malformed, or fails signature
            verification. Callers should map this to HTTP 401.
    """
    if not isinstance(token, str) or token.count(".") != 2:
        raise ValueError("Invalid access token")

    header_b64, payload_b64, signature_b64 = token.split(".")

    # Verify signature with constant-time comparison.
    try:
        expected_sig = _sign(
            f"{header_b64}.{payload_b64}".encode("ascii"),
            _get_secret(),
        )
        provided_sig = _b64url_decode(signature_b64)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid access token") from exc
    if not hmac.compare_digest(expected_sig, provided_sig):
        raise ValueError("Invalid access token")

    # Parse header — reject anything that isn't our expected HS256.
    try:
        header = json.loads(_b64url_decode(header_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid access token header") from exc
    if header.get("alg") != DEFAULT_ALGORITHM:
        raise ValueError("Unsupported token algorithm")

    # Parse payload.
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid access token payload") from exc

    try:
        user_id = str(payload["sub"])
        school_id = str(payload["school_id"])
        role = str(payload["role"])
        exp_ts = int(payload["exp"])
        iat_ts = int(payload["iat"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Access token is missing required claims") from exc

    expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    issued_at = datetime.fromtimestamp(iat_ts, tz=timezone.utc)
    if datetime.now(tz=timezone.utc) >= expires_at:
        raise ValueError("Access token has expired")

    return TokenClaims(
        user_id=user_id,
        school_id=school_id,
        role=role,
        expires_at=expires_at,
        issued_at=issued_at,
    )


__all__ = ["TokenClaims", "create_access_token", "decode_access_token"]

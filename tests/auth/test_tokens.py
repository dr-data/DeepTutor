"""Tests for :mod:`deeptutor.auth.tokens`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from deeptutor.auth.tokens import create_access_token, decode_access_token


def test_round_trip_encodes_and_decodes_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "test-secret")
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="teacher",
    )
    claims = decode_access_token(token)
    assert claims.user_id == "usr_abc"
    assert claims.school_id == "sch_xyz"
    assert claims.role == "teacher"
    assert claims.expires_at > claims.issued_at


def test_expired_token_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "test-secret")
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="student",
        ttl_minutes=-1,
    )
    with pytest.raises(ValueError, match="expired"):
        decode_access_token(token)


def test_tampered_token_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "test-secret")
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="student",
    )
    # Flip a character in the middle of the signature section.
    parts = token.split(".")
    assert len(parts) == 3
    tampered_sig = parts[2][:-1] + ("A" if parts[2][-1] != "A" else "B")
    tampered = ".".join([parts[0], parts[1], tampered_sig])
    with pytest.raises(ValueError):
        decode_access_token(tampered)


def test_different_secret_rejects_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "secret-one")
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="student",
    )
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "secret-two")
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_extra_claims_do_not_override_reserved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "test-secret")
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="student",
        extra_claims={"role": "admin", "display_name": "Alice"},
    )
    claims = decode_access_token(token)
    # "role" must not have been overridden by extra_claims.
    assert claims.role == "student"


def test_ttl_minutes_is_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_JWT_SECRET", "test-secret")
    before = datetime.now(tz=timezone.utc)
    token = create_access_token(
        user_id="usr_abc",
        school_id="sch_xyz",
        role="student",
        ttl_minutes=30,
    )
    claims = decode_access_token(token)
    # Allow a small clock skew window.
    expected = before + timedelta(minutes=30)
    assert abs((claims.expires_at - expected).total_seconds()) < 5

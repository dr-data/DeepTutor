"""Tests for :mod:`deeptutor.auth.passwords`."""

from __future__ import annotations

import pytest

from deeptutor.auth.passwords import hash_password, verify_password


def test_hash_password_produces_verifiable_hash() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed)


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("secret")
    assert not verify_password("wrong", hashed)


def test_verify_password_handles_empty_inputs() -> None:
    hashed = hash_password("secret")
    assert not verify_password("", hashed)
    assert not verify_password("secret", "")
    assert not verify_password("", "")


def test_verify_password_rejects_malformed_hash() -> None:
    assert not verify_password("secret", "not-a-real-hash")


def test_hash_password_rejects_empty_input() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_two_hashes_of_same_password_differ() -> None:
    # bcrypt uses a random salt, so two hashes of the same password should differ.
    a = hash_password("same")
    b = hash_password("same")
    assert a != b
    assert verify_password("same", a)
    assert verify_password("same", b)

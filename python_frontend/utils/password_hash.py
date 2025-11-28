"""
Custom password hashing utilities using a deterministic double-hashing scheme.

This module implements two lightweight non-cryptographic hash functions (djb2
and fnv1a) and combines them in a double-hashing style to produce a stable
password digest. It also provides a small salt generator and a verify helper.

WARNING: Custom password hashing schemes are usually NOT recommended for
production. Prefer `werkzeug.security.generate_password_hash` (PBKDF2)
or `bcrypt`/`argon2` instead. This implementation follows the user's request
to demonstrate double hashing and load-factor concepts.
"""
import os
import binascii
from typing import Tuple


def generate_salt(length: int = 16) -> str:
    """Generate a random hex salt."""
    return binascii.hexlify(os.urandom(length)).decode('ascii')


def djb2(data: bytes) -> int:
    """DJB2 hash (deterministic) returning a non-negative integer."""
    h = 5381
    for b in data:
        h = ((h << 5) + h) + b  # h * 33 + b
        h &= 0xFFFFFFFFFFFFFFFF
    return h


def fnv1a(data: bytes) -> int:
    """FNV-1a 64-bit hash (deterministic) returning a non-negative integer."""
    h = 0xcbf29ce484222325
    for b in data:
        h ^= b
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


def double_hash_digest(password: str, salt: str, rounds: int = 1000) -> str:
    """Produce a deterministic hex digest using repeated double-hashing.

    The algorithm:
    - Start with bytes = (password + salt).encode('utf-8')
    - For `rounds` iterations:
        h1 = djb2(bytes)
        h2 = fnv1a(bytes)
        combined = (h1 << 64) ^ h2
        bytes = combined.to_bytes(16, 'big', signed=False)
    - Return hex string of final bytes
    """
    if rounds < 1:
        rounds = 1

    b = (password + salt).encode('utf-8')
    for _ in range(rounds):
        h1 = djb2(b)
        h2 = fnv1a(b)
        combined = ((h1 & 0xFFFFFFFFFFFFFFFF) << 64) ^ (h2 & 0xFFFFFFFFFFFFFFFF)
        b = combined.to_bytes(16, 'big', signed=False)

    return binascii.hexlify(b).decode('ascii')


def hash_password(password: str, rounds: int = 1000) -> Tuple[str, str]:
    """Generate (salt, digest) pair for a password.

    Returns salt and the hex digest. The caller can store `salt$digest`.
    """
    salt = generate_salt()
    digest = double_hash_digest(password, salt, rounds=rounds)
    return salt, digest


def verify_password(password: str, salt: str, digest: str, rounds: int = 1000) -> bool:
    """Verify `password` against `salt` and `digest` using the same rounds."""
    calc = double_hash_digest(password, salt, rounds=rounds)
    return calc == digest

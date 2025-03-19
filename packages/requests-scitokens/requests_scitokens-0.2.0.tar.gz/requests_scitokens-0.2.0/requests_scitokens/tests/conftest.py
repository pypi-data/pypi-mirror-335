# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Test configuration for `requests-scitokens`."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

import pytest

from scitokens import SciToken


# -- old pytest fixtures --------------

if pytest.__version__ < "3.9.0":  # RL8
    from pathlib import Path
    from tempfile import TemporaryDirectory

    @pytest.fixture
    def tmp_path():
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)


# -- SciTokens fixtures ---------------

ISSUER = "local"
_SCOPE_PATH = "/igwn_auth_utils"
READ_AUDIENCE = "igwn_auth_utils"
READ_SCOPE = "read:{}".format(_SCOPE_PATH)
WRITE_AUDIENCE = "igwn_auth_utils2"
WRITE_SCOPE = "write:{}".format(_SCOPE_PATH)


@pytest.fixture(scope="session")  # one per suite is fine
def private_key():
    """Generate a private RSA key with which to sign a token."""
    return generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )


@pytest.fixture(scope="session")
def public_key(private_key):
    """The public key for the private_key."""
    return private_key.public_key()


@pytest.fixture(scope="session")
def public_pem(public_key):
    """The public_key in PEM format."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _create_token(
    key=None,
    iss=ISSUER,
    aud=READ_AUDIENCE,
    scope=READ_SCOPE,
    **kwargs
):
    """Create a token."""
    if key:
        from scitokens.utils.keycache import KeyCache
        keycache = KeyCache.getinstance()
        keycache.addkeyinfo(iss, "test_key", key.public_key())
    now = int(time.time())
    token = SciToken(key=key, key_id="test_key")
    token.update_claims({
        "iat": now,
        "nbf": now,
        "exp": now + 86400,
        "iss": iss,
        "aud": aud,
        "scope": scope,
    })
    token.update_claims(kwargs)
    return token


def _write_token(token, path):
    """Write a token to a file."""
    with open(path, "wb") as file:
        file.write(token.serialize(lifetime=86400))


@pytest.fixture
def rtoken(private_key):
    """A token with the ``READ_SCOPE``."""
    return _create_token(
        key=private_key,
        scope=READ_SCOPE,
    )


@pytest.fixture
def wtoken(private_key):
    """A token with the ``WRITE_SCOPE``."""
    return _create_token(
        key=private_key,
        aud=WRITE_AUDIENCE,
        scope=WRITE_SCOPE,
    )


@pytest.fixture
def rtoken_path(rtoken, tmp_path):
    """The path of a file containing the serialised ``READ_SCOPE`` token."""
    token_path = tmp_path / "token.use"
    _write_token(rtoken, token_path)
    return token_path

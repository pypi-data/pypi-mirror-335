# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Tests for `requests_scitokens.auth`."""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

import os
from unittest import mock

import requests
from scitokens import SciToken

from requests_scitokens import auth
from requests_scitokens.utils import serialize_token

# -- mock helpers ---------------------

deserialize = SciToken.deserialize


def _insecure_deserialize_factory(key):
    """Generate an insecure version of SciToken.deserialize.

    Hardcodes ``insecure=True, public_key={key}``.
    """
    def _insecure_deserialize(
        tokenstr,
        audience,
        require_key,
        insecure,  # noqa: ARG001
        public_key,  # noqa: ARG001
    ):
        return deserialize(
            tokenstr,
            audience,
            require_key,
            insecure=True,
            public_key=key,
        )
    return _insecure_deserialize


def _token_response(request, context):
    """Text response based on whether a token was received or not."""
    if request.headers.get("Authorization", "").startswith("Bearer"):
        context.status_code = 200
        return "Success"
    context.status_code = 401
    return "Unauthorized"


def assert_tokens_equal(a, b):
    """Assert that two `SciToken` objects are equal."""
    assert dict(a.claims()) == dict(b.claims())


class TestHTTPSciTokenAuth:
    """Test `HTTPSciTokenAuth."""

    Auth = auth.HTTPSciTokenAuth

    def test_init(self):
        """Test initialisation."""
        auth = self.Auth()
        assert auth.token is None
        assert auth.audience is None

    def test_eq(self):
        """Test `__eq__`."""
        a = self.Auth(token=None, audience="ANY")
        b = self.Auth(token=None, audience="ANY")
        assert a == b

    def test_neq(self):
        """Test `__ne__`."""
        a = self.Auth(token=None, audience="ANY")
        b = self.Auth(token=None, audience="https://example.com")
        assert a != b

    @mock.patch("requests_scitokens.auth.SciToken.discover")
    def test_token_header_empty(self, find_token):
        """Test handling of no token."""
        find_token.return_value = None
        req = requests.Request()
        auth = self.Auth()
        assert auth(req).headers.get("Authorization") is None

    def test_token_header(self, rtoken):
        """Test token serialisation."""
        auth = self.Auth(token=rtoken)
        req = requests.Request()
        assert auth(req).headers["Authorization"] == (
            f"Bearer {serialize_token(rtoken)}"
        )

    @mock.patch.dict(os.environ)
    def test_find_token(self, rtoken, rtoken_path, public_pem):
        """Test `find_token`."""
        os.environ["BEARER_TOKEN_FILE"] = str(rtoken_path)
        auth = self.Auth()
        token = auth.find_token(insecure=True, public_key=public_pem)
        assert_tokens_equal(token, rtoken)

    def test_handle_401_no_challenge(self, requests_mock):
        """Test handling of 401 responses with no challenge."""
        # mock a request that doesn't respond with a Bearer challenge
        # in the WWW-Authenticate header
        requests_mock.get(
            "https://example.com/",
            status_code=401,
            text="Access denied",
        )
        # and check that we propagate the response
        resp = requests.get(
            "https://example.com",
            auth=self.Auth(),
            timeout=10,
        )
        assert resp.status_code == 401
        assert resp.text == "Access denied"

    @mock.patch.dict(os.environ)
    def test_handle_401_challenge(self, rtoken, public_pem, requests_mock):
        """Test handling of 401 responses with a challenge."""
        os.environ["BEARER_TOKEN"] = serialize_token(rtoken)
        requests_mock.get(
            "https://example.com/",
            [
                # initial response issues bearer challenge
                {
                    "status_code": 401,
                    "headers": {"WWW-Authenticate": "Bearer"},
                },
                # second response should pass if token was received
                {"text": _token_response},
            ],
        )
        with mock.patch(
            "requests_scitokens.auth.SciToken.deserialize",
            _insecure_deserialize_factory(public_pem),
        ):
            assert requests.get(
                "https://example.com",
                auth=self.Auth(),
                timeout=10,
            ).status_code == 200

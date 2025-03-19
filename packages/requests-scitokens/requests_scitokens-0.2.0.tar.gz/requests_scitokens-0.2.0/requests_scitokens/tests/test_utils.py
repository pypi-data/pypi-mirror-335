# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Tests for `requests_scitokens.utils`."""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

import pytest

from requests_scitokens import utils as rsutils


@pytest.mark.parametrize(("url", "kwargs", "aud"), [
    pytest.param(
        "https://example.com/data",
        {},
        "https://example.com",
        id="basic",
    ),
    pytest.param(
        "example.com",
        {},
        "https://example.com",
        id="default scheme",
    ),
    pytest.param(
        "https://example.com:443/data/test",
        {},
        "https://example.com",
        id="port",
    ),
    pytest.param(
        "http://example.com:443/data/test",
        {},
        "http://example.com",
        id="non-default scheme",
    ),
    pytest.param(
        "example.com:443/data/test",
        {"scheme": "xroot"},
        "xroot://example.com",
        id="keyword scheme",
    ),
])
def test_default_audience(url, kwargs, aud):
    """Test `default_audience()`."""
    assert rsutils.default_audience(url, **kwargs) == aud

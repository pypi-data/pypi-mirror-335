# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""SciToken plugin for Requests.

Overview
========

This package provides a custom `HTTPSciTokenAuth` object that will handle
discovering a `~scitokens.SciToken` and attaching a serialisation of the token
to a request in the ``Authorization`` header.

The `HTTPSciTokenAuth` object will also dynamically handle 401 Unauthorized
response that include a ``WWW-Authenticate`` header with a ``Bearer`` challenge.

`requests_scitokens` includes wrapped versions of the standard `requests.api`
methods to simplify performing token-aware requests, for example:

>>> from requests_scitokens import get
>>> get('https://secure.example.com/')

To explicitly pass a `~scitokens.SciToken` into a request, use the ``token``
keyword:

>>> import scitokens
>>> token = scitokens.SciToken.deserialize(...)
>>> get("https://secure.example.com", token=token)
"""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

from .auth import HTTPSciTokenAuth
from .requests import (
    delete,
    get,
    head,
    patch,
    post,
    put,
)
from .sessions import (
    Session,
    SessionMixin,
)

try:
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = "dev"

# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Session API for requests-scitokens."""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

import requests

from requests_scitokens.auth import HTTPSciTokenAuth


class SessionMixin:
    """`requests.Session` mixin class to default to `HTTPSciTokenAuth`."""

    def __init__(
        self,
        *args,
        auth=None,
        token=None,
        **kwargs,
    ):
        """Create a new `Session` with defaut token auth."""
        if auth is None:
            auth = HTTPSciTokenAuth(token=token)
        super().__init__(*args, auth=auth, **kwargs)


class Session(SessionMixin, requests.Session):
    """`requests.Session` with `HTTPSciTokenAuth` enabled by default."""

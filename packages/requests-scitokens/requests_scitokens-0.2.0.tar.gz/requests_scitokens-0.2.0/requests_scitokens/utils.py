# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Utilities for requests_scitokens."""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

from requests import __version__ as requests_version
from requests.utils import prepend_scheme_if_needed
from urllib3.util import parse_url

REQUESTS_PREPEND_SCHEME_BROKEN = requests_version < "2.27.0"


def default_audience(url, scheme="https"):
    """Return the expected ``aud`` claim to authorize a request to ``url``.

    Parameters
    ----------
    url : `str`
        The URL that will be requested.

    scheme: `str`, optional
        The default URL scheme to apply.

    Returns
    -------
    audience : `str`
        The audience values (`str`) expected for ``url``.

    Examples
    --------
    >>> default_audience(
    ...     "https://storage.example.com:1095//my/data.dat",
    ... )
    'https://storage.example.com'

    Hostnames given without a URL scheme have the ``scheme`` keyword
    prepended to the audience URI.

    >>> default_audience("storage.example.com")
    'https://storage.example.com'
    """
    if REQUESTS_PREPEND_SCHEME_BROKEN and "://" not in url:
        url = f"//{url}"
    else:
        url = prepend_scheme_if_needed(url, scheme)
    parsed = parse_url(prepend_scheme_if_needed(url, scheme))
    return f"{parsed.scheme}://{parsed.hostname}"


def serialize_token(token):
    """Serialise a `~scitokens.SciToken`.

    If ``token`` was parsed from a serialisation, the same serialisation
    will be returned, otherwise the :meth:`~scitokens.SciToken.serialize`
    method of ``token`` will be called.
    """
    return (
        token._serialized_token
        or token.serialize().decode("utf-8")
    )

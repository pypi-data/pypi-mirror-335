# Copyright (C) 2024-2025 Cardiff University
# SPDX-License-Identifier: Apache-2.0

"""Request API for requests-scitokens."""

__author__ = "Duncan Macleod <macleoddm@cardiff.ac.uk>"

from functools import wraps

import requests.api

from requests_scitokens.auth import HTTPSciTokenAuth
from requests_scitokens.utils import default_audience


@wraps(requests.api.request)
def request(
    method,
    url,
    *args,
    auth=None,
    session=None,
    **kwargs,
):
    """Send a SciToken-aware request.

    Parameters
    ----------
    method : `str`
        The method to use.

    url : `str`,
        The URL to request.

    auth : `requests.auth.AuthBase`, `tuple`, optional
        The auth handler to use for this request.
        By default a `requests_scitokens.HTTPSciTokenAuth` handler
        will be attached.

    session : `requests.Session`, optional
        The connection session to use, if not given one will be
        created on-the-fly.

    args, kwargs
        All other keyword arguments are passed directly to
        `requests.Session.request`

    Returns
    -------
    resp : `requests.Response`
        The response object.

    See Also
    --------
    requests.Session.request
        For information on how the request is performed.
    """
    if auth is None:
        auth = HTTPSciTokenAuth(
            token=kwargs.pop("token"),
            audience=kwargs.pop("audience", default_audience(url)),
        )

    if not session:  # use module
        session = requests
    return session.request(method, url, *args, auth=auth, **kwargs)


def _request_wrapper_factory(method):
    """Wrap a :mod:`requests` method to use `requests_scitokens.request`.

    Parameters
    ----------
    method : `str`
        The HTTP method to wrap.

    Returns
    -------
    func : `callable`
        A new method wrapping around the equivalent `requests` method
        but using `requests_scitokens.HTTPSciTokenAuth` by default.
    """
    @wraps(getattr(requests.api, method))
    def _request_wrapper(url, *args, session=None, **kwargs):
        return request(method, url, *args, session=session, **kwargs)

    return _request_wrapper


# request methods
delete = _request_wrapper_factory("delete")
get = _request_wrapper_factory("get")
head = _request_wrapper_factory("head")
patch = _request_wrapper_factory("patch")
post = _request_wrapper_factory("post")
put = _request_wrapper_factory("put")

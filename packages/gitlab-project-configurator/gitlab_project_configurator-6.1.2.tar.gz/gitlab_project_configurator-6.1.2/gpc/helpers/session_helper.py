# Copyright (c) 2022 and later Renault S.A.S.
# Developed by Renault S.A.S. and affiliates which hold all
# intellectual property rights. Use of this software is subject
# to a specific license granted by RENAULT S.A.S.

# Standard Library
import logging

# Third Party Libraries
import requests

from requests.adapters import HTTPAdapter
from urllib3 import Retry


log = logging.getLogger(__name__)


def create_retry_request_session():
    """Create an Request Session with retry strategy.

    An exponential retry strategy is executed on network connectivity
    or gateway errors.

    Returns:
        An instance of a request Session.
    """
    HTTP_CODE_TOO_MANY_REQUESTS = 429
    HTTP_CODE_INTERNAL_SERVER_ERROR = 500
    HTTP_CODE_BAD_GATEWAY = 502
    HTTP_CODE_SERVICE_UNAVAILABLE = 503
    HTTP_CODE_GATEWAY_TIMEOUT = 504
    adapter = HTTPAdapter(
        max_retries=Retry(
            total=4,
            backoff_factor=1,
            allowed_methods=None,
            status_forcelist=[
                HTTP_CODE_TOO_MANY_REQUESTS,
                HTTP_CODE_INTERNAL_SERVER_ERROR,
                HTTP_CODE_BAD_GATEWAY,
                HTTP_CODE_SERVICE_UNAVAILABLE,
                HTTP_CODE_GATEWAY_TIMEOUT,
            ],
        )
    )
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

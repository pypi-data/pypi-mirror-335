import os
from typing import Optional

import urllib3
from dasl_api import ApiClient, Configuration

from dasl_client.conn.user_agent import get_user_agent


def get_base_conn(enable_retries: bool = True, host: Optional[str] = None) -> ApiClient:
    """
    Get the base conn for the API.
    TODO: update the default address with our hosted system when it exists.

    :param enable_retries: If True, retry gateway, DNS, and general connection
                           errors up to 5 times before failing.
    :param host: an optional DASL host address to connect to. Will use the
                 default address if not supplied.
    :return: An API conn without any auth
    """
    if host is None:
        host = os.getenv("DASL_API_URL", "https://api.prod.sl.antimatter.io")
    config = Configuration(host=host)
    if enable_retries:
        # configure retries with backup for all HTTP verbs; we do not limit this to only
        # idempotent verbs as the subset of retries we allow indicates the API was never
        # reached
        config.retries = urllib3.Retry(
            total=5,
            backoff_factor=0.1,
            allowed_methods=None,
            status_forcelist=[502, 503],
        )
    _api_client = ApiClient(configuration=config)
    _api_client.user_agent = get_user_agent()
    return _api_client

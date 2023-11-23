import logging

import httpx

from neetbox.utils.mvc import Singleton

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.ERROR)

__no_proxy = {
    "http://": None,
    "https://": None,
}


def __load_http_client():
    __local_http_client = httpx.Client(proxies=__no_proxy)  # type: ignore
    return __local_http_client


# singleton
_local_http_client: httpx.Client = __load_http_client()


class Connection(metaclass=Singleton):
    _http_client: httpx.Client

    # _websocket_client
    def __init__(self, cfg) -> None:
        pass

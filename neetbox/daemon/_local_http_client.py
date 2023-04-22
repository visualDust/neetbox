import httpx

__no_proxy = {
    "http://": None,
    "https://": None,
}


def __load_http_client():
    __local_http_client = httpx.Client(proxies=__no_proxy)
    return __local_http_client


_local_http_client: httpx.Client = __load_http_client()

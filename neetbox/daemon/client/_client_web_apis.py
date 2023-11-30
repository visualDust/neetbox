# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox.daemon._protocol import *
from neetbox.daemon.client._client import connection


def _get(url):
    r = connection.http.get(url)
    _data = r.json()
    return _data


def _post(url, data=None):
    r = connection.http.post(url, json=data)
    return r


def get_list(base_addr):
    api_addr = f"{base_addr}{FRONTEND_API_ROOT}/list"
    return _get(api_addr)


def get_status_of(base_addr, name):
    api_addr = f"{base_addr}{FRONTEND_API_ROOT}/status/{name}"
    return _get(api_addr)


def shutdown(base_addr):
    api_addr = f"{base_addr}{FRONTEND_API_ROOT}/shutdown"
    return _post(api_addr)

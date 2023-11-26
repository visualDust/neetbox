# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox.config import get_module_level_config
from neetbox.daemon._protocol import *
from neetbox.daemon.client._client import connection


def get_base_addr():
    __cfg = get_module_level_config()
    daemon_address = f"{__cfg['host']}:{__cfg['port']}"
    return f"http://{daemon_address}/"


def _fetch(url):
    r = connection.http.get(url)
    _data = r.json()
    return _data


def get_list():
    api_addr = f"{get_base_addr()}{FRONTEND_API_ROOT}/list"
    return _fetch(api_addr)


def get_status_of(name):
    api_addr = f"{get_base_addr()}{FRONTEND_API_ROOT}/status/{name}"
    return _fetch(api_addr)

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


def get_status_of(base_addr, workspace_id):
    id2name = get_list(base_addr)
    name2id = {v: k for k, v in id2name}  # todo resolve dup name
    if workspace_id not in name2id:
        return None
    _id = name2id[workspace_id]
    api_addr = f"{base_addr}{FRONTEND_API_ROOT}/status/{_id}"
    return _get(api_addr)


def shutdown(base_addr):
    api_addr = f"{base_addr}{FRONTEND_API_ROOT}/shutdown"
    return _post(api_addr)

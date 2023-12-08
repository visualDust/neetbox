# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection


def _get(api):
    r = connection.get(api=api)
    _data = r.json()
    return _data


def _post(api, data=None):
    r = connection.post(api=api, json=data)
    return r


def get_list():
    api = f"{FRONTEND_API_ROOT}/list"
    return _get(api)


def get_status_of(project_id):
    id2name = get_list()
    name2id = {v: k for k, v in id2name}  # todo resolve dup name
    if project_id not in name2id:
        return None
    _id = name2id[project_id]
    api = f"{FRONTEND_API_ROOT}/status/{_id}"
    return _get(api)


def shutdown():
    api = "/shutdown"
    return _post(api)

# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection


def _get(api, root=None):
    r = connection.get(api=api, root=root)
    _data = r.json()
    return _data


def _post(api, root=None, data=None):
    r = connection.post(api=api, root=root, json=data)
    return r


def get_list(root=None):
    api = f"{FRONTEND_API_ROOT}/list"
    return _get(api, root=root)


def get_status_of(project_id, root=None):
    id2name = get_list(root=root)
    name2id = {v: k for k, v in id2name}  # todo resolve dup name
    if project_id not in name2id:
        return None
    _id = name2id[project_id]
    api = f"{FRONTEND_API_ROOT}/status/{_id}"
    return _get(api)


def shutdown(root=None):
    api = "/shutdown"
    return _post(api, root=root)

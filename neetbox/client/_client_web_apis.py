# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230414


from neetbox._protocol import *

from ._client import connection


def _get(api, root=None):
    r = connection.get(api=api, root=root)
    _data = r.json()
    return _data


def _post(api, root=None, data=None):
    r = connection.post(api=api, root=root, json=data)
    return r


def shutdown(root=None):
    api = f"{API_ROOT}/{SERVER_KEY}/shutdown"
    return _post(api, root=root)

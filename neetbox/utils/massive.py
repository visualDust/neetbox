# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231216

import collections
import functools
import os
import socket
import struct
from concurrent.futures import ThreadPoolExecutor
from typing import Union

_ThreadPoolExecutor = ThreadPoolExecutor()


def is_loopback(host):
    loopback_checker = {
        socket.AF_INET: lambda x: struct.unpack("!I", socket.inet_aton(x))[0] >> (32 - 8) == 127,
        socket.AF_INET6: lambda x: x == "::1",
    }
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            r = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
        except socket.gaierror:
            return False
        for family, _, _, _, sockaddr in r:
            if not loopback_checker[family](sockaddr[0]):
                return False
    return True


def nonblocking(func):
    @functools.wraps(func)
    def _use_thread_pool(*args, **kwargs):
        try:
            return _ThreadPoolExecutor.submit(func, *args, **kwargs)  # type: ignore
        except Exception as e:
            raise e

    return _use_thread_pool


def update_dict_recursively(self: dict, the_other: dict):
    for _k, _v in the_other.items():
        if type(_v) is dict:  # currently resolving a dict child
            if _k in self:  # dfs merge
                update_dict_recursively(self=self[_k], the_other=the_other[_k])
            else:
                self[_k] = the_other[_k]
        else:  # not a dict, overwriting
            self[_k] = the_other[_k]


def check_read_toml(path) -> Union[dict, bool]:
    import toml

    if not os.path.isfile(path):  # but config file not exist
        return False
    try:
        return toml.load(path)  # try load as toml
    except Exception as e:
        return False


def describe_object(obj, length_limit=None) -> str:
    if hasattr(obj, "__name__"):
        description = obj.__name__
    elif hasattr(obj, "__class__"):
        description = f"{obj.__class__.__name__} object"
    else:
        description = str(obj)
    if length_limit and len(description) > length_limit:
        description = description[:length_limit] + "..."
    return description

# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

import collections
from neetbox.utils.utils import patch
from multiprocessing import current_process

DEFAULT_CONFIG = {
    "name": None,
    "version": None,
    "logging": {"logdir": None},
    "pipeline": {},
    "integrations": {
        "environment": {
            "gpus": "auto",
        },
        "datasets": [],
    },
    "daemon": {
        "enable": True,
        "displayName": None,
        "server": "localhost",
        "port": 20202,
        "updateInterval": 10,
        "uploadInterval": 10,
        "info": ["log", "status"],
        "allowIpython":False
    },
}
WORKSPACE_CONFIG: dict = DEFAULT_CONFIG.copy()


def update_with(cfg: dict):
    def _update_dict_recursively(self: dict, the_other: dict):
        for _k, _v in the_other.items():
            if type(_v) is dict:  # currently resolving a dict child
                if _k in self:  # dfs merge
                    _update_dict_recursively(self=self[_k], the_other=the_other[_k])
                else:
                    self[_k] = the_other[_k]
            else:  # not a dict, overwriting
                self[_k] = the_other[_k]

    global WORKSPACE_CONFIG
    _update_dict_recursively(WORKSPACE_CONFIG, cfg)


def get_current():
    global WORKSPACE_CONFIG
    return WORKSPACE_CONFIG

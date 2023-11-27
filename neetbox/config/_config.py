# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

DEFAULT_WORKSPACE_CONFIG = {
    "name": None,
    "version": None,
    "logging": {"level": "INFO", "logdir": None},
    "pipeline": {
        "updateInterval": 0.5,
    },
    "integrations": {
        "autoload": True,
        "environment": {"hardware": {"monit": True, "interval": 0.5}, "platform": {"monit": True}},
    },
    "daemon": {
        "enable": True,
        "host": "127.0.0.1",
        "port": 20202,
        "displayName": None,
        "allowIpython": False,
        "mute": True,
        "mode": "detached",
        "uploadInterval": 0.5,
    },
}
WORKSPACE_CONFIG: dict = DEFAULT_WORKSPACE_CONFIG.copy()


def update_workspace_config_with(cfg: dict):
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

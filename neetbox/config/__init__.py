# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413


import inspect

from neetbox.config._config import DEFAULT_WORKSPACE_CONFIG as default
from neetbox.config._config import get_current
from neetbox.utils.framing import get_frame_module_traceback


def get_module_level_config(module=None):
    try:
        module = (
            module or get_frame_module_traceback(traceback=2).__name__  # type: ignore
        )  # try to trace if module not given
        if type(module) is not str:  # try to trace the belonging module of the given object
            module = inspect.getmodule(module).__name__  # type: ignore
    except Exception:
        module = "@"  # faild to trace, returning all configs
    the_config = get_current()
    sub_module_names = module.split(".")
    if len(sub_module_names):
        if sub_module_names[0] == "neetbox":
            # skip 'neetbox'
            sub_module_names.pop(0)
        for sub_module in sub_module_names:
            if sub_module not in the_config:
                return the_config
            the_config = the_config[sub_module]
    return the_config


__all__ = ["get_module_level_config", "default"]

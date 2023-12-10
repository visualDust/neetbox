# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import importlib
import pkgutil

from neetbox.config._workspace import (
    _get_module_level_config as get_module_level_config,
)
from neetbox.core import Registry
from neetbox.utils.framing import get_frame_module_traceback

__QUERY_AFTER_LOAD_WORKSPACE = Registry("__QUERY_AFTER_LOAD_WORKSPACE")
on_workspace_loaded = __QUERY_AFTER_LOAD_WORKSPACE.register


def _scan_sub_modules():
    __THIS_MODULE = get_frame_module_traceback(1)
    for sub_module_info in pkgutil.iter_modules(__THIS_MODULE.__path__):
        importlib.import_module(f"{__THIS_MODULE.__name__}.{sub_module_info.name}")


def _init_extensions():
    """
    DO NOT call before workspace config load
    """
    if not get_module_level_config()["autoload"]:
        return
    for name, fun in __QUERY_AFTER_LOAD_WORKSPACE.items():
        fun()

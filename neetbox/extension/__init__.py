# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import importlib
import pkgutil

from neetbox.config import get_module_level_config
from neetbox.core import Registry
from neetbox.utils.framing import get_frame_module_traceback

_QUERY_BEFORE_LOAD_WORKSPACE = Registry("__QUERY_BEFORE_LOAD_WORKSPACE")
before_workspace_load = _QUERY_BEFORE_LOAD_WORKSPACE.register

_QUERY_AFTER_LOAD_WORKSPACE = Registry("__QUERY_AFTER_LOAD_WORKSPACE")
on_workspace_loaded = _QUERY_AFTER_LOAD_WORKSPACE.register


def _iter_import_sub_modules():
    _THIS_MODULE = get_frame_module_traceback(1)
    for sub_module_info in pkgutil.iter_modules(_THIS_MODULE.__path__):
        importlib.import_module(f"{_THIS_MODULE.__name__}.{sub_module_info.name}")


def _run_things_after_load_workspace() -> None:
    if not get_module_level_config()["autoload"]:
        return
    _iter_import_sub_modules()
    for name, fun in _QUERY_AFTER_LOAD_WORKSPACE.items():
        fun()


def _run_things_before_load_workspace() -> None:
    _iter_import_sub_modules()
    for name, fun in _QUERY_BEFORE_LOAD_WORKSPACE.items():
        fun()

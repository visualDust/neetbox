# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import importlib
import pkgutil

from neetbox.config import get_module_level_config
from neetbox.core import Registry
from neetbox.integrations.engine import Engine as engine
from neetbox.integrations.engine import get_installed_engines, get_supported_engines
from neetbox.utils.framing import get_frame_module_traceback

__all__ = [
    "engine",
    "get_supported_engines",
    "get_installed_engines",
]

_QUERY_AFTER_LOAD_WORKSPACE = Registry("__INTEGRATION_LOADER_DICT")


def _iter_import_sub_modules():
    _THIS_MODULE = get_frame_module_traceback(1)
    for sub_module_info in pkgutil.iter_modules(_THIS_MODULE.__path__):
        importlib.import_module(f"{_THIS_MODULE.__name__}.{sub_module_info.name}")


def _post_init_workspace():
    _cfg = get_module_level_config()
    if not _cfg["autoload"]:
        return  # do not load if auto load is disabled
    _iter_import_sub_modules()
    for name, fun in _QUERY_AFTER_LOAD_WORKSPACE.items():
        fun()


call_on_workspace_load = _QUERY_AFTER_LOAD_WORKSPACE.register
__all__ = ["call_on_workspace_load"]

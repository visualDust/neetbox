# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413


import os
import types
from typing import Union

from ._workspace import _get_module_level_config, export_default_config

__IS_WORKSPACE_LOADED = False


def get_module_level_config(module: Union[str, types.ModuleType] = None):
    global __IS_WORKSPACE_LOADED
    if not __IS_WORKSPACE_LOADED:
        __IS_WORKSPACE_LOADED = True
        from ._workspace import _create_load_workspace

        _create_load_workspace()

    module_config = _get_module_level_config(module, traceback=3)
    return module_config


def get_project_id():
    return get_module_level_config("@")["projectid"]


def get_run_id():
    return get_module_level_config("@")["runid"]


__all__ = ["get_module_level_config", "export_default_config", "get_project_id", "get_run_id"]

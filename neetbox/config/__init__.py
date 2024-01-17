# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230413

import types
from typing import Union

from neetbox._protocol import MACHINE_ID_KEY, PROJECT_ID_KEY, RUN_ID_KEY

from .project import _get_module_level_config, export_default_config
from .user import get as get_user_config

__IS_WORKSPACE_LOADED = False


def get_module_level_config(module: Union[str, types.ModuleType] = None):
    global __IS_WORKSPACE_LOADED
    if not __IS_WORKSPACE_LOADED:
        __IS_WORKSPACE_LOADED = True
        from .project import _create_load_workspace

        _create_load_workspace()

    module_config = _get_module_level_config(module, stack_offset=3)
    return module_config


def get_machine_id():
    return get_user_config(MACHINE_ID_KEY)


def get_project_id():
    return get_module_level_config("@")[PROJECT_ID_KEY]


def get_run_id():
    return get_module_level_config("@")[RUN_ID_KEY]


__all__ = ["get_module_level_config", "export_default_config", "get_project_id", "get_run_id"]

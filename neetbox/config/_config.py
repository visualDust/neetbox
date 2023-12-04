# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

import inspect
import types
from importlib.metadata import version
from typing import Union
from uuid import uuid4

from neetbox.core import Registry
from neetbox.utils.framing import get_frame_module_traceback

NEETBOX_VERSION = version("neetbox")

_DEFAULT_WORKSPACE_CONFIG = {
    "name": None,
    "version": NEETBOX_VERSION,
    "workspace-id": None,
    "logging": {"level": "INFO", "logdir": None},
    "pipeline": {
        "updateInterval": 0.5,
    },
    "extension": {
        "autoload": True,
    },
    "daemon": {
        "enable": True,
        "host": "127.0.0.1",
        "port": 20202,
        "allowIpython": False,
        "mute": True,
        "mode": "detached",
        "uploadInterval": 0.5,
    },
}


def _obtain_new_run_id():
    """put a new run id into config. do not run before workspace loaded as a project.

    Returns:
        str: new run id
    """
    global _DEFAULT_WORKSPACE_CONFIG
    _DEFAULT_WORKSPACE_CONFIG["run-id"] = str(uuid4())
    return _DEFAULT_WORKSPACE_CONFIG["run-id"]


def _update_dict_recursively(self: dict, the_other: dict):
    for _k, _v in the_other.items():
        if type(_v) is dict:  # currently resolving a dict child
            if _k in self:  # dfs merge
                _update_dict_recursively(self=self[_k], the_other=the_other[_k])
            else:
                self[_k] = the_other[_k]
        else:  # not a dict, overwriting
            self[_k] = the_other[_k]


WORKSPACE_CONFIG: dict = _DEFAULT_WORKSPACE_CONFIG.copy()

_QUERY_ADD_EXTENSION_DEFAULT_CONFIG = Registry("__QUERY_ADD_EXTENSION_DEFAULT_CONFIG")
export_default_config = _QUERY_ADD_EXTENSION_DEFAULT_CONFIG.register


def _build_global_config_dict_for_module(module, local_config):
    """build a global config from a local config of a module. for example:
    - local config in neetbox/moduleA/some.py: { { "a" : 1 } }
    - the returned global config: {
        moduleA: {
            some: {
                "a" : 1
            }
        }
    }

    Args:
        module (_type_): _description_
        local_config (_type_): _description_
    """

    def _form_global_config_dict_from_module_name_list(
        pass_in_a_empty_dict_to_operate, module_name_list, local_config
    ):
        """turn a local config to a global config.
        Args:
            pass_in_a_empty_dict_to_operate (dict): pass in a empty dict, this function directly write into the dict, no value is returned.
            module_name_list (list): list of splited module names, for example, should be ["neetbox", "moduleA", "some"] for module neetbox.moduleA.some.
            local_config (dict): the local config of the sub module
        """
        for module_name in module_name_list:
            pass_in_a_empty_dict_to_operate[module_name] = {}
            pass_in_a_empty_dict_to_operate = pass_in_a_empty_dict_to_operate[module_name]
        for _k, _v in local_config.items():
            pass_in_a_empty_dict_to_operate[_k] = _v

    try:
        config = {}
        module_names = module.__name__.split(".")
        if module_names[0] == "neetbox":
            module_names.pop(0)
        _form_global_config_dict_from_module_name_list(config, module_names, local_config)
        return config
    except Exception as e:
        raise e


def _update_default_config_from_config_register():
    """iterate through config register to read their default config and write the result into global config. DO NOT run after workspace loaded.

    Raises:
        e: any possible exception
    """
    global _DEFAULT_WORKSPACE_CONFIG
    for _, fun in _QUERY_ADD_EXTENSION_DEFAULT_CONFIG.items():
        try:
            local_config = fun()
            parsed_local_config = _build_global_config_dict_for_module(
                inspect.getmodule(fun), local_config
            )
            _update_dict_recursively(_DEFAULT_WORKSPACE_CONFIG, parsed_local_config)
        except Exception as e:
            raise e


def _update_default_workspace_config_with(cfg: dict):
    global _DEFAULT_WORKSPACE_CONFIG
    _update_dict_recursively(_DEFAULT_WORKSPACE_CONFIG, cfg)
    return _DEFAULT_WORKSPACE_CONFIG


def get_current():
    global _DEFAULT_WORKSPACE_CONFIG
    return _DEFAULT_WORKSPACE_CONFIG


def get_module_level_config(module: Union[str, types.ModuleType] = None):
    """get a module level config from global config

    Args:
        module (str or module, optional): which module's config to get. Defaults to None(which means neetbox will automatically find the module in which this function is called). if you want to get all the global config, pass "@" for module.

    Returns:
        dict: the config you want.
    """
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

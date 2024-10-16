# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231203

import os
from uuid import uuid4

import toml

from neetbox._protocol import MACHINE_ID_KEY
from neetbox.utils.localstorage import (
    get_create_neetbox_config_directory,
    get_create_neetbox_data_directory,
)
from neetbox.utils.massive import check_read_toml

_GLOBAL_CONFIG = {
    MACHINE_ID_KEY: str(uuid4()),
    "vault": get_create_neetbox_data_directory(),
    "bypass-db-version-check": False,
}

_GLOBAL_CONFIG_FILE_NAME = f"neetbox.global.toml"


def update_dict_recursively_on_missing_keys(A, B):
    """
    Update dictionary B with keys from dictionary A. Add missing keys from A to B,
    but do not overwrite existing keys in B. Handles nested dictionaries recursively.
    """
    missed_keys = []
    for key, value in A.items():
        if key not in B:
            missed_keys.append(key)
            B[key] = value
        else:
            if isinstance(value, dict) and isinstance(B[key], dict):
                missed_keys += update_dict_recursively_on_missing_keys(value, B[key])
            else:
                # Do not modify B[key] if it already exists
                pass
    return missed_keys


def overwrite_create_local(config: dict):
    neetbox_config_dir = get_create_neetbox_config_directory()
    config_file_path = os.path.join(neetbox_config_dir, _GLOBAL_CONFIG_FILE_NAME)
    with open(config_file_path, "w+") as config_file:
        toml.dump(config, config_file)


def read_create_local():
    global _GLOBAL_CONFIG
    neetbox_config_dir = get_create_neetbox_config_directory()
    config_file_path = os.path.join(neetbox_config_dir, _GLOBAL_CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):  # config not exist, try to create
        overwrite_create_local(_GLOBAL_CONFIG)
    # read local file
    user_cfg = check_read_toml(config_file_path)
    assert user_cfg
    update_dict_recursively_on_missing_keys(_GLOBAL_CONFIG, user_cfg)
    _GLOBAL_CONFIG.update(user_cfg)
    overwrite_create_local(_GLOBAL_CONFIG)


def set(key, value):
    global _GLOBAL_CONFIG
    read_create_local()
    _GLOBAL_CONFIG[key] = value
    overwrite_create_local(_GLOBAL_CONFIG)


def get(key=None):
    read_create_local()
    if key is None:
        return _GLOBAL_CONFIG.copy()
    return _GLOBAL_CONFIG.get(key, None)

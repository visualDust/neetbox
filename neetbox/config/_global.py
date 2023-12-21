# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231203

import os
from importlib.metadata import version

import toml

CONFIG_FILE_NAME = f"cli.neetbox.toml"
NEETBOX_VERSION = version("neetbox")
from uuid import uuid4

from neetbox._protocol import ID_KEY
from neetbox.utils.massive import (
    check_read_toml,
    get_user_config_directory,
    update_dict_recursively,
)

_GLOBAL_CONFIG = {
    "version": NEETBOX_VERSION,
    "servers": [{"address": "localhost", "port": 20202}],
    ID_KEY: uuid4(),
}

CONFIG_FILE_NAME = f"neetbox.toml"


def overwrite_create_local(config: dict):
    user_config_dir = get_user_config_directory()
    assert user_config_dir is not None
    neetbox_config_dir = os.path.join(user_config_dir, "neetbox")
    config_file_path = os.path.join(neetbox_config_dir, CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):  # config not exist, try to create
        if not os.path.exists(neetbox_config_dir):  # config folder not exist
            os.mkdir(neetbox_config_dir)
        assert os.path.isdir(neetbox_config_dir)
    with open(config_file_path, "w+") as config_file:
        toml.dump(config, config_file)


def read_create_local():
    global _GLOBAL_CONFIG
    user_config_dir = get_user_config_directory()
    assert user_config_dir is not None
    neetbox_config_dir = os.path.join(user_config_dir, "neetbox")
    config_file_path = os.path.join(neetbox_config_dir, CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):  # config not exist, try to create
        overwrite_create_local(_GLOBAL_CONFIG)
    # read local file
    user_cfg = check_read_toml(config_file_path)
    assert user_cfg
    for k, v in user_cfg.items():
        _GLOBAL_CONFIG[k] = v


def set(key, value):
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG[key] = value
    overwrite_create_local(_GLOBAL_CONFIG)


def get(key):
    read_create_local()
    return _GLOBAL_CONFIG.get(key, None)

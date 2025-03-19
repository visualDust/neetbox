# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231224

import os
import pathlib
import sys

from vdtoys.localstorage import get_user_app_data_directory, get_user_config_directory


def get_create_neetbox_config_directory():
    path = os.path.join(get_user_config_directory(), "neetbox")
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(
        path
    ), f"Fialed to create neetbox config directory {path}, please check your permission or create it manually."
    return path


def get_create_neetbox_data_directory():
    path = os.path.join(get_user_app_data_directory(), "neetbox")
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(
        path
    ), f"Fialed to create neetbox data directory {path}, please check your permission or create it manually."
    return path

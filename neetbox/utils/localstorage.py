# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231224

import os
import pathlib
import sys


def get_user_config_directory():
    """Returns a platform-specific root directory for user config settings.
    On Windows, prefer %LOCALAPPDATA%, then %APPDATA%, since we can expect the AppData directories to be ACLed to be visible only to the user and admin users (https://stackoverflow.com/a/7617601/1179226). If neither is set, return None instead of falling back to something that may be world-readable.
    """
    if os.name == "nt":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            return appdata
        appdata = os.getenv("APPDATA")
        if appdata:
            return appdata
        return None
    # On non-windows, use XDG_CONFIG_HOME if set, else default to ~/.config.
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        return xdg_config_home
    return os.path.join(os.path.expanduser("~"), ".config")


def get_create_neetbox_config_directory():
    path = os.path.join(get_user_config_directory(), "neetbox")
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(
        path
    ), f"Fialed to create neetbox config directory {path}, please check your permission or create it manually."
    return path


def get_user_app_data_directory():
    """
    Returns a parent directory path
    where persistent application data can be stored.

    - linux: ~/.local/share
    - macOS: ~/Library/Application Support
    - windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        app_data_path = home / "AppData/Roaming"
    elif sys.platform == "linux":
        app_data_path = home / ".local/share"
    elif sys.platform == "darwin":
        app_data_path = home / "Library/Application Support"

    return str(app_data_path)


def get_create_neetbox_data_directory():
    path = os.path.join(get_user_app_data_directory(), "neetbox")
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(
        path
    ), f"Fialed to create neetbox data directory {path}, please check your permission or create it manually."
    return path


def get_file_size_in_bytes(file_path):
    return os.path.getsize(file_path)


def get_folder_size_in_bytes(folder_path, skip_symbolic_link=True):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.islink(fp) and skip_symbolic_link:
                continue  # Skip if it is symbolic link
            total_size += os.path.getsize(fp)
    return total_size

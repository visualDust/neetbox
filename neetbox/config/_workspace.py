import os
import uuid
from importlib.metadata import version

import toml

import neetbox.daemon as daemon
import neetbox.extension as extension  # DO NOT remove this import
from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

from ._config import (
    _obtain_new_run_id,
    _update_default_config_from_config_register,
    _update_default_workspace_config_with,
)
from ._config import get_current as get_current_config

_logger = logger("NEETBOX", style=LogStyle(with_datetime=False, skip_writers=["ws"]))

CONFIG_FILE_NAME = f"neetbox.toml"
NEETBOX_VERSION = version("neetbox")


def _init_workspace(path=None, **kwargs) -> bool:
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, CONFIG_FILE_NAME)
    if not os.path.isfile(config_file_path):  # config file not exist
        try:  # creating config file using default config
            with open(config_file_path, "w+") as config_file:
                extension._run_things_before_load_workspace()  # also run things before load workspace on init workspace
                _update_default_config_from_config_register()  # load custom config into default config
                _config = get_current_config()
                if "name" in kwargs and kwargs["name"]:  # using given name
                    _config["name"] = kwargs["name"]
                else:  # using the folder name
                    _config["name"] = os.path.basename(os.path.normpath(os.getcwd()))
                _config["projectid"] = str(uuid.uuid4())
                toml.dump(_config, config_file)
            _logger.ok(f"Workspace config created as {config_file_path}.")
            return True
        except Exception as e:
            _logger.err(f"Failed to create {config_file_path}: {e}")
            return False
    else:  # config file exist:
        _logger.err((f"Config file already exists."))  # noqa
        return False


def _load_workspace(path=None) -> bool:
    extension._run_things_before_load_workspace()  # also run things before load workspace on init workspace
    _update_default_config_from_config_register()  # load custom config into default config
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, CONFIG_FILE_NAME)
    if not os.path.isfile(config_file_path):  # but config file not exist
        _logger.err(f"Config file {config_file_path} not exists.")
        return False
    try:  # do load
        _config_loaded_from_file = toml.load(config_file_path)
        _update_default_workspace_config_with(_config_loaded_from_file)
        _logger.ok(f"workspace config loaded from {config_file_path}.")
        return True
    except Exception as e:
        _logger.err(f"failed to load workspace config from {config_file_path}: {e}")
        return False


def _load_workspace_as_a_project(connect_daemon=False):
    success_flag = _load_workspace()  # init from config file
    if not success_flag:  # failed to load workspace config, exiting
        os._exit(255)
    _obtain_new_run_id()  # obtain new run id
    extension._run_things_after_load_workspace()  # run things after init workspace
    if connect_daemon:
        daemon.connect()


def _is_in_workspace():
    return os.path.isfile(CONFIG_FILE_NAME)

import os
import sys

import toml

import neetbox.daemon as daemon
import neetbox.integrations as integrations
from neetbox.config import default as default_config
from neetbox.config._config import update_workspace_config_with
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger
from neetbox.utils.framing import get_frame_module_traceback

logger = Logger("NEETBOX", style=LogStyle(with_datetime=False, skip_writers=["ws"]))

MODULE_NAME = get_frame_module_traceback(1).__name__  # type: ignore
CONFIG_FILE_NAME = f"{MODULE_NAME}.toml"


def _init_workspace(path=None, **kwargs) -> bool:
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, CONFIG_FILE_NAME)
    if not os.path.isfile(config_file_path):  # config file not exist
        try:  # creating config file using default config
            with open(config_file_path, "w+") as config_file:
                _config = dict(default_config)
                if "name" in kwargs and kwargs["name"]:  # using given name
                    _config["name"] = kwargs["name"]
                else:  # using the folder name
                    _config["name"] = os.path.basename(os.path.normpath(os.getcwd()))
                toml.dump(_config, config_file)
            logger.ok(f"Workspace config created as {config_file_path}.")
            return True
        except Exception as e:
            logger.err(f"Failed to create {config_file_path}: {e}")
            return False
    else:  # config file exist:
        logger.err((f"Config file already exists."))  # noqa
        return False


def _load_workspace(path=None) -> bool:
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, CONFIG_FILE_NAME)
    if not os.path.isfile(config_file_path):  # but config file not exist
        logger.err(f"Config file {config_file_path} not exists.")
        return False
    try:  # do load
        load_config = toml.load(config_file_path)
        update_workspace_config_with(load_config)
        logger.ok(f"workspace config loaded from {config_file_path}.")
        return True
    except Exception as e:
        logger.err(f"failed to load workspace config from {config_file_path}: {e}")
        return False


is_in_daemon_process = (
    "NEETBOX_DAEMON_PROCESS" in os.environ and os.environ["NEETBOX_DAEMON_PROCESS"] == "1"
)


def _load_workspace_as_a_project():
    success = _load_workspace()  # init from config file
    if not success:  # failed to load workspace config, exiting
        os._exit(255)
    # post init
    integrations._post_init_workspace()
    daemon._try_attach_daemon()


def _is_in_workspace():
    return os.path.isfile(CONFIG_FILE_NAME)


if len(sys.argv) > 0 and sys.argv[0].endswith("neet") or is_in_daemon_process:
    # running in cli or daemon process, do not load workspace
    pass
elif _is_in_workspace():  # if a config file exist and not running in cli
    _load_workspace_as_a_project()

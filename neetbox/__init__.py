import os
import toml
from neetbox.config import default
from neetbox.logging.logger import Logger
from neetbox.config._config import _update
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback(1).__name__


def init(path=None):
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    # read config file

    logger = Logger(module_name)  # no output file
    config_file_name = f"{module_name}.toml"
    config_file_path = os.path.join(current_path, config_file_name)
    _fallback_flag = False
    if not os.path.isfile(config_file_path):  # config file not exists
        try:  # creating config file using default config
            with open(config_file_path, "w+") as cfgf:
                toml.dump(default, cfgf)
            logger.ok(f"Workspace config created as {config_file_path}.")
        except Exception as e:
            logger.err(f"Failed to create {config_file_path}: {e}")
            _fallback_flag = True

    # the config file now exists
    try:
        load_config = toml.load(config_file_path)
        logger.ok(f"Loaded workspace config from {config_file_path}.")
    except Exception as e:
        logger.err(f"Failed to load config from {config_file_path}: {e}")
        _fallback_flag = True

    if not _fallback_flag:  # put the config
        _update(load_config)
    else:  # something wrong, using default config
        raise RuntimeError(
            f"Failed to parse config file '{config_file_path}'. Check permissions and file format."
        )


config_file_name = f"{module_name}.toml"
if os.path.isfile(config_file_name): # if in a workspace
    init()

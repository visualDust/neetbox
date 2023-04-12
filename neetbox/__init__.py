import os
import toml
from neetbox.config import default
from neetbox.config._config import _update
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback(1).__name__
config_file_name = f"{module_name}.toml"


def init(path=None, load=False) -> bool:
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, config_file_name)

    if not load:
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        if not os.path.isfile(config_file_path):  # config file not exist
            try:  # creating config file using default config
                with open(config_file_path, "w+") as cfgf:
                    toml.dump(default, cfgf)
                logger.ok(f"Workspace config created as {config_file_path}.")
                return True
            except Exception as e:
                logger.err(f"Failed to create {config_file_path}: {e}")
                return False
        else:  # config file exist:
            logger.err((f"Config file already exists."))
            return False
    else:  # load only. trying to load from not existing file
        if not os.path.isfile(config_file_path):  # config file not exist
            from neetbox.logging.logger import Logger

            logger = Logger("NEETBOX")  # builtin standalone logger
            logger.err(f"Config file {config_file_path} not exists.")
            return False

    try:
        load_config = toml.load(config_file_path)
        _update(load_config)
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        logger.ok(f"Loaded workspace config from {config_file_path}.")
        return True
    except Exception as e:
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        logger.err(f"Failed to load config from {config_file_path}: {e}")
        return False


if os.path.isfile(config_file_name):  # if in a workspace
    init(load=True)

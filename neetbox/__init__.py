import os
import toml
from neetbox.config import default
from neetbox.logging.logger import Logger
from neetbox.config._config import _update
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback(1).__name__
config_file_name = f"{module_name}.toml"
logger = Logger("NEETBOX")  # builtin standalone logger

def init(path=None, load_only=False):
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, config_file_name)
    _fallback_flag = False
    
    if not load_only:
        if not os.path.isfile(config_file_path):  # config file not exist
            try:  # creating config file using default config
                with open(config_file_path, "w+") as cfgf:
                    toml.dump(default, cfgf)
                logger.ok(f"Workspace config created as {config_file_path}.")
            except Exception as e:
                logger.err(f"Failed to create {config_file_path}: {e}")
                _fallback_flag = True
        else: # config file exist:
            logger.err(f"Config file already exists.")
            raise RuntimeError(f"Config file already exists.")
    else: # load only. trying to load from not existing file
        if not os.path.isfile(config_file_path):  # config file not exist
            logger.err(f"Config file {config_file_path} not exists.")
            _fallback_flag = True

    if not _fallback_flag:  # if file exist
        try:
            load_config = toml.load(config_file_path)
            _update(load_config)
            logger.ok(f"Loaded workspace config from {config_file_path}.")
        except Exception as e:
            logger.err(f"Failed to load config from {config_file_path}: {e}")
            _fallback_flag = True

    if _fallback_flag:  # something wrong, using default config
        raise RuntimeError(
            f"Failed to parse config file '{config_file_path}'. Check permissions and file format."
        )

if os.path.isfile(config_file_name):  # if in a workspace
    init(load_only=True)

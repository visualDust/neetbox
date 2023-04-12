import os
import toml
from neetbox.config import default
from neetbox.config._config import _update
from neetbox.utils.framing import get_frame_module_traceback


def init(path=None):
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    # read config file
    module_name = get_frame_module_traceback(1).__name__
    config_file_name = f"{module_name}.toml"
    config_file_path = config_file_name

    _fallback_flag = False
    if not os.path.isfile(config_file_path):  # config file not exists
        try:  # creating config file using default config
            with open(config_file_path, "w+") as cfgf:
                toml.dump(default, cfgf)
        except:
            _fallback_flag = True

    # the config file now exists
    try:
        load_config = toml.load(config_file_path)
    except:
        _fallback_flag = True

    if not _fallback_flag:  # put the config
        _update(load_config)
    else:  # something wrong, using default config
        raise RuntimeError(
            f"Failed to parse config file '{config_file_path}'. Check permissions and file format."
        )
